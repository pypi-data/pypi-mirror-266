# cython: profile=False

import contextlib
import logging
import weakref
import numpy as np
cimport numpy as np

from libc.stdlib cimport free, malloc, calloc

cimport cython

from finesse import BeamParam
from finesse.env import warn
from finesse.cmatrix cimport SubCCSView1DArray, SubCCSView2DArray
from finesse.detectors.general import NoiseDetector
from finesse.components.general import NoiseType
from finesse.components.readout import _Readout
from finesse.components.node import NodeType
from finesse.frequency cimport Frequency, frequency_info_t, FrequencyContainer
from finesse.components.workspace cimport ConnectionSetting
from finesse.cymath cimport complex_t
from finesse.cymath.math cimport float_eq
from finesse.cymath.complex cimport conj, COMPLEX_0
from finesse.cymath.gaussbeam cimport beam_param, transform_q, inv_transform_q
from finesse.detectors.workspace import DetectorWorkspace
from finesse.symbols import Constant
from finesse.exceptions import BeamTraceException
from finesse.components.workspace cimport ConnectorWorkspace, ConnectorMatrixSimulationInfo
from finesse.components.modal.workspace cimport KnmConnectorWorkspace
from finesse.components.workspace cimport ConnectorCallbacks, fill_list_t
from finesse.components.modal.cavity cimport CavityWorkspace
from finesse.warnings import CavityUnstableWarning
from finesse.utilities.cyomp cimport determine_nthreads_even
from finesse.parameter cimport Parameter

LOGGER = logging.getLogger(__name__)


