from finesse.cmatrix cimport CCSMatrix
from finesse.cymath cimport complex_t
from finesse.tracing.tree cimport TraceTree
from finesse.tracing.forest cimport TraceForest
from finesse.simulations.base cimport ModelSettings, NodeBeamParam, SimConfigData
from finesse.frequency cimport frequency_info_t, FrequencyContainer, Frequency
from cpython.ref cimport PyObject
from finesse.components.workspace cimport ConnectorWorkspace


cdef extern from "constants.h":
    long double PI
    double C_LIGHT

# Structure to store the various information about each individual node
# such as where the node sits in the RHS vector, what the unique index is
# in a given simulation.
cdef struct NodeInfoEntry:
    Py_ssize_t index # unique index
    Py_ssize_t rhs_index # index node starts in RHS vector
    Py_ssize_t freq_index
    Py_ssize_t nfreqs # number of frequencies at this node
    Py_ssize_t nhoms # number of HOMs at this node
    frequency_info_t *frequencies # Frequencies array present at this node, size nfreqs


cdef class MatrixSystemWorkspaces:
    cdef readonly:
        list to_initial_fill
        list to_refill
        list to_rhs_refill
        list to_noise_refill
        list to_noise_input_refill
        list noise_detectors
        int num_to_refill
        int num_to_rhs_refill
        int num_to_noise_refill
        int num_to_noise_input_refill
        int num_noise_detectors
    cdef:
        PyObject** ptr_to_refill
        PyObject** ptr_to_rhs_refill
        PyObject** ptr_to_noise_refill
        PyObject** ptr_to_noise_input_refill
        PyObject** ptr_noise_detectors


cdef class MatrixSystemSolver:
    cdef:
        readonly CCSMatrix _M
        readonly dict connections
        readonly dict _noise_matrices
        readonly dict _submatrices
        readonly dict _diagonals
        readonly dict _noise_submatrices
        Py_ssize_t num_nodes
        readonly dict nodes
        readonly dict node_map
        readonly dict nodes_idx
        NodeInfoEntry* _c_node_info
        readonly FrequencyContainer optical_frequencies
        readonly dict signal_frequencies
        readonly tuple unique_elec_mech_fcnts # Unique frequency containers for mech/elec
        readonly dict noise_sources
        readonly int nhoms
        readonly complex_t[::1] out_view
        readonly bint any_frequencies_changing
        bint is_signal_matrix
        readonly bint forced_refill
        public bint manual_rhs
        readonly MatrixSystemWorkspaces workspaces
        readonly unsigned int num_solves # number of times solve has been called

        # Edges that have a changing mode mismatch, Node ID pair (in, out)
        readonly int[:, ::1] changing_mismatch_node_ids

    cpdef setup_nodes(self, list nodes, dict node_map) noexcept
    cpdef clear_rhs(self) noexcept
    cdef initial_fill(self) noexcept
    cpdef refill(self) noexcept
    cdef fill_rhs(self) noexcept
    cdef fill_noise_inputs(self) noexcept
    cdef refactor(self) noexcept
    cdef factor(self) noexcept
    cdef solve(self) noexcept
    cdef solve_noises(self) noexcept
    cdef construct(self) noexcept
    cdef destruct(self) noexcept
    cdef initial_run(self) noexcept
    cpdef run(self) noexcept

    cdef get_node_matrix_params(self, node, Py_ssize_t *Ns, Py_ssize_t *Nf, frequency_info_t** fptr) noexcept
    cdef tuple get_node_frequencies(self, node) noexcept

    cdef update_frequency_info(self) noexcept
    cdef assign_submatrices(self, workspaces) noexcept
    cdef assign_noise_submatrices(self, workspaces) noexcept

    cdef add_noise_matrix(self, object key) noexcept
    cdef add_rhs(self, unicode key) noexcept

    cpdef Py_ssize_t findex(self, object node, Py_ssize_t freq) noexcept
    cdef Py_ssize_t findex_fast(self, Py_ssize_t node_id, Py_ssize_t freq) noexcept nogil

    cpdef Py_ssize_t field(self, object node, Py_ssize_t freq=?, Py_ssize_t hom=?) noexcept
    cdef Py_ssize_t field_fast(self, Py_ssize_t node_id, Py_ssize_t freq=?, Py_ssize_t hom=?) noexcept nogil
    cdef inline Py_ssize_t field_fast_2(
        self,
        Py_ssize_t node_rhs_idx,
        Py_ssize_t num_hom,
        Py_ssize_t freq,
        Py_ssize_t hom
    ) noexcept nogil

    cpdef complex_t get_out(self, object node, Py_ssize_t freq=?, Py_ssize_t hom=?) noexcept
    cdef complex_t get_out_fast(self, Py_ssize_t node_id, Py_ssize_t freq=?, Py_ssize_t hom=?) noexcept nogil

    cdef int set_source_fast(self, Py_ssize_t node_id, Py_ssize_t freq_idx, Py_ssize_t hom_idx, complex_t value, unsigned rhs_index=?) except -1
    cdef int set_source_fast_2(self, Py_ssize_t rhs_idx, complex_t value) except -1
    cdef int set_source_fast_3(self, Py_ssize_t rhs_idx, complex_t value, unsigned rhs_index) except -1

    cpdef Py_ssize_t node_id(self, object node) noexcept
    cpdef get_node_info(self, name) noexcept