cdef class MatrixSystemSolver:
    """A linear set of systems can be represented as a matrix, each equation
    in this system is a particular state which we want to compute. The system
    is solved by applying some inputs into various states, or the right hand
    side (RHS) vector, and solving the system.

    The underlying matrix can be either a sparse or dense matrix. This class
    should not assume either, but merely call upon a standard matrix interface.
    Therefore the algorithm used for solving can varying significantly.
    The overall matrix is sectioned into submatricies which connect various
    states together.

    Nodes represent a physical location in the model in which some state of
    the system must be computed. Some nodes can have multiple states, such
    as multiple optical modes.
    """

    def __init__(self,
                matrix_type,
                str name,
                list nodes,
                FrequencyContainer optical_frequencies,
                dict signal_frequencies,
                int num_optical_homs,
                bint is_signal_matrix,
                bint forced_refill,
                dict node_map
    ):
        if is_signal_matrix:
            if signal_frequencies is None:
                raise Exception("Signal frequency containers not provided")
        else:
            if signal_frequencies is not None:
                raise Exception("Signal frequency container incorrectly provided for carrier simulation")
        assert(num_optical_homs >= 1)

        self.is_signal_matrix = is_signal_matrix
        self.manual_rhs = False
        self.workspaces = MatrixSystemWorkspaces()
        self.forced_refill = forced_refill
        self._M = matrix_type(name)
        self.out_view = None
        self.nhoms = num_optical_homs
        self.optical_frequencies = optical_frequencies
        self.signal_frequencies = signal_frequencies

        if is_signal_matrix:
            # Get the unique FrequencyContainer objects for filling the info of.
            # This could be more optimal and dive into the references and check if
            # frequency containers are actually unique, but this mostly just stops
            # there being 100s of fsig containers from each node
            # TODO - optimise this away from a tuple
            self.unique_elec_mech_fcnts = tuple(set(signal_frequencies.values()))
            self.noise_sources = dict()
            self._noise_matrices = dict()

        self.any_frequencies_changing = False
        # Global flag for if any frequency is changing
        for _f in self.optical_frequencies.frequencies:
            if _f.symbol.is_changing:
                self.any_frequencies_changing = True
                break

        self.setup_nodes(nodes, node_map)

    def __dealloc__(self):
        if self._c_node_info != NULL:
            free(self._c_node_info)

    cdef get_node_matrix_params(self, node, Py_ssize_t *Ns, Py_ssize_t *Nf, frequency_info_t** fptr) noexcept:
        """For a given node in the simulation this should set the provided pointers
        regarding the number of states and submatricies that are required in the matrix:
            - Ns : Number of unique states at the node per frequency
            - Nf : Number of frequencies at the node
            - fptr : Pointer to frequency_info_t for details on the number of frequencies
        """
        assert(Ns)
        assert(Nf)
        assert(fptr)

        cdef FrequencyContainer ficnt

        if node.type is NodeType.OPTICAL:
            Ns[0] = self.nhoms
            Nf[0] = self.optical_frequencies.size
            fptr[0] = &self.optical_frequencies.frequency_info[0]
        elif node.type is NodeType.MECHANICAL:
            # Higher order mechanical modes at a particular frequency. This should probably
            # be kept as 1 mode per frequency, additional mechanical degrees of freedom should
            # be defined as a separate node in a port.
            ficnt = <FrequencyContainer>(self.signal_frequencies[node])
            Ns[0] = 1
            Nf[0] = ficnt.size
            fptr[0] = &(ficnt.frequency_info[0])
        elif node.type is NodeType.ELECTRICAL:
            ficnt = <FrequencyContainer>(self.signal_frequencies[node])
            Ns[0] = 1 # no higher order modes of electronics as far as I'm aware...
            Nf[0] = ficnt.size
            fptr[0] = &(ficnt.frequency_info[0])
        else:
            raise Exception("Node type not handled")

    cdef tuple get_node_frequencies(self, node) noexcept:
        if node.type == NodeType.OPTICAL:
            return self.optical_frequencies.frequencies
        elif node.type == NodeType.MECHANICAL:
            return self.signal_frequencies[node].frequencies
        elif node.type == NodeType.ELECTRICAL:
            return self.signal_frequencies[node].frequencies
        else:
            raise ValueError()

    cpdef setup_nodes(self, list all_nodes, dict node_map) noexcept:
        cdef:
            Py_ssize_t i, s_rhs_idx, s_f_idx, Nsm, Neq
            NodeInfoEntry *info
            frequency_info_t *finfo_ptr = NULL

        self.nodes = {n.full_name : n for n in all_nodes}
        self.num_nodes = len(self.nodes)
        self.node_map = {a.full_name: b.full_name for a, b, in node_map.items()}

        self._c_node_info = <NodeInfoEntry*> calloc(self.num_nodes, sizeof(NodeInfoEntry))
        if not self._c_node_info:
            raise MemoryError()

        self.nhoms
        s_rhs_idx = 0 # total number of states in the matrix so far
        s_f_idx = 0 # Number of frequency submatrices so far
        i = 0
        self.nodes_idx = {}

        for n in self.nodes.values():
            if n in node_map:
                continue
            self.get_node_matrix_params(n, &Neq, &Nsm, &finfo_ptr)
            info = &self._c_node_info[i]

            info.index = self.nodes_idx[n.full_name] = i
            i += 1

            info.rhs_index = s_rhs_idx
            info.freq_index = s_f_idx
            info.nfreqs = Nsm
            info.nhoms = Neq
            info.frequencies = finfo_ptr

            s_rhs_idx += Neq * Nsm  # Track how many equations we are going through
            s_f_idx   += Nsm        # keep track of how many frequencies*nodes

        for n, a in node_map.items():
            self.nodes_idx[n.full_name] = self.nodes_idx[a.full_name]

    @contextlib.contextmanager
    def component_edge_fill(self, comp, edgestr, f1, f2, conjugate = False):
        """
        Returns a matrix for the submatrix an element has requested
        for different connections it needs. The key is::

            (element, connection_name, ifreq, ofreq)

        This is a context manager, to be used like with sim.component_edge_fill(key) as mat::

            mat[:] = computations

        Parameters
        ----------
        element : finesse.component.Connector
            The object reference that created the requests.
        connection_name : str
            String name given to the connection.
        ifreq : finesse.Frequency
            Incoming frequency.
        ofreq : finesse.Frequency
            Outgoing frequency.

        Returns
        -------
        matrix
        """
        #the two-stage nature of this will make some fill checks and hooks
        #much more safe (and powerfull)

        #this will be helpful for on-demand filling and will also help improve
        #make DC simulation of squeezers work (because post-fill transformations
        #will be needed)
        key = (comp, edgestr, f1.index, f2.index)
        mat = self._submatrices[key]
        yield mat
        #check things, or transform things here
        if conjugate:
            mat[:].imag *= -1
        return

    @contextlib.contextmanager
    def component_edge_fill3(self, owner_idx, conn_idx, f1_index, f2_index):
        if conn_idx < 0:
            raise IndexError(f"This connection was not included in the simulation. {owner_idx, conn_idx, f1_index, f2_index}")
        mat = self._submatrices[(owner_idx, conn_idx, f1_index, f2_index)]
        yield mat
        return

    cdef assign_submatrices(self, connector_workspaces) noexcept:
        """An important function. This takes all the connector workspaces - i.e. model elements
        that have requested some type of connection in the model - and ensures they have the
        correct submatrix allocated to them in for this solver.
        """
        cdef:
            NodeInfoEntry node_inf
            Frequency ifreq, ofreq
            bint couples_f, is_freq_gen
            ConnectorWorkspace ws

        if self._submatrices:
            raise Exception("Submatrices already assigned")

        self._submatrices  = {}
        self._diagonals = {}
        self.connections  = {}

        from finesse.components import FrequencyGenerator

        # Add in the diagonal elements of the matrix
        for n, node_info_idx in self.nodes_idx.items():
            if n in self.node_map:
                continue # node is being mapped so doesn't have any equations in matrix
            node_inf = self._c_node_info[node_info_idx]
            Nsm = node_inf.nfreqs
            Neq = node_inf.nhoms

            for freq in range(Nsm):
                fidx = self.findex(n, freq)  # Get index for this submatrix
                diagonal = self._M.declare_equations(
                    Neq, fidx, f"I,node={n},f={freq},fidx={fidx},Neq={Neq}"
                )
                self._diagonals[fidx] = diagonal

        id_owner = -1
        # for everything that needs to fill the matrix...
        for ws in connector_workspaces:
            owner = ws.owner
            id_owner += 1
            ws.owner_id = id_owner # store the owner index

            idx_connection = -1
            owner._registered_connections

            # For each connection this element wants...
            for name in owner._registered_connections:
                #print(name)
                idx_connection += 1

                if self.is_signal_matrix:
                    ws_conn = ws.signal.connections
                    conn_settings = ws.signal.connection_settings
                else:
                    ws_conn = ws.carrier.connections
                    conn_settings = ws.carrier.connection_settings
                # convert weak ref (input, output)
                nio = []
                for _ in owner._registered_connections[name]:
                    nio.append(owner.nodes[_])

                enabled_check = owner._enabled_checks.get(name, None)
                if enabled_check:
                    enabled_check = enabled_check()
                else:
                    enabled_check = True

                nio = tuple(nio)

                # If we are a carrier matrix only compute optics, no AC electronics or mechanics
                if not self.is_signal_matrix:
                    if (nio[0].type is not NodeType.OPTICAL
                        or nio[1].type is not NodeType.OPTICAL) or not enabled_check:
                        #print("excluded", name)
                        continue
                else:
                    # elec and mech nodes from a connection are not all necessarily modelled
                    # check if they are in the node list for this simulation
                    if (not (nio[0].full_name in self.nodes_idx and nio[1].full_name in self.nodes_idx)) or not enabled_check:
                        # If this connection hasn't been allocated then we set the
                        # matrix view array which is stored in the workspace connections info
                        # to None, so that fill methods can quickly check if they should
                        # touch it or not
                        idx_connection -= 1 # reduce connection idx count as we aren't allocating it now
                        if not hasattr(ws_conn, name):
                            setattr(ws_conn, name, None)
                        setattr(ws_conn, name + "_idx", -1)
                        continue

                dim = 0 # Dimension of the frequency coupling matrix
                # If we are not using a specialist connections object then
                # we need to add something to the generic Connections
                Nfi = self._c_node_info[self.node_id(nio[0])].nfreqs
                Nfo = self._c_node_info[self.node_id(nio[1])].nfreqs

                #print("!!!", owner, nio, Nfi, Nfo)
                ifreqs = self.get_node_frequencies(nio[0])
                ofreqs = self.get_node_frequencies(nio[1])
                #print("   in", nio[0], ifreqs, "\n   out", nio[1], ofreqs)

                # Frequency generators might couple fields, they might not.
                # so by default we set them to.
                is_freq_gen = isinstance(owner, FrequencyGenerator)
                # If the node type is different then we also are probably
                # coupling multiple frequencies together. For examaple,
                # Rad pressure, couples all sideband/carrier beats into
                # a single force state
                if hasattr(owner, "_couples_frequency"):
                    does_f_couple = owner._couples_frequency
                else:
                    does_f_couple = None

                couples_f = (
                    (
                        is_freq_gen
                        or (nio[0].type != nio[1].type)
                        or does_f_couple is not None
                    )
                    # Only if one of the nodes is optical do we have multiple
                    # frequencies to couple into
                    and (nio[0].type == NodeType.OPTICAL or nio[1].type == NodeType.OPTICAL)
                )
                #print(f"   is_freq_gen={is_freq_gen} couples_f={couples_f}")

                if not hasattr(ws_conn, name):
                    #print("NOT DEFINED", )
                    if couples_f:
                        # We will need a 2D array of submatrices to describe how multiple
                        # elements will couple together
                        setattr(ws_conn, name, np.empty((Nfi, Nfo) , dtype=object))
                        dim = 2
                    else:
                        # if not, just a diagonal
                        setattr(ws_conn, name, np.empty(Nfi, dtype=object))
                        dim = 1
                else:
                    #print("DEFINED", name, ws_conn)
                    # If a specialist object already exists lets probe it's shape
                    # as that will describe what can actually be coupled or not
                    dim = getattr(ws_conn, name).ndim

                # keep references for the matrices for each connection
                _conn = getattr(ws_conn, name)
                if not isinstance(_conn, (SubCCSView1DArray, SubCCSView2DArray, np.ndarray)):
                    raise ValueError(f"{ws_conn}.{name} should be a SubCCSView1DArray, SubCCSView2DArray, or np.ndarray not {type(_conn)}")
                self.connections[nio] = getattr(ws_conn, name)

                # Loop over all the frequencies we can couple between and add
                # submatrixes to the overall model
                for ifreq in ifreqs:
                    for ofreq in ofreqs:
                        #print("   &&& TRY ", ifreq, ofreq, does_f_couple)
                        # For each input and output frequency check if our
                        # element wants to couple them at this
                        if (
                            couples_f
                            and (does_f_couple is not None and not does_f_couple(ws, name, ifreq, ofreq))
                        ):
                            continue
                        elif not couples_f and ifreq.index != ofreq.index:
                            # If it doesn't couple frequencies and the
                            # frequencies are different then ignore
                            continue

                        #print("   &&& ACCEPT ", ifreq, ofreq)

                        iodx = []  # submatrix indices
                        tags = []  # descriptive naming tags for submatrix key
                        #key_name = re.sub(r"^[^.]*\.", "", name)
                        #key_name = re.sub(r">[^.]*\.", ">", key_name)
                        key = [id_owner, idx_connection]

                        # Get simulation unique indices for submatrix
                        # position. How we get these depends on the type of
                        # the nodes involved
                        for freq, node in zip((ifreq, ofreq), nio):
                            iodx.append(self.findex(node, freq.index))
                            tags.append(freq.name)
                            key.append(freq.index)

                        assert len(iodx) == 2
                        assert len(key) == 4

                        # Here we determined whether to conjugate fill a submatrix view or not
                        conjugate_fill = False
                        if self.is_signal_matrix:
                            if nio[0].type == nio[1].type == NodeType.OPTICAL:
                                # Opt-2-Opt lower sideband is conjugated
                                if ifreq.audio_order < 0 and ofreq.audio_order < 0:
                                    conjugate_fill = True
                            elif nio[0].type == NodeType.OPTICAL and ifreq.audio_order < 0:
                                # Opt-2-? lower sideband is conjugated
                                conjugate_fill = True
                            elif nio[1].type == NodeType.OPTICAL and ofreq.audio_order < 0:
                                # ?-2-Opt lower sideband is conjugated
                                conjugate_fill = True

                        if tuple(key) not in self._submatrices:
                            smname = "{}__{}__{}".format(name, *tags)

                            #print("Requesting:", key)

                            # Then we get a view of the underlying matrix which we set the values
                            # with. Store one for each frequency. By requesting this view we are
                            # telling the matrix that these elements should be non-zero in the
                            # model.
                            setting = conn_settings.get(name)
                            if setting is None:
                                # default to using full matrix if nothing set
                                setting = ConnectionSetting.MATRIX

                            if setting == ConnectionSetting.DIAGONAL:
                                #print("!!!D", owner, name, self.is_signal_matrix)
                                SM = self._M.declare_subdiagonal_view(*iodx, smname, conjugate_fill)
                            elif setting == ConnectionSetting.MATRIX:
                                #print("!!!M", owner, name, self.is_signal_matrix)
                                SM = self._M.declare_submatrix_view(*iodx, smname, conjugate_fill)
                            elif setting == ConnectionSetting.DISABLED:
                                #print("!!!DIS", owner, name, self.is_signal_matrix)
                                SM = None
                            else:
                                raise Exception(f"Unhandled setting {setting}")
                            #print("!@#", owner, name, self.is_signal_matrix, dim)
                            try:
                                if dim == 1:
                                    getattr(ws_conn, name)[ifreq.index] = SM
                                elif dim == 2:
                                    getattr(ws_conn, name)[ifreq.index, ofreq.index] = SM
                                else:
                                    raise Exception(f"Unhandled dimension size {dim}")
                            except IndexError:
                                raise IndexError(f"Error setting submatrix to connection {name} in {owner}. "
                                                  "Size of array of submatricies wrong, number of frequencies "
                                                  "assumed probably incorrect.")

                            setattr(ws_conn, name + "_idx", idx_connection)
                            self._submatrices[tuple(key)] = SM
                        else:
                            # Check if we've just requested the same submatrix.
                            SM = self._submatrices[tuple(key)]
                            if SM.from_idx != iodx[0] or SM.to_idx != iodx[1]:
                                raise Exception(
                                    "Requested submatrix has already been requested,"
                                    "but new one has different indices"
                                )
                            else:
                                continue
        #print("done")

    cdef assign_noise_submatrices(self, connector_workspaces) noexcept:
        import itertools
        cdef NodeInfoEntry node_inf
        cdef Frequency ifreq, ofreq
        cdef ConnectorWorkspace ws
        cdef int i

        self._noise_submatrices  = {}

        for noise_type, sources in self.noise_sources.items():
            M = self._noise_matrices[noise_type]
            self._noise_submatrices[noise_type] = {}

            # Add in the diagonal elements of the matrices
            for n, node_info_idx in self.nodes_idx.items():
                if n in self.node_map:
                    continue # node is being mapped so doesn't have any equations in matrix
                node_inf = self._c_node_info[node_info_idx]
                Nsm = node_inf.nfreqs
                Neq = node_inf.nhoms
                for freq in range(Nsm):
                    fidx = self.findex(n, freq)  # Get index for this submatrix
                    mat = M.declare_equations(
                        Neq, fidx, f"I,node={n},f={freq},fidx={fidx},Neq={Neq}"
                    )
                    self._noise_submatrices[noise_type][fidx] = mat

            for comp, nodes in sources:
                ws = None
                for _ws in self.workspaces.to_noise_refill:
                    if _ws.owner is comp:
                        ws = _ws
                        break
                if ws is None:
                        raise Exception("Noise source not registered")
                for name, node in nodes:
                    freqs = self.get_node_frequencies(node)

                    if hasattr(comp, "_couples_noise"):
                        couples_noise = comp._couples_noise
                    else:
                        couples_noise = None

                    # Loop over all the noise sidebands we can couple between and add
                    # submatrixes to the overall model
                    for ifreq, ofreq in itertools.product(freqs, freqs):
                        if couples_noise is None:
                            if ifreq.index != ofreq.index:
                                continue
                        elif not couples_noise(ws, node, noise_type, ifreq, ofreq):
                            continue

                        iodx = []  # submatrix indices
                        tags = []  # descriptive naming tags for submatrix key
                        key = [ws.owner_id, self.node_id(node)]

                        # Get simulation unique indices for submatrix position.
                        for freq in [ifreq, ofreq]:
                            iodx.append(self.findex(node, freq.index))
                            tags.append(freq.name)
                            key.append(freq.index)

                        assert len(iodx) == 2
                        assert len(key) == 4

                        # Here we determined whether to conjugate fill a submatrix view or not
                        conjugate_fill = False
                        if node.type == NodeType.OPTICAL:
                            # Opt-2-Opt lower sideband is conjugated
                            if ifreq.audio_order < 0 and ofreq.audio_order < 0:
                                conjugate_fill = True

                        if tuple(key) not in self._noise_submatrices[noise_type]:
                            smname = "{}__{}__{}".format(name, *tags)

                            if ifreq == ofreq:
                                SM = self._noise_submatrices[noise_type][self.findex(node, ifreq.index)]
                            else:
                                SM = M.declare_submatrix_view(*iodx, smname, conjugate_fill)
                            getattr(ws.signal.noise_sources, name)[ifreq.index, ofreq.index] = SM

                            self._noise_submatrices[noise_type][tuple(key)] = SM
                        else:
                            # Check if we've just requested the same submatrix.
                            sm = self._noise_submatrices[noise_type][tuple(key)]
                            if sm.from_idx != iodx[0] or sm.to_idx != iodx[1]:
                                raise Exception(
                                    "Requested submatrix has already been requested,"
                                    "but new one has different indices"
                                )
                            else:
                                continue

        if NoiseType.QUANTUM in self.noise_sources:
            M = self._noise_matrices[NoiseType.QUANTUM]
            for ws in connector_workspaces:
                for i in range(ws.input_noise.num_nodes):
                    n = ws.input_noise.node_info[i].idx
                    node_inf = self._c_node_info[n]
                    Nsm = node_inf.nfreqs
                    for freq in range(Nsm):
                        fidx = self.findex_fast(n, freq)  # Get index for this submatrix
                        ws.input_noise.nodes[i, freq] = self._noise_submatrices[NoiseType.QUANTUM][fidx]
                for i in range(ws.output_noise.num_nodes):
                    n = ws.output_noise.node_info[i].idx
                    node_inf = self._c_node_info[n]
                    Nsm = node_inf.nfreqs
                    for freq in range(Nsm):
                        fidx = self.findex_fast(n, freq)  # Get index for this submatrix
                        ws.output_noise.nodes[i, freq] = self._noise_submatrices[NoiseType.QUANTUM][fidx]

    cdef add_noise_matrix(self, object key) noexcept:
        raise NotImplementedError

    cdef add_rhs(self, unicode key) noexcept:
        raise NotImplementedError

    cdef update_frequency_info(self) noexcept:
        self.optical_frequencies.update_frequency_info()
        if self.is_signal_matrix:
            for i in range(len(self.unique_elec_mech_fcnts)):
                (<FrequencyContainer>self.unique_elec_mech_fcnts[i]).update_frequency_info()

    cdef factor(self) noexcept:
        raise NotImplementedError()

    cdef refactor(self) noexcept:
        raise NotImplementedError()

    cdef solve(self) noexcept:
        raise NotImplementedError()

    cdef solve_noises(self) noexcept:
        raise NotImplementedError()

    cdef initial_fill(self) noexcept:
        cdef Py_ssize_t i
        cdef ConnectorWorkspace ws
        cdef ConnectorMatrixSimulationInfo cmsinfo
        cdef fill_list_t *fill_list

        self.optical_frequencies.initialise_frequency_info()
        if self.is_signal_matrix:
            for i in range(len(self.unique_elec_mech_fcnts)):
                (<FrequencyContainer>self.unique_elec_mech_fcnts[i]).initialise_frequency_info()

        for ws in self.workspaces.to_initial_fill:
            ws.update_parameter_values()
            if self.is_signal_matrix:
                cmsinfo = ws.signal
            else:
                cmsinfo = ws.carrier
            fill_list = &cmsinfo.matrix_fills

            for i in range(fill_list.size):
                if fill_list.infos[i].fn_c:
                    fill_list.infos[i].fn_c(ws)
                elif fill_list.infos[i].fn_py:
                    (<object>fill_list.infos[i].fn_py).__call__(ws)

    cpdef refill(self) noexcept:
        cdef Py_ssize_t i, j
        cdef ConnectorWorkspace ws
        cdef fill_list_t *fill_list

        if self.any_frequencies_changing:
            self.update_frequency_info()

        for i in range(self.workspaces.num_to_refill):
            ws = <ConnectorWorkspace>self.workspaces.ptr_to_refill[i]
            # TODO (sjr) Probably don't need this update call for now
            #            (see start of self.run method)
            ws.update_parameter_values()
            if self.is_signal_matrix:
                fill_list = &ws.signal.matrix_fills
            else:
                fill_list = &ws.carrier.matrix_fills

            for j in range(fill_list.size):
                if fill_list.infos[j].refill or self.forced_refill:
                    if fill_list.infos[j].fn_c:
                        fill_list.infos[j].fn_c(ws)
                    elif fill_list.infos[j].fn_py:
                        (<object>fill_list.infos[j].fn_py).__call__(ws)

        # As we have changed the matrix elements we need to refactor
        self.refactor()

    cdef fill_rhs(self) noexcept:
        cdef ConnectorWorkspace ws
        cdef ConnectorMatrixSimulationInfo sys_ws
        for ws in self.workspaces.to_rhs_refill:
            ws.update_parameter_values()

            if self.is_signal_matrix:
                sys_ws = ws.signal
            else:
                sys_ws = ws.carrier

            if sys_ws.fn_rhs_c is not None:
                sys_ws.fn_rhs_c.func(ws)
            elif sys_ws.fn_rhs_py is not None:
                sys_ws.fn_rhs_py(ws)

    cdef fill_noise_inputs(self) noexcept:
        cdef ConnectorWorkspace ws
        for ws in self.workspaces.to_noise_input_refill:
            if NoiseType.QUANTUM in self.noise_sources:
                if ws.signal.fn_quantum_noise_input_c is not None:
                    ws.signal.fn_quantum_noise_input_c.func(ws)
                elif ws.signal.fn_quantum_noise_input_py is not None:
                    ws.signal.fn_quantum_noise_input_py(ws)

        for ws in self.workspaces.to_noise_refill:
            if NoiseType.QUANTUM in self.noise_sources:
                if ws.signal.fn_quantum_noise_c is not None:
                    ws.signal.fn_quantum_noise_c.func(ws)
                elif ws.signal.fn_quantum_noise_py is not None:
                    ws.signal.fn_quantum_noise_py(ws)

    cdef construct(self) noexcept:
        """This is called when workspaces and submatrices have been setup. Calling
        construct should now go and allocate the memory for the matrix and RHS.

        This method should be overwritten by an inheriting solver class with
        specfics of the solving technique.
        """
        raise NotImplementedError()

    cdef destruct(self) noexcept:
        """This is called when finishing and unbuilding the simulation.

        Classes that override this call should mindful of what this method is doing
        to and call it.
        """
        self._M = None
        self.workspaces.clear_workspaces()

    cdef initial_run(self) noexcept:
        """Once a solver has been constructed it will most likely need to be initially
        filled and ran. Some sparse solvers for example must do a full factor first, then
        can perform faster refactors.

        This method should be overwritten by an inheriting solver class with
        specfics of the solving technique.
        """
        raise NotImplementedError()

    cpdef run(self) noexcept:
        """Executes the simulation for model in its current state.

        Takes the following steps to compute an output:
         * If self.manual_rhs:
            * Clears the RHS vector
            * Fills the RHS vector
         * Fills the matrix
         * Solves
        """
        if not self.manual_rhs:
            self.clear_rhs()
            self.fill_rhs()
        self.refill()
        self.solve()

    @property
    def M(self):
        """
        A weak reference to the underlying Matrix object.

        .. note::

            References to the Matrix should not be kept.

        :getter: Returns a weak reference to the underlying matrix (read-only).
        """
        return weakref.ref(self._M)

    def print_matrix(self):
        self._M.print_matrix()

    cpdef clear_rhs(self) noexcept:
        self._M.clear_rhs()

    def set_source(self, object node, int freq_idx, int hom_idx, complex value):
        self._M.set_rhs(self.field_fast(self.node_id(node), freq_idx, hom_idx), value)

    cdef int set_source_fast(self, Py_ssize_t node_id, Py_ssize_t freq_idx, Py_ssize_t hom_idx, complex_t value, unsigned rhs_index=0) except -1:
        return self._M.c_set_rhs(self.field_fast(node_id, freq_idx, hom_idx), value, rhs_index)

    cdef int set_source_fast_2(self, Py_ssize_t rhs_idx, complex_t value) except -1:
        return self._M.c_set_rhs(rhs_idx, value, 0)

    cdef int set_source_fast_3(self, Py_ssize_t rhs_idx, complex_t value, unsigned rhs_index) except -1:
        return self._M.c_set_rhs(rhs_idx, value, rhs_index)

    cpdef Py_ssize_t findex(self, object node, Py_ssize_t freq) noexcept:
        """
        Returns simulation unique index for a given frequency at this node.
        Used to refer to submatrices of HOMs in the interferometer matrix.

        Parameters
        ----------
        node : :class:`.Node`
            Node object to get the index of.
        freq : int
            Frequency index.

        Returns
        -------
        index : int
            Index of the `node` for a given frequency.
        """
        return self.findex_fast(self.node_id(node), freq)

    cdef Py_ssize_t findex_fast(self, Py_ssize_t node_id, Py_ssize_t freq) noexcept nogil:
        cdef:
            NodeInfoEntry ni = self._c_node_info[node_id]
            Py_ssize_t freq_idx = ni.freq_index

        return freq_idx + freq

    cpdef Py_ssize_t field(self, object node, Py_ssize_t freq=0, Py_ssize_t hom=0) noexcept:
        """
        Returns simulation unique index of a field at a particular frequency
        index at this node.

        Parameters
        ----------
        node : :class:`.Node`
            Node object to get the index of.
        freq : int
            Frequency index.
        hom : int, optional
            Higher Order Mode index, defaults to zero.
        """
        return self.field_fast(self.node_id(node), freq, hom)

    cdef Py_ssize_t field_fast(self, Py_ssize_t node_id, Py_ssize_t freq=0, Py_ssize_t hom=0) noexcept nogil:
        cdef:
            NodeInfoEntry ni = self._c_node_info[node_id]
            Py_ssize_t Nh = ni.nhoms
            Py_ssize_t rhs_idx = ni.rhs_index
        return rhs_idx + freq * Nh + hom

    cdef inline Py_ssize_t field_fast_2(
        self,
        Py_ssize_t node_rhs_idx,
        Py_ssize_t num_hom,
        Py_ssize_t freq,
        Py_ssize_t hom) noexcept nogil:
        """Inlined function to return field index fast."""
        return node_rhs_idx + freq * num_hom + hom

    cpdef complex_t get_out(self, object node, Py_ssize_t freq=0, Py_ssize_t hom=0) noexcept:
        return self.get_out_fast(self.node_id(node), freq, hom)

    @cython.boundscheck(False)
    @cython.wraparound(False)
    @cython.initializedcheck(False)
    cdef complex_t get_out_fast(self, Py_ssize_t node_id, Py_ssize_t freq=0, Py_ssize_t hom=0) noexcept nogil:
        cdef Py_ssize_t field_idx = self.field_fast(node_id, freq, hom)

        if self.out_view is None:
            return COMPLEX_0

        return self.out_view[field_idx]

    cpdef Py_ssize_t node_id(self, object node) noexcept:
        if type(node) is str:
            return self.nodes_idx[node]
        else:
            return self.nodes_idx[node.full_name]

    cpdef get_node_info(self, node) noexcept:
        """For a given node (object or name) the key parameters
        for where this node is represented in the matrix of linear
        equations is returned in a NodeInfoEntry object.
        """
        cdef int i
        if type(node) is str:
            i = self.nodes_idx[node]
        else:
            i = self.nodes_idx[node.full_name]

        cdef NodeInfoEntry ni = self._c_node_info[i]
        return {
            "index": ni.index,
            "rhs_index": ni.rhs_index,
            "freq_index": ni.freq_index,
            "nfreqs": ni.nfreqs,
            "nhoms": ni.nhoms,
        }

    def get_frequency_object(self, frequency, node):
        """Get a :class:`.Frequency` object corresponding to a numerical or symbolic value.
        Returns none if nothing has been found.

        Parameters
        ----------
        f : number or :class:`.Symbol`
            Frequency to search for in this simulation.

        Returns
        -------
        :class:`.Frequency`
            The frequency object.
        """
        from finesse.symbols import Symbol

        if node.type == NodeType.OPTICAL:
            frequencies = self.optical_frequencies.frequencies
        elif node.type == NodeType.MECHANICAL:
            if not self.is_signal_matrix:
                return None
            frequencies = self.signal_frequencies[node].frequencies
        elif node.type == NodeType.ELECTRICAL:
            if not self.is_signal_matrix:
                return None
            frequencies = self.signal_frequencies[node].frequencies

        if isinstance(frequency, Symbol):
            if frequency.is_changing:
                # if it's tunable we want to look for the symbol that is just this
                # lasers frequency, as it will be changing
                for f in frequencies:
                    if f.symbol == frequency:
                        return f

        f_value = float(frequency)
        # otherwise do some value comparisons
        for f in frequencies:
            if np.isclose(float(f.f), f_value, atol=1e-15, rtol=1e-15):
                return f

        return None