cdef class CarrierSignalMatrixSimulation:
    cdef:
        readonly MatrixSystemSolver carrier
        readonly MatrixSystemSolver signal
        readonly bint compute_signals

        readonly unicode name
        readonly set changing_parameters
        readonly set tunable_parameters
        readonly object model
        readonly bint is_modal
        readonly bint do_matrix_solving

        readonly MatrixSystemWorkspaces carrier_ws
        readonly MatrixSystemWorkspaces signal_ws
        readonly list detector_workspaces
        readonly list readout_workspaces

        public dict workspace_name_map
        public list workspaces
        public list variable_workspaces
        readonly list gouy_phase_workspaces

        ### Tracing stuff ###
        public dict cavity_workspaces
        NodeBeamParam* trace
        # Beam parameters in initial state as a BeamTraceSolution object
        readonly object initial_trace_sol
        # The TraceForest of geometrically changing branches. This is an
        # empty forest for any simulation in which geometric parameters
        # are not changing.
        readonly TraceForest trace_forest
        # Node couplings which will have changing mode mismatches,
        # determined from trace_forest via tree intersection searching
        readonly tuple changing_mismatch_couplings
        # Optical node id pairs (in, out) where mismatch is happening
        readonly set changing_mismatch_edges
        readonly set nodes_with_changing_q # Nodes that will potentially have a changing q
        # A dict of {<tuple of newly unstable cavities> : <contingent TraceForest>}
        # required for when a scan results in a geometrically changing cavity becoming
        # unstable -> invalidating self.trace_forest temporarily for that data point
        dict contingent_trace_forests
        bint needs_reflag_changing_q # Used when exiting from unstable cavity regions
        bint retrace

        # List of workspaces for components which scatter modes
        list to_scatter_matrix_compute
        readonly ModelSettings model_settings
        object __weakref__

        SimConfigData config_data

    cdef initialise_model_settings(self) noexcept
    cdef initialise_sim_config_data(self) noexcept

    cpdef initialise_workspaces(self) noexcept
    cpdef initialise_noise_matrices(self) noexcept
    cpdef initialise_noise_sources(self) noexcept
    cpdef initialise_noise_selection_vectors(self) noexcept
    cdef initialise_trace_forest(self, optical_nodes) noexcept
    cpdef update_all_parameter_values(self) noexcept
    cpdef update_map_data(self) noexcept
    cdef void update_cavities(self) noexcept
    cpdef void compute_knm_matrices(self) noexcept
    cdef int set_gouy_phases(self) except -1
    cpdef modal_update(self) noexcept

    cpdef run_carrier(self) noexcept
    cpdef run_signal(self, solve_noises=?) noexcept

    # Methods to construct the changing TraceForest for the simulation
    cdef _determine_changing_beam_params(self, TraceForest forest=?, bint set_tree_node_ids=?) noexcept
    cdef void _setup_trace_forest(self, TraceForest forest=?, bint set_tree_node_ids=?) noexcept
    cdef void _setup_single_trace_tree(self, TraceTree tree, bint set_tree_node_ids=?) noexcept

    # Find the newly unstable cavity instances from the changing forest
    cdef tuple _find_new_unstable_cavities(self) noexcept
    cdef TraceForest _initialise_contingent_forest(self, tuple unstable_cavities) noexcept

    # Perform the beam trace on the changing TraceForest
    cdef void _propagate_trace(self, TraceTree tree, bint symmetric) noexcept
    cpdef trace_beam(self) noexcept