cdef class CarrierSignalMatrixSimulation:
    """A matrix based simulation which models the DC build of optical
    fields (carriers) and optionally a signal simulation, which models
    small AC oscillations throughout the system around the DC operating
    point.

    This simualations class contains two solvers, one for the carrier
    optical fields, and another for the signal simulations consisting of
    optical, electrical, and mechanical.
    """
    def __init__(self, model, unicode name, bint needs_matrix=True):
        self.model = model
        self.name = name
        self.initial_trace_sol = None
        self.trace = NULL
        self.changing_mismatch_couplings = ()
        self.contingent_trace_forests = {}
        self.needs_reflag_changing_q = False
        self.do_matrix_solving = needs_matrix

    def __dealloc__(self):
        if self.trace:
            free(self.trace)

    def build(self):
        from finesse.simulations.KLU import KLUMatrixSystemSolver

        if self.model.fsig.f.is_changing and self.model.fsig.f.value is None:
            warn(
                "Signal frequency (fsig) was set to None but simulation needs it. "
                "Setting default value of 1 Hz"
            )
            self.model.fsig.f.value = 1

        # Keep a list of all the things changing in the simulation
        self.changing_parameters = set(
            p for el in self.model.elements.values() for p in el.parameters if p.is_changing
        )
        self.tunable_parameters = set(
            p for p in self.changing_parameters if p.is_tunable
        )
        self.compute_signals = self.model.fsig.f.value is not None
        self.is_modal = self.model.is_modal
        self.initialise_model_settings()
        self.initialise_sim_config_data()

        # First we sort out the two matrix simulations as required by the model
        cf = self.generate_carrier_frequencies()
        onodes = self.model.optical_nodes

        if self.do_matrix_solving:
            self.carrier = KLUMatrixSystemSolver("carrier", onodes, cf, None, self.model_settings.num_HOMs, False, self.model.force_refill, {})

            if self.compute_signals:
                nodes = onodes.copy()
                nodes.extend(self.model.get_active_signal_nodes())
                osf, sf, = self.generate_signal_frequencies(nodes, cf)
                self.signal = KLUMatrixSystemSolver("signal", nodes, osf, sf, self.model_settings.num_HOMs, True, self.model.force_refill, {})
                self.initialise_noise_matrices()

        self.initialise_trace_forest(onodes)
        self.initialise_workspaces()
        self.update_all_parameter_values()

        if self.do_matrix_solving and self.compute_signals:
            self.initialise_noise_sources()
            self.initialise_noise_selection_vectors()

        if self.is_modal:
            # compute all the initial:
            #     - scattering matrices
            #     - space Gouy phases
            #     - laser tem Gouy phases
            if self.do_matrix_solving:
                for ws in self.workspaces:
                    # if the connector scatters modes then initialise the
                    # knm workspaces here and store the connector workspace
                    # in to_scatter_matrix_compute for future use
                    if isinstance(ws, (KnmConnectorWorkspace)):
                        (<KnmConnectorWorkspace> ws).initialise_knm_workspaces()
                        self.to_scatter_matrix_compute.append(ws)
                self.compute_knm_matrices()
            self.set_gouy_phases()
            # ... then determine which beam parameters will be changing
            # so that only the items from above which change get
            # re-computed on subsequent calls to their respective functions
            self._determine_changing_beam_params()

        if self.do_matrix_solving:
            self.carrier.assign_submatrices(self.workspaces)
            self.carrier.construct()
            self.carrier.initial_run()

            if self.signal:
                self.signal.assign_submatrices(self.workspaces)
                self.signal.assign_noise_submatrices(self.workspaces)
                self.signal.construct()
                self.signal.initial_run()

        self.setup_output_workspaces()

    def unbuild(self):
        if self.carrier is not None:
            self.carrier.destruct()
        if self.signal is not None:
            self.signal.destruct()

        for p in self.changing_parameters:
            # Reset all changing parameters so their type can change again
            (<Parameter>p).__disable_state_type_change = False

        # self._unbuild()
        # self._clear_workspace()

        # Code below can be used in debug mode to determine if anyone is keeping any
        # references to this matrix object, meaning its memory can't be freed.
        # This takes ~20ms to do so makes a difference for quick models. Maybe we need
        # a debug mode

        #_ref = self._M
        #self._M = None

        # refs = gc.get_referrers(_ref)
        # Nref = len(refs)
        # if Nref > 0:
        #     warn(
        #         f"Something other than the Simulation object (N={Nref}) is keeping"
        #         f" a reference to the matrix object {repr(self._M)}."
        #         " Could lead to excessive memory usage if not released."
        #     )
        #     for _ in refs:
        #         warn(f" - {repr(_)}")
        #del _ref


    cdef void update_cavities(self) noexcept:
        cdef CavityWorkspace ws
        for ws in self.cavity_workspaces.values():
            ws.update()

    cpdef void compute_knm_matrices(self) noexcept:
        cdef KnmConnectorWorkspace ws
        for ws in self.to_scatter_matrix_compute:
            ws.update_changing_knm_workspaces()
            ws.compute_scattering_matrices()
            # TODO (sjr) Probably want a flag to check if quantum noise calcs
            #            being performed and to only do this call if so
            ws.compute_knm_losses()

    cpdef update_map_data(self) noexcept:
        """This will cycle through each map being used and if
        it is defined by a function it will be evaluated again.
        """
        cdef KnmConnectorWorkspace ws
        # This could be made more efficient by just storing the
        # a list of those with changing maps
        for ws in self.to_scatter_matrix_compute:
            ws.update_map_data()

    cdef int set_gouy_phases(self) except -1:
        cdef ConnectorWorkspace ws
        cdef int rtn

        for ws in self.gouy_phase_workspaces:
            if ws.fn_gouy_c is not None:
                rtn = ws.fn_gouy_c.func(ws)
            elif ws.fn_gouy_py is not None:
                rtn = ws.fn_gouy_py(ws)
            if rtn:
                return rtn

        return 0

    cpdef modal_update(self) noexcept:
        """Updates HOM related dependencies / properties of the model.

        These updates are as follows:

         * Execute a beam trace on the changing trace trees
         * Computes the changing scattering matrices
         * Calculates the Gouy phase of Spaces and Laser power coefficients

        Returns
        -------
        validity : bool
            True if the modal update was successful, or False if an unstable
            cavity combination prevented a beam trace from being performed.
        """
        # Evaluate changing properties of cavity workspaces
        self.update_cavities()

        if self.retrace:
            if not self.trace_beam():
                return False

        # Compute the changing scattering matrices
        if self.do_matrix_solving:
            self.compute_knm_matrices()

        # Update the changing Gouy phases at spaces
        # and TEM Gouy phases at lasers
        self.set_gouy_phases()

        return True

    cdef _determine_changing_beam_params(
        self, TraceForest forest=None, bint set_tree_node_ids=True,
    ) noexcept:
        cdef:
            Py_ssize_t i
            Py_ssize_t num_nodes = self.carrier.num_nodes
            KnmConnectorWorkspace kws

        # Re-set all beam parameter changing flags to false initially
        for i in range(num_nodes):
            self.trace[i].is_fixed = True

        if self.retrace:
            LOGGER.info("Flagging changing beam parameters.")
            # Prepare the forest for simulation by setting all the node_id attributes
            # and flag the corresponding self.trace entries as changing
            self._setup_trace_forest(forest, set_tree_node_ids)

        # Now tell each knm workspace whether it is changing or not
        # so that only changing scattering matrices get recomputed
        # from here on
        for kws in self.to_scatter_matrix_compute:
            kws.flag_changing_knm_workspaces(self.changing_mismatch_edges)

    def is_component_in_mismatch_couplings(self, comp):
        """Determines whether the connector `comp` is associated with any
        of the node couplings in the stored changing mismatch couplings.

        .. note::

            This method can be replaced if connectors eventually use more
            granular refill flags --- i.e. per coupling refill flags. Then
            the check for refilling that coupling can simply include the
            condition ``(from_node, to_node) in sim.changing_mismatch_couplings``.
        """
        return any(node.component is comp for node, _ in self.changing_mismatch_couplings)

    cdef void _setup_trace_forest(self, TraceForest forest=None, bint set_tree_node_ids=True) noexcept:
        cdef:
            Py_ssize_t tree_idx
            TraceTree tree

        if forest is None:
            forest = self.trace_forest

        for tree_idx in range(forest.size()):
            tree = forest.forest[tree_idx]
            self._setup_single_trace_tree(tree, set_tree_node_ids)

    cdef void _setup_single_trace_tree(self, TraceTree tree, bint set_tree_node_ids=True) noexcept:
        cdef:
            TraceTree ltree = tree.left
            TraceTree rtree = tree.right

        # Only ever need to do this once, so avoid repeating when reflagging
        # changing beam params after exiting unstable cavity regions
        if set_tree_node_ids:
            tree.node_id = self.carrier.node_id(tree.node)
            tree.opp_node_id = self.carrier.node_id(tree.node.opposite)

        self.trace[tree.node_id].is_fixed = False
        self.trace[tree.opp_node_id].is_fixed = False

        if ltree is not None:
            self._setup_single_trace_tree(ltree)
        if rtree is not None:
            self._setup_single_trace_tree(rtree)

    cdef tuple _find_new_unstable_cavities(self) noexcept:
        cdef:
            Py_ssize_t tree_idx
            TraceTree tree

            CavityWorkspace cav_ws
            bint source_is_cav
            double gx, gy

            list ch_unstable_cavities = []

        for tree_idx in range(self.trace_forest.size()):
            tree = self.trace_forest.forest[tree_idx]

            if tree.is_source:
                cav_ws = self.cavity_workspaces.get(tree.dependency)
                source_is_cav = cav_ws is not None
                if source_is_cav: # Tree is an internal cavity tree
                    # The geometrically changing cavity has become unstable
                    # so inform that this is the case
                    if not cav_ws.is_stable:
                        ch_unstable_cavities.append(cav_ws.owner)

                        gx = cav_ws.gx
                        gy = cav_ws.gy
                        if float_eq(gx, gy):
                            warn(
                                f"Cavity {repr(tree.dependency.name)} is unstable with "
                                f"g = {gx}",
                                CavityUnstableWarning
                            )
                        else:
                            warn(
                                f"Cavity {repr(tree.dependency.name)} is unstable with "
                                f"gx = {gx}, gy = {gy}",
                                CavityUnstableWarning
                            )

        if not ch_unstable_cavities:
            return ()

        # Return tuple of the unstable cavities sorted by name so that
        # all permutations of the same combination of cavities give same
        # tuple --- important for look-ups in contingent_trace_forests dict
        return tuple(sorted(ch_unstable_cavities, key=lambda x: x.name))

    cdef TraceForest _initialise_contingent_forest(self, tuple unstable_cavities) noexcept:
        cdef TraceForest contingent_forest = TraceForest(self.model, self.trace_forest.symmetric)
        cdef TraceForest model_trace_forest = self.model.trace_forest
        cdef list order = model_trace_forest.dependencies.copy()
        for uc in unstable_cavities:
            order.remove(uc)

        # If there are no dependencies left after disabling the
        # unstable cavities then a beam trace cannot be performed
        # at this data point so no forest can be planted
        if not order:
            warn(
                "Cannot build a contingent trace forest as the simulation "
                "is in a regime with no stable cavities nor Gauss objects.",
                CavityUnstableWarning
            )
            return None

        contingent_forest.plant(order)

        self._determine_changing_beam_params(contingent_forest)

        return contingent_forest

    @cython.initializedcheck(False)
    cdef void _propagate_trace(self, TraceTree tree, bint symmetric) noexcept:
        cdef:
            TraceTree ltree = tree.left
            TraceTree rtree = tree.right

            const NodeBeamParam* q1 = &self.trace[tree.node_id]
            complex_t qx1 = q1.qx.q
            complex_t qy1 = q1.qy.q
            complex_t qx2, qy2

        if ltree is not None:
            # For non-symmetric traces we have some special checks
            # to do on trees which couldn't be reached from the
            # other dependency trees. Note these are only performed
            # on the left tree; see TraceForest._add_backwards_nonsymm_trees
            # for details.
            if symmetric or (not tree.do_nonsymm_reverse and not tree.do_inv_transform):
                qx2 = transform_q(tree.left_abcd_x, qx1, tree.nr, ltree.nr)
                qy2 = transform_q(tree.left_abcd_y, qy1, tree.nr, ltree.nr)
            elif tree.do_inv_transform:
                # Can't reach tree directly but there is a coupling from ltree.node
                # to tree.node so apply the inverse abcd law to get correct q
                qx2 = inv_transform_q(tree.left_abcd_x, qx1, tree.nr, ltree.nr)
                qy2 = inv_transform_q(tree.left_abcd_y, qy1, tree.nr, ltree.nr)
            else:
                # Really is no way to get to the node (no coupling from ltree.node to
                # tree.node) so only option now is to reverse q for ltree node entry
                qx2 = -conj(qx1)
                qy2 = -conj(qy1)

            self.trace[ltree.node_id].qx.q = qx2
            self.trace[ltree.node_id].qy.q = qy2
            if symmetric:
                self.trace[ltree.opp_node_id].qx.q = -conj(qx2)
                self.trace[ltree.opp_node_id].qy.q = -conj(qy2)

            self._propagate_trace(ltree, symmetric)

        if rtree is not None:
            qx2 = transform_q(tree.right_abcd_x, qx1, tree.nr, rtree.nr)
            qy2 = transform_q(tree.right_abcd_y, qy1, tree.nr, rtree.nr)

            self.trace[rtree.node_id].qx.q = qx2
            self.trace[rtree.node_id].qy.q = qy2
            if symmetric:
                self.trace[rtree.opp_node_id].qx.q = -conj(qx2)
                self.trace[rtree.opp_node_id].qy.q = -conj(qy2)

            self._propagate_trace(rtree, symmetric)

    cpdef trace_beam(self) noexcept:
        """Traces the beam through the paths which are dependent upon changing
        geometric parameter(s).

        This method will modify those entries in the ``self.trace`` C array
        which were previously determined to have changing beam parameter values.

        Returns
        -------
        validity : bool
            True if the tracing was successful, or False if an unstable
            cavity combination prevented a beam trace from being performed.

        Raises
        ------
        ex : :class:`.BeamTraceException`
            If the ``"unstable_handling"`` entry of the associated
            :attr:`.Model.sim_trace_config` dict is ``"abort"`` and
            any unstable cavities were encountered.
        """
        cdef:
            TraceTree tree
            Py_ssize_t tree_idx

            CavityWorkspace cav_ws
            bint source_is_cav

            complex_t qx_src, qy_src

            # The actual trace forest which gets traced. In most circumstances
            # this will be self.trace_forest but if changing cavities enter an
            # unstable regime then this will be temporarily swapped out for the
            # contingent forest for this data point (see below).
            TraceForest trace_forest

            # Objects necessary for dealing with newly unstable cavities
            tuple ch_unstable_cavities
            TraceForest contingent_forest

        # No changing beam parameters, do nothing
        if self.trace_forest.empty():
            return True

        # First we loop over the source trees and find any changing
        # cavities which have become unstable
        ch_unstable_cavities = self._find_new_unstable_cavities()

        # If we did find any newly unstable cavities then the current trace_forest
        # is invalidated at the current data point so we must build a new forest with
        # the unstable cavities disabled
        # NOTE (sjr) Don't worry about increased Python interaction in
        #            this block as this will rarely be executed anyway
        if ch_unstable_cavities:
            unstable_handling = self.model.sim_trace_config["unstable_handling"]

            # Abort simulation if tracing config set-up to do so when
            # encountering any unstable cavities
            if unstable_handling == "abort":
                raise BeamTraceException(
                    "Aborting simulation due to presence of unstable cavities: "
                    f"{', '.join([cav.name for cav in ch_unstable_cavities])}"
                )
            # Or if tracing config is set-up to abort only the retrace when
            # any unstable cavities encountered, flag this to notify that
            # appropriate detector outputs should be masked
            if unstable_handling == "mask":
                LOGGER.info(
                    "Aborting retrace as simulation tracing configuration is set-up "
                    "to mask at any data point(s) where unstable cavities occur."
                )
                return False

            LOGGER.info(
                "Attempting to use a contingent trace forest due "
                "to the presence of unstable cavities"
            )
            # Look-up the combination of unstable cavities to see if a
            # contingent forest was already built from this
            contingent_forest = self.contingent_trace_forests.get(ch_unstable_cavities)

            # No previous forest built from the given combination of disabled
            # unstable cavities so need to build one here
            if contingent_forest is None:
                LOGGER.debug(
                    "For unstable cavity combination %s no cached contingent "
                    "trace forest found, now attempting to build a new one...",
                    [uc.name for uc in ch_unstable_cavities],
                )
                contingent_forest = self._initialise_contingent_forest(ch_unstable_cavities)
                # If there are no dependencies left after disabling the
                # unstable cavities then a beam trace cannot be performed
                # at this data point so inform of this on return
                if contingent_forest is None:
                    return False

                # Cache the contingent forest for this combination of unstable
                # cavities as these typically occur in blocks (or across strides)
                # of data points so we don't want to keep rebuilding the same
                # contingency forests for identical unstable cavity combos
                self.contingent_trace_forests[ch_unstable_cavities] = contingent_forest
            else:
                LOGGER.debug(
                    "For unstable cavity combination %s found and using "
                    "cached contingent trace forest:%s",
                    [uc.name for uc in ch_unstable_cavities],
                    contingent_forest
                )

            # Make sure only the correctly changing beam parameters, according
            # to self.trace_forest, get reflagged when exiting from the unstable
            # region again
            self.needs_reflag_changing_q = True

            # Use the contingent forest for this data point
            trace_forest = contingent_forest

        # Otherwise we just use the standard changing trace forest of the simulation
        else:
            trace_forest = self.trace_forest

            # If we've just exited an unstable cavity region where a contingent trace
            # forest was being used, then we need to reflag the beam parameters which
            # are changing
            if self.needs_reflag_changing_q:
                self._determine_changing_beam_params(forest=None, set_tree_node_ids=False)
                self.needs_reflag_changing_q = False

        # Now do the actual beam tracing by simply traversing the forest
        # and propagating the beam through each tree
        for tree_idx in range(trace_forest.size()):
            tree = trace_forest.forest[tree_idx]

            if tree.is_source:
                cav_ws = self.cavity_workspaces.get(tree.dependency)
                source_is_cav = cav_ws is not None

                if not source_is_cav: # Source tree is from a Gauss
                    # TODO (sjr) Should probably make some workspace for Gauss objects
                    #            which then uses cy_expr's for evaluating these things
                    #            if they're symbolic. But for now this will do.
                    qx_src = complex(tree.dependency.qx.q)
                    qy_src = complex(tree.dependency.qy.q)
                else: # Source tree is from a Cavity
                    qx_src = cav_ws.qx
                    qy_src = cav_ws.qy

                self.trace[tree.node_id].qx.q = qx_src
                self.trace[tree.node_id].qy.q = qy_src
                if trace_forest.symmetric:
                    self.trace[tree.opp_node_id].qx.q = -conj(qx_src)
                    self.trace[tree.opp_node_id].qy.q = -conj(qy_src)

            self._propagate_trace(tree, trace_forest.symmetric)

        return True

    cpdef run_carrier(self) noexcept:
        """Runs the carrier matrix solver for the current state of the model.
        This will update all the C based structs with the current model state so
        that filling and calculations can be performed.

        Returns
        -------
        validity : bool
            True if this was a valid run, or False if a recoverable error occurred
            which results in the output being invalid for this call.
        """
        # NOTE (sjr) Just updating all parameter values on each call to run for
        #            now. This may not be the most optimal thing to do, but it
        #            avoids duplicating these parameter update calls in different
        #            places (e.g. refill, compute_knm_matrices, set_gouy_phases) and
        #            should be safe in that no parameters get accidentally missed at
        #            any data point.
        # ddb - this just updates everything, even things that are not changing as
        # it acts on all the workspaces, probably not the best idea
        self.update_all_parameter_values()

        # Update HOM stuff
        if self.is_modal:
            # Immediately return if invalid beam trace region encountered
            # no need to go ahead and fill or solve as they won't be used
            if not self.modal_update():
                return False

        if self.do_matrix_solving:
            self.carrier.run()

        return True

    cpdef run_signal(self, solve_noises=True) noexcept:
        """Runs the signal matrix solver for the current state. This function should assume that
        a call to the `run_carrier` method has preceeded it. Many modal and parameter updates
        should happen in there already, so do not need to be repeated here.
        """
        self.model_settings.fsig = float(self.model.fsig.f.value)
        # Probably some other preparatory stuff needs to go here in the future
        if self.do_matrix_solving:
            self.signal.run()

            # Then ask components for their noise contributions
            if solve_noises and self.signal.noise_sources:
                self.signal.fill_noise_inputs()
                self.signal.solve_noises()

    def setup_output_workspaces(self):
        # Once the simulations are started we can tell all the detectors to
        # prepare themselves
        self.detector_workspaces = []
        self.readout_workspaces = []

        for rd in self.model.get_elements_of_type(_Readout):
            # Readouts can emulate multiple detectors, so here we
            # get a collection of them depending on what the readout
            # is doing and add them to the list
            wss = rd._get_output_workspaces(self)
            if wss is not None:
                # Get the name of the readout output for storing
                # bit of a hack to get the attributes out of the
                # SimpleNamespace object used
                for name, ws in zip(rd.outputs.__dict__.values(), wss): # check we can iterate over the returned workspaces
                    if not isinstance(ws, DetectorWorkspace):
                        raise TypeError(f"Readout detector ({rd}) workspace ({ws}) not a DetectorWorkspace type")
                    self.readout_workspaces.append(ws)
                    self.workspace_name_map[name] = ws
                    if rd.output_detectors:
                        self.detector_workspaces.append(ws)

        for det in self.model.detectors:
            ws = det._get_workspace(self)
            self.workspace_name_map[det.name] = ws

            if not isinstance(ws, DetectorWorkspace):
                raise TypeError(f"Detector ({det}) workspace ({ws}) not a DetectorWorkspace type")

            self.detector_workspaces.append(ws)
            if self.signal and isinstance(ws.owner, NoiseDetector):
                self.signal.workspaces.noise_detectors.append(ws)

        for _ in self.detector_workspaces:
            _.compile_cy_exprs()

        if self.signal:
            self.signal.workspaces.detector_list_to_C()

    def __enter__(self):
        self.build()

    def __exit__(self, type_, value, traceback):
        self.unbuild()

    cpdef update_all_parameter_values(self) noexcept:
        """Loops through all workspaces to update the C structs so they
        represent the current model element parameter values.
        """
        cdef:
            ConnectorWorkspace ws

            Py_ssize_t i
            # TODO (sjr) Should probably cache these or move away from
            #            lists for best performance
            Py_ssize_t Ncws = len(self.workspaces)

        for i in range(Ncws):
            ws = self.workspaces[i]
            ws.update_parameter_values()

    def get_q(self, node):
        """Returns a tuple of (qx, qy) for a given node. The returned
        value is only valid until this simulations trace forest has
        been updated.

        Parameters
        ----------
        node : :class:`finesse.components.OpticalNode`
            Node to get beam parameters at

        Returns
        -------
        (qx, qy)
            Tuple of x and y beam parameters
        """
        cdef NodeBeamParam *nodebp

        idx = self.carrier.node_id(node)
        if idx >= 0 and idx < len(self.model.optical_nodes):
            nodebp = &self.trace[idx]
            return (
                BeamParam(q=nodebp.qx.q, nr=nodebp.qx.nr, wavelength=nodebp.qx.wavelength),
                BeamParam(q=nodebp.qy.q, nr=nodebp.qy.nr, wavelength=nodebp.qy.wavelength),
            )
        else:
            raise IndexError("Node index is not in simulation")

    cdef initialise_trace_forest(self, optical_nodes) noexcept:
        cdef TraceForest model_trace_forest
        cdef double nr
        # Before we setup the workspaces some initial beam trace must be done
        # so that workspaces can initialise themselves
        if self.is_modal:
            # Make sure the model trace forest gets re-planted
            # when building a new simulation
            self.model._rebuild_trace_forest = True
            LOGGER.info(
                "Performing initial beam trace with configuration options:\n    %s",
                self.model.sim_trace_config,
            )
            # Plant the model trace_forest and execute initial beam trace
            self.initial_trace_sol = self.model.beam_trace(**self.model.sim_initial_trace_args)
            model_trace_forest = self.model.trace_forest
            self.nodes_with_changing_q = model_trace_forest.get_nodes_with_changing_q()
            self.changing_mismatch_edges = set()

            LOGGER.info(
                "Nodes with changing q during simulation:\n    %s",
                self.nodes_with_changing_q,
            )
            self.retrace = self.model.sim_trace_config["retrace"]
            self.trace = <NodeBeamParam*> calloc(len(optical_nodes), sizeof(NodeBeamParam))
            if not self.trace:
                raise MemoryError()

            for i, n in enumerate(optical_nodes):
                qx, qy = self.initial_trace_sol[n]
                nr = qx.nr
                self.trace[i] = NodeBeamParam(
                    beam_param(qx.q, nr, self.model_settings.lambda0),
                    beam_param(qy.q, nr, self.model_settings.lambda0),
                    n in self.nodes_with_changing_q
                )

            if self.retrace:
                # Construct the forest of changing trace trees - it's important
                # that this is done before initialising connector workspaces as
                # they need the changing forest to be present for refill flag
                self.trace_forest = model_trace_forest.make_changing_forest()
                self.retrace &= not self.trace_forest.empty()

                if self.retrace:
                    LOGGER.info(
                        "Determined changing trace trees:%s", self.trace_forest
                    )
                    # Get the nodes at which trees of the changing forest intersect
                    # with trees of the full forest which have different trace
                    # dependencies. These couplings will have potentially changing
                    # mode mismatches during the simulation.
                    self.changing_mismatch_couplings = self.trace_forest.find_potential_mismatch_couplings(
                        model_trace_forest
                    )
                    # The above returns node objects. It is more useful to also store
                    # the equivalent simulation specific "node IDs" which is just an
                    # integer and used more in the cythonised code as some nodes get
                    # dropped when not used in a simulation.
                    # Optical nodes for signal and carrier all have the same IDs
                    for i, (ni, no) in enumerate(self.changing_mismatch_couplings):
                        self.changing_mismatch_edges.add(
                            tuple((self.carrier.node_id(ni), self.carrier.node_id(no)))
                        )

                    if self.changing_mismatch_couplings:
                        LOGGER.info(
                            "Found changing mismatched node couplings: %s",
                            [f"{n1.full_name} -> {n2.full_name}"
                            for n1, n2 in self.changing_mismatch_couplings]
                        )
            else:
                self.trace_forest = TraceForest(self.model, self.model.sim_trace_config["symmetric"])
        else:
            # just make an empty TraceForest
            self.trace_forest = TraceForest(self.model, self.model.sim_trace_config["symmetric"])

    cdef initialise_model_settings(self) noexcept:
        self.model_settings = self.model._settings

        if self.model.fsig.f.value is None:
            self.model_settings.fsig = 0
        else:
            self.model_settings.fsig = float(self.model.fsig.f.value)

    cdef initialise_sim_config_data(self) noexcept:
        # Nominal number of threads will be Nhoms / 10
        self.config_data.nthreads_homs = determine_nthreads_even(self.model_settings.num_HOMs, 10)

        LOGGER.info("Using %d threads for HOM parallel loops.", self.config_data.nthreads_homs)

    def generate_carrier_frequencies(self):
        """Returns a list of Frequency objects that the model has requested"""
        from finesse.frequency import Frequency, generate_frequency_list
        if len(self.model._frequency_generators) == 0:
            # Nothing in the model is generating a carrier frequency. Typical
            # situation is when no laser is included for signal modelling.
            # Simple solution, just use a default 0Hz
            frequencies_to_use = [Constant(0.0)]
        else:
            frequencies_to_use = generate_frequency_list(self.model)

        carrier_frequencies = list()

        LOGGER.info("Generating simulation with user carrier frequencies %s", self.model.frequencies)

        for i, f in enumerate(self.model.frequencies):
            try:
                f_name = str(f.eval(keep_changing_symbols=True))
            except AttributeError:
                f = Constant(f)
                f_name = str(f)

            carrier_frequencies.append(Frequency(f_name, self, f, index=i))

        N = len(self.model.frequencies)
        LOGGER.info("Generating simulation with carrier frequencies %s", frequencies_to_use)
        for i, f in enumerate(frequencies_to_use):
            carrier_frequencies.append(
                Frequency(
                    str(f.eval(keep_changing_symbols=True)),
                    self,
                    f,
                    index=N+i
                )
            )

        fcnt = FrequencyContainer(carrier_frequencies)
        return fcnt

    def generate_signal_frequencies(self, nodes, FrequencyContainer carrier_optical_frequencies):
        """Generates the optical, mechanical, and electrical frequencies that should be
        modelled by the signal simulation.
        """
        optical_frequencies = [] # All optical frequencies are present at all nodes
        # elec and mech can have different frequencies on a per node basis
        signal_frequencies = {}

        for i, f in enumerate(carrier_optical_frequencies.frequencies):
            fp = f.f + self.model.fsig.f.ref
            fm = f.f - self.model.fsig.f.ref
            optical_frequencies.append(
                Frequency(str(fp.eval(keep_changing_symbols=True)),
                            self, fp, index=2*i, audio_order=1,
                            audio=True, audio_carrier_index=i)
            )
            optical_frequencies.append(
                Frequency(str(fm.eval(keep_changing_symbols=True)),
                            self, fm, index=2*i+1, audio_order=-1,
                            audio=True, audio_carrier_index=i)
            )

        fcnt = FrequencyContainer(optical_frequencies, carrier_cnt=carrier_optical_frequencies)

        # Audio matrix frequencies are more complicated as they can have multiple frequencies
        # in mechanical and electrical, on a per-node basis...
        fsig = FrequencyContainer(
            (Frequency("fsig", self, self.model.fsig.f.ref, index=0), )
        )

        for node in nodes:
            if node.type == NodeType.OPTICAL:
                continue

            #-----------------------------------------------------------------------------------
            # Mechanical frequencies
            #-----------------------------------------------------------------------------------
            # By default mechanical frequencies just have a single frequency at the Model.fsig.f
            # However for more complicated systems we can have multiple frequencies.
            elif node.type == NodeType.MECHANICAL:
                fs = []
                freqs = node.frequencies
                if len(freqs) == 1 and freqs[0] == self.model.fsig.f.ref:
                    # Most components will just use a single fsig so reuse same object
                    # for efficient filling later
                    signal_frequencies[node] = fsig
                else:
                    for i, sym in enumerate(node.frequencies):
                        fs.append(
                            Frequency(
                                str(fm.eval(keep_changing_symbols=True)),
                                self,
                                sym,
                                index=i,
                            )
                        )
                    signal_frequencies[node] = FrequencyContainer(tuple(fs))

            #-----------------------------------------------------------------------------------
            # Electrical frequencies
            #-----------------------------------------------------------------------------------
            elif node.type == NodeType.ELECTRICAL:
                signal_frequencies[node] = fsig
            else:
                raise ValueError("Unexpected")

        return fcnt, signal_frequencies

    cpdef initialise_workspaces(self) noexcept:
        cdef ConnectorMatrixSimulationInfo info
        from finesse.components import Connector, Cavity
        # TODO ddb - probably need to move away from lists as they aren't that fast to iterate
        # over. Maybe once we have all the lists filled we can covert them into some PyObject
        # memoryview
        self.workspace_name_map = {}
        self.workspaces = []
        self.cavity_workspaces = {}
        self.to_scatter_matrix_compute = []
        self.gouy_phase_workspaces = []

        if self.is_modal and self.trace == NULL:
            raise Exception("Beam trace has not been set before workspaces are initialised")

        # Get any callbacks for the elements in the model
        # tell the element that we have now built the model and it
        # should do some initialisations for running simulations
        for el in self.model.elements.values():
            el._setup_changing_params()

            if isinstance(el, Connector):
                ws = el._get_workspace(self)
                if ws is None:
                    continue

                self.workspaces.append(ws) # store all workspaces here
                self.workspace_name_map[el.name] = ws

                if isinstance(ws, ConnectorWorkspace):
                    # Determine if we should be adding this workspace to any
                    # todo list for looping over later

                    # Here we grab the information objects from each workspace
                    # which describes the connections and filling to be done
                    # for each element for each simulation type
                    if self.signal:
                        x = (
                            (ws.carrier, self.carrier),
                            (ws.signal, self.signal)
                        )
                    else:
                        x = ((ws.carrier, self.carrier),)

                    for info, mtx in x:
                        ws_store = mtx.workspaces
                        if info.callback_flag & ConnectorCallbacks.FILL_MATRIX:
                            ws_store.to_initial_fill.append(ws) # Initial fill all
                            if info.matrix_fills.num_refills > 0 or mtx.forced_refill:
                                ws_store.to_refill.append(ws)

                        if info.callback_flag & ConnectorCallbacks.FILL_RHS:
                            ws_store.to_rhs_refill.append(ws)

                        if info.callback_flag & ConnectorCallbacks.FILL_NOISE:
                            try:
                                if any([x in self.signal.noise_sources for x in ws.owner.noises]):
                                    ws_store.to_noise_refill.append(ws)
                            except AttributeError:
                                # Component isn't a NoiseGenerator, but can still generate quantum
                                # noise
                                if NoiseType.QUANTUM in self.signal.noise_sources:
                                    ws_store.to_noise_refill.append(ws)

                        # Quantum noise is special, as all connectors can be a source if they have
                        # open inputs
                        if info.callback_flag & ConnectorCallbacks.FILL_INPUT_NOISE:
                            if NoiseType.QUANTUM in self.signal.noise_sources:
                                ws_store.to_noise_input_refill.append(ws)

                    if ws.fn_gouy_c is not None or ws.fn_gouy_py is not None:
                        self.gouy_phase_workspaces.append(ws)

                elif ws is not None:
                    # None means the component doesn't want anything
                    # to do with this simulation
                    raise Exception("Unexpected workspace type")
            elif isinstance(el, Cavity):
                self.cavity_workspaces[el] = el._get_workspace(self)
                self.workspace_name_map[el.name] = self.cavity_workspaces[el]

        # Compile cy_exprs for changing symbolics, these are stored
        # in ElementWorkspace.chprm_expr which is used for fast evaluating
        # of the changing symbolic expressions
        for ws in self.workspaces:
            ws.compile_cy_exprs()
            # Also compile the changing ABCD matrix elements, these are
            # stored in the relevant cy_expr** field of the associated
            # workspace -> note that the cy_expr* element is NULL for non
            # changing elements
            if self.is_modal:
                ws.compile_abcd_cy_exprs()

        LOGGER.info("Refilling carrier elements:\n%s", self.carrier.workspaces.to_refill)

        self.carrier.workspaces.list_to_C()
        if self.signal:
            LOGGER.info("Refilling signal elements:\n%s", self.signal.workspaces.to_refill)
            self.signal.workspaces.list_to_C()
        #print(self.name)
        #print("MATRIX")
        #print("carrier to_refill", len(self.carrier.workspaces.to_refill))
        #print("signal to_refill", len(self.signal.workspaces.to_refill))
        #print("to_rhs_refill", self.to_rhs_refill)



    cpdef initialise_noise_matrices(self) noexcept:
        from finesse.detectors.general import NoiseDetector

        # Which noise types are we measuring?
        for el in self.model.detectors:
            if isinstance(el, NoiseDetector):
                if el.noise_type not in self.signal.noise_sources:
                    self.signal.noise_sources[el.noise_type] = []
                    self.signal.add_noise_matrix(el.noise_type)

    cpdef initialise_noise_sources(self) noexcept:
        from finesse.components.general import NoiseGenerator

        for el in self.model.elements.values():
            if isinstance(el, NoiseGenerator):
                for _type, nodes in el.noises.items():
                    # Only consider noise sources for the types of noise we'll be measuring
                    if _type in self.signal.noise_sources:
                        self.signal.noise_sources[_type].append((el, nodes))

    cpdef initialise_noise_selection_vectors(self) noexcept:
        for el in self.model.elements.values():
            if hasattr(el, "_requested_selection_vectors"):
                for name in el._requested_selection_vectors:
                    el._requested_selection_vectors[name] = self.signal._M.request_rhs_view()


cdef class MatrixSystemWorkspaces:
    def __cinit__(self):
        self.ptr_to_refill = NULL
        self.ptr_to_rhs_refill = NULL
        self.ptr_to_noise_refill = NULL
        self.ptr_to_noise_input_refill = NULL
        self.ptr_noise_detectors = NULL

    def __init__(self):
        self.to_initial_fill = []
        self.to_refill = []
        self.to_rhs_refill = []
        self.to_noise_refill = []
        self.to_noise_input_refill = []
        self.noise_detectors = []

    def list_to_C(self):
        """Converts the python lists of workspaces into C Pyobject arrays for
        fast loop access.
        """
        if (
            self.ptr_to_refill != NULL
            or self.ptr_to_rhs_refill != NULL
            or self.ptr_to_noise_refill != NULL
            or self.ptr_to_noise_input_refill != NULL
        ):
            raise MemoryError()

        self.num_to_refill = len(self.to_refill)
        self.ptr_to_refill = <PyObject**> malloc(self.num_to_refill * sizeof(PyObject*))
        if not self.ptr_to_refill:
            raise MemoryError()
        cdef int i
        for i in range(self.num_to_refill):
            self.ptr_to_refill[i] = <PyObject*>self.to_refill[i]

        self.num_to_rhs_refill = len(self.to_rhs_refill)
        self.ptr_to_rhs_refill = <PyObject**> malloc(self.num_to_rhs_refill * sizeof(PyObject*))
        if not self.ptr_to_rhs_refill:
            raise MemoryError()
        for i in range(self.num_to_rhs_refill):
            self.ptr_to_rhs_refill[i] = <PyObject*>self.to_rhs_refill[i]

        self.num_to_noise_refill = len(self.to_noise_refill)
        self.ptr_to_noise_refill = <PyObject**> malloc(self.num_to_noise_refill * sizeof(PyObject*))
        if not self.ptr_to_noise_refill:
            raise MemoryError()
        for i in range(self.num_to_noise_refill):
            self.ptr_to_noise_refill[i] = <PyObject*>self.to_noise_refill[i]

        self.num_to_noise_input_refill = len(self.to_noise_input_refill)
        self.ptr_to_noise_input_refill = <PyObject**> malloc(self.num_to_noise_input_refill * sizeof(PyObject*))
        if not self.ptr_to_noise_input_refill:
            raise MemoryError()
        for i in range(self.num_to_noise_input_refill):
            self.ptr_to_noise_input_refill[i] = <PyObject*>self.to_noise_input_refill[i]

    def clear_workspaces(self):
        self.to_initial_fill.clear()
        self.to_refill.clear()
        self.to_rhs_refill.clear()
        self.to_noise_refill.clear()
        self.to_noise_input_refill.clear()
        self.noise_detectors.clear()

    def detector_list_to_C(self):
        self.num_noise_detectors = len(self.noise_detectors)
        if self.ptr_noise_detectors != NULL:
            raise MemoryError()
        self.ptr_noise_detectors = <PyObject**> malloc(self.num_noise_detectors * sizeof(PyObject*))
        if not self.ptr_noise_detectors:
            raise MemoryError()
        for i in range(self.num_noise_detectors):
            self.ptr_noise_detectors[i] = <PyObject*>self.noise_detectors[i]

    def __dealloc__(self):
        if self.ptr_to_refill:
            free(self.ptr_to_refill)

        if self.ptr_to_rhs_refill:
            free(self.ptr_to_rhs_refill)

        if self.ptr_to_noise_refill:
            free(self.ptr_to_noise_refill)

        if self.ptr_to_noise_input_refill:
            free(self.ptr_to_noise_input_refill)

        if self.ptr_noise_detectors:
            free(self.ptr_noise_detectors)
