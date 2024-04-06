"""Collection of Actions that deal linear time invariant (LTI) modelling tasks."""

import logging

import numpy as np

from finesse.components import Node
from finesse.components.node import NodeType
from finesse.exceptions import FinesseException

from ...components import DegreeOfFreedom
from ...solutions import BaseSolution
from ..runners import run_fsig_sweep, run_fsig_sweep2, run_fsig_sweep3
from .base import Action, names_to_nodes

LOGGER = logging.getLogger(__name__)


class FrequencyResponseSolution(BaseSolution):
    """A solution from running a :class:`FrequencyResponse` action on a model. This
    solution contains the frequency vector and potentially multiple input and output
    transfer function matrix.

    Attributes
    ----------
    f : array_like
        Frequency vector [Hz]
    inputs : array_like
        The input names injected into for this analysis
    outputs : array_like
        The output names read out for this analysis
    out : arrray_like[dtype=np.complex128]
        A matrix of transfer functions for each input to every output over the
        array of frequencies requested. Depending on which frequency response
        action was run will decide what shape this output matrix actually is.
    """

    def __getitem__(self, key):
        try:
            key = np.atleast_1d(key).tolist()
            inp_key = slice(None, None, None)
            out_key = slice(None, None, None)

            for k in key:
                _k = np.atleast_1d(k)
                if all(_ in self.inputs for _ in _k):
                    inp_key = tuple(self.inputs.index(_) for _ in _k)
                if all(_ in self.outputs for _ in _k):
                    out_key = tuple(self.outputs.index(_) for _ in _k)

            slices = (slice(None, None, None), inp_key, out_key)
            return self.out[slices].squeeze()
        except (ValueError, IndexError, TypeError):
            return super().__getitem__(key)

    def plot_dofs(self, *dofs, axs=None, max_width=12, show_unity=False, **kwargs):
        import matplotlib.pyplot as plt
        import numpy as np

        if "show" in kwargs:
            del kwargs["show"]

        if len(dofs) == 0:
            dofs = self.inputs

        if axs is None:
            # if no axes are given then grab the figure
            # and any axes that are in it
            fig = plt.gcf()
            axs = np.atleast_2d(fig.axes)
        else:
            axs = np.atleast_2d(axs)
            fig = axs[0, 0].figure()

        dofs = np.atleast_1d(dofs)
        N = len(dofs)
        W = min(5, max_width / N)
        if np.prod(axs.shape) != N:
            fig, axs = plt.subplots(
                1, N, figsize=(W * N, 3.5), squeeze=False, sharey=True
            )

        if "label" not in kwargs:
            kwargs["label"] = self.outputs

        for i, dof in enumerate(dofs):
            axs[0, i].loglog(self.f, abs(self[dof]), **kwargs)
            axs[0, i].set_xlabel("Frequency [Hz]")
            axs[0, i].set_title(dof)
            axs[0, i].legend()
            if show_unity:
                axs[0, i].hlines(
                    1, min(self.f), max(self.f), color="k", ls=":", zorder=-10
                )

        axs[0, 0].set_ylabel("OUTPUT/DOF")
        plt.tight_layout()

        return fig, axs

    plot = plot_dofs  # Default plot option

    def plot_readouts(self, *readouts, axs=None, max_width=12, **kwargs):
        import matplotlib.pyplot as plt

        if len(readouts) == 0:
            readouts = self.outputs

        readouts = np.atleast_1d(readouts)
        if axs is None:
            N = len(readouts)
            W = min(5, max_width / N)
            fig, axs = plt.subplots(
                1, N, figsize=(W * N, 3.5), squeeze=False, sharey=True
            )
        else:
            fig = plt.gcf()

        if "label" not in kwargs:
            kwargs["label"] = self.inputs

        for i, rd in enumerate(readouts):
            axs[0, i].loglog(self.f, abs(self[rd]), **kwargs)
            axs[0, i].set_xlabel("Frequency [Hz]")
            axs[0, i].set_title(rd)
            axs[0, i].legend()

        axs[0, 0].set_ylabel("OUTPUT/DOF")
        plt.tight_layout()

        return fig, axs


# IMPORTANT: renaming this class impacts the katscript spec and should be avoided!
class FrequencyResponse(Action):
    """Computes the frequency response of a signal injceted at various nodes to compute
    transfer functions to multiple output nodes. Inputs and outputs should be electrical
    or mechanical nodes. It does this in an efficient way by using the same model and
    solving for multiple RHS input vectors.

    This action does not alter the model state. This action will ignore any currently
    definied signal generator elements in the model.

    To inject into optical nodes please see :class:`FrequencyResponse2`.

    Parameters
    ----------
    f : array, double
        Frequencies to compute the transfer functions over
    inputs : iterable[str or Element]
        Mechanical or electrical node to inject signal at
    outputs : iterable[str or Element]
        Mechanical or electrical nodes to measure output at
    open_loop : bool, optional
        Computes open loop transfer functions if the system has closed
    name : str, optional
        Solution name

    Examples
    --------
    Here we measure a set of transfer functions from DARM and CARM
    to four readouts for a particular `model`,

    >>> sol = model.run(FrequencyResponse(np.geomspace(0.1, 50000, 100),
    ...         ('DARM', 'CARM'),
    ...         ('AS.DC', 'AS45.I', 'AS45.Q', 'REFL9.I'),
    ... ))

    Single inputs and outputs can also be specified

    >>> model.run(FrequencyResponse(np.geomspace(0.1, 50000, 100), 'DARM', AS.DC'))

    The transfer functions can then be accessed like a 2D array by name,
    the ordering of inputs to outputs does not matter.

    >>> sol['DARM'] # DARM to all outputs
    >>> sol['DARM', 'AS.DC'] # DARM to AS.DC
    >>> sol['DARM', ('AS.DC', 'AS45.I')]
    >>> sol['AS.DC'] # All inputs to AS.DC readout
    """

    def __init__(
        self, f, inputs, outputs, *, open_loop=False, name="frequency_response"
    ):
        super().__init__(name)
        inputs = np.atleast_1d(inputs)
        outputs = np.atleast_1d(outputs)
        if f is None:
            raise FinesseException("A frequency vector must be provided")

        try:
            self.f = np.array(f, dtype=np.float64, copy=True)
        except Exception:
            # If the f is a symbol...
            self.f = np.array(f.eval(), dtype=np.float64, copy=True)
        if self.f.size == 0:
            raise FinesseException("Frequency vector has size 0")
        if any(self.f <= 0):
            raise FinesseException(
                "Frequency vector must contain values greater than 0"
            )

        def process(x, input):
            if isinstance(x, DegreeOfFreedom):
                if input:
                    return x.AC.i.full_name
                else:
                    return x.AC.o.full_name
            elif isinstance(x, (str, np.str_)):
                return x
            else:  # Try and get full_name
                return x.full_name

        self.inputs = list(process(i, True) for i in inputs)
        self.outputs = list(process(o, False) for o in outputs)
        self.open_loop = open_loop

    def _do(self, state, fsig_independant_outputs=None, fsig_dependant_outputs=None):
        input_rhs_indices = np.zeros(len(self.inputs), dtype=int)
        output_rhs_indices = np.zeros(len(self.outputs), dtype=int)

        # some signals will need to be scaled
        input_scaling = np.ones(len(self.inputs), dtype=float)
        output_scaling = np.ones(len(self.outputs), dtype=float)

        for i, node in enumerate(
            names_to_nodes(state.model, self.inputs, default_hints=("input",))
        ):
            if node.type is NodeType.OPTICAL:
                raise FinesseException(
                    f"Optical nodes ({node}) cannot be used with the frequency response action"
                )
            else:
                # set scaling for mechanical input signals
                if node.type is NodeType.MECHANICAL:
                    input_scaling[i] /= state.sim.model_settings.x_scale

                input_rhs_indices[i] = state.sim.signal.field(node, 0, 0)
        for i, node in enumerate(
            names_to_nodes(state.model, self.outputs, default_hints=("output",))
        ):
            if node.type is NodeType.OPTICAL:
                raise FinesseException(
                    f"Optical nodes ({node}) cannot be used with the frequency response action"
                )
            else:
                # set scaling for mechanical output signals
                if node.type is NodeType.MECHANICAL:
                    output_scaling[i] *= state.sim.model_settings.x_scale

                output_rhs_indices[i] = state.sim.signal.field(node, 0, 0)

        sol = FrequencyResponseSolution(self.name)
        sol.f = self.f
        sol.inputs = self.inputs
        sol.outputs = self.outputs
        state.sim.run_carrier()
        rtn = run_fsig_sweep(
            state.sim,
            self.f,
            input_rhs_indices,
            output_rhs_indices,
            input_scaling,
            output_scaling,
            None,
            self.open_loop,
            tuple(fsig_independant_outputs)
            if fsig_independant_outputs is not None
            else None,
            tuple(fsig_dependant_outputs)
            if fsig_dependant_outputs is not None
            else None,
        )
        if (fsig_dependant_outputs is not None) or (
            fsig_independant_outputs is not None
        ):
            sol.out = rtn[0]
            sol.extra_outputs = rtn[1]
        else:
            sol.out = rtn

        return sol

    def _requests(self, model, memo, first=True):
        memo["changing_parameters"].append("fsig.f")
        memo["keep_nodes"].extend((_, ("input",)) for _ in self.inputs)
        memo["keep_nodes"].extend((_, ("output",)) for _ in self.outputs)


# IMPORTANT: renaming this class impacts the katscript spec and should be avoided!
class FrequencyResponse2(Action):
    """Computes the frequency response of a signal injected at an optical port at a
    particular optical frequency. This differs from :class:`FrequencyResponse` in the
    way the inputs and outputs are prescribed. For :class:`FrequencyResponse2` you
    specify optical input nodes and a signal output node.

    This action does not alter the model state. This action will ignore any currently
    definied signal generator elements in the model.

    Produces an output transfer matrix from each HOM at a particular frequency and
    optical node to some readout output. The shape of the output matrix is:

    [frequencies, outputs, inputs, HOMs]

    It should be noted that when exciting a lower signal sideband frequency it will
    actually return the operator for propagating the conjugate of the lower sideband.
    This is because FINESSE is internally solving for the conjugate of the lower sideband
    to linearise non-linear optical effects.

    Parameters
    ----------
    f : array, double
        Frequencies to compute the transfer functions over
    inputs : iterable[tuple[str or Node, Frequency]]
        Optical node and frequency tuple to inject at. A symbolic refence to the
        model's fsig.f parameter should always be used when defining a frequency to
        look at.
    outputs : iterable[str or Element]
        Mechanical or electrical (signal)nodes to measure output to
    name : str, optional
        Solution name

    Examples
    --------
    It is advisable to use always use a reference to the symbolic reference to
    the signal frequency `model.fsig.f.ref` instead of a fixed number incase it
    changes. This action will look for an initial frequency bin of X Hz to track
    during the frequency response analysis. A symbolic reference will always
    ensure the right bin is used, in cases such as looking at RF signal sidebands,
    `10e6+model.fsig.f.ref` and `10e6-model.fsig.f.ref` will always look at the
    upper and lower signal sideband around the +10MHz sideband.

    >>> import finesse
    >>> from finesse.analysis.actions import FrequencyResponse2
    >>> model = finesse.script.parse('''
    ... l l1
    ... bs bs1 R=1 T=0 xbeta=1e-6 ybeta=1e-9
    ... readout_dc A
    ... link(l1, bs1, A)
    ... fsig(1)
    ... modes(maxtem=1)
    ... gauss g1 l1.p1.o w=1m Rc=inf
    ... ''')
    >>> sol = model.run(
    ...     FrequencyResponse2(
    ...         [1, 10, 100],
    ...         [
    ...             ('bs1.p2.o', +model.fsig.f.ref),
    ...             ('bs1.p2.o', -model.fsig.f.ref)
    ...         ],
    ...         ['A.DC']
    ...     )
    ... )
    """

    def __init__(self, f, inputs, outputs, *, name="frequency_response2"):
        super().__init__(name)

        if f is None:
            raise FinesseException("A frequency vector must be provided")
        try:
            self.f = np.array(f, dtype=np.float64, copy=True)
        except Exception:
            # If the f is a symbol...
            self.f = np.array(f.eval(), dtype=np.float64, copy=True)
        if self.f.size == 0:
            raise FinesseException("Frequency vector has size 0")
        if any(self.f <= 0):
            raise FinesseException(
                "Frequency vector must contain values greater than 0"
            )

        self.inputs = inputs
        self.outputs = outputs

        self.input_nodes = []
        self.input_freqs = []
        for node, freq in inputs:
            if not isinstance(node, (Node, str, np.str_)):
                raise FinesseException(
                    f"Inputs should be a node or a string name of a node, not {node}"
                )
            self.input_nodes.append(node)
            self.input_freqs.append(freq)

        self.output_nodes = []
        for node in outputs:
            if not isinstance(node, (Node, str, np.str_)):
                raise FinesseException(
                    f"Outputs should be a node or a string name of a node, not {node}"
                )
            self.output_nodes.append(node)

        def process_node(x, input):
            if isinstance(x, DegreeOfFreedom):
                if input:
                    return x.AC.i.full_name
                else:
                    return x.AC.o.full_name
            elif isinstance(x, (str, np.str_)):
                return x
            else:  # Try and get full_name
                return x.full_name

        self.input_nodes = list(process_node(i, True) for i in self.input_nodes)
        self.output_nodes = list(process_node(o, False) for o in self.output_nodes)

    def _do(self, state, fsig_independant_outputs=None, fsig_dependant_outputs=None):
        input_rhs_indices = np.zeros(len(self.input_nodes), dtype=int)
        output_rhs_indices = np.zeros(len(self.output_nodes), dtype=int)

        # some signals will need to be scaled
        input_scaling = np.ones(len(self.input_nodes), dtype=float)
        output_scaling = np.ones(len(self.output_nodes), dtype=float)

        for i, (node, freq) in enumerate(
            zip(
                names_to_nodes(state.model, self.input_nodes, default_hints=("input",)),
                self.input_freqs,
            )
        ):
            freq_obj = state.sim.signal.get_frequency_object(freq, node)
            freq_idx = freq_obj.index

            if node.type is NodeType.OPTICAL:
                input_rhs_indices[i] = state.sim.signal.field(node, freq_idx, 0)
            else:
                if freq_idx != 0:
                    raise FinesseException(
                        f"Input frequency for {node} should be the signal frequency"
                    )
                # set scaling for mechanical input signals
                if node.type is NodeType.MECHANICAL:
                    input_scaling[i] /= state.sim.model_settings.x_scale
                input_rhs_indices[i] = state.sim.signal.field(node, 0, 0)

        for i, node in enumerate(
            names_to_nodes(state.model, self.output_nodes, default_hints=("output",))
        ):
            if node.type is NodeType.OPTICAL:
                raise FinesseException(
                    f"Optical nodes ({node}) cannot be used with the FrequencyResponse2 action"
                )
            else:
                # set scaling for mechanical output signals
                if node.type is NodeType.MECHANICAL:
                    output_scaling[i] *= state.sim.model_settings.x_scale
                output_rhs_indices[i] = state.sim.signal.field(node, 0, 0)

        sol = FrequencyResponseSolution(self.name)
        sol.f = self.f
        sol.inputs = self.inputs
        sol.outputs = self.outputs
        state.sim.run_carrier()
        rtn = run_fsig_sweep2(
            state.sim,
            self.f,
            input_rhs_indices,
            output_rhs_indices,
            input_scaling,
            output_scaling,
            None,
            tuple(fsig_independant_outputs)
            if fsig_independant_outputs is not None
            else None,
            tuple(fsig_dependant_outputs)
            if fsig_dependant_outputs is not None
            else None,
        )
        if (fsig_dependant_outputs is not None) or (
            fsig_independant_outputs is not None
        ):
            sol.out = rtn[0]
            sol.extra_outputs = rtn[1]
        else:
            sol.out = rtn

        return sol

    def _requests(self, model, memo, first=True):
        for freq in self.input_freqs:
            try:
                if model.fsig.f.ref not in freq.parameters():
                    raise IndexError()
            except (AttributeError, IndexError):  # catch if freq not a symbol
                raise FinesseException(
                    f"{self} requires frequencies to be specified as a symbolic expression which must include `model.fsig.f.ref`, not {freq}."
                )

        memo["changing_parameters"].append("fsig.f")
        memo["keep_nodes"].extend((_, ("input",)) for _ in self.input_nodes)
        memo["keep_nodes"].extend((_, ("output",)) for _ in self.output_nodes)


# IMPORTANT: renaming this class impacts the katscript spec and should be avoided!
class FrequencyResponse3(Action):
    """Computes the frequency response of a signal injected at an optical port at a
    particular optical frequency. This differs from :class:`FrequencyResponse` in the
    way the inputs and outputs are prescribed. For :class:`FrequencyResponse3` you
    specify optical input nodes and a signal output node.

    This action does not alter the model state. This action will ignore any currently
    definied signal generator elements in the model.

    Produces an output transfer matrix from each HOM at a particular frequency and
    optical node to some other optical node and frequency.

    The shape of the output matrix is: [frequencies, outputs, inputs, HOMs, HOMs]

    It should be noted that when exciting a lower signal sideband frequency it will
    actually return the operator for propagating the conjugate of the lower sideband.
    This is because FINESSE is internally solving for the conjugate of the lower sideband
    to linearise non-linear optical effects.

    Parameters
    ----------
    f : array, double
        Frequencies to compute the transfer functions over
    inputs : iterable[tuple[str or Node, Frequency]]
        Optical node and frequency tuple to inject at
    outputs : iterable[tuple[str or Node, Frequency]]
        Optical node and frequency tuple to inject at
    name : str, optional
        Solution name

    Examples
    --------
    It is advisable to use always use a reference to the symbolic reference to
    the signal frequency `model.fsig.f.ref` instead of a fixed number incase it
    changes. This action will look for an initial frequency bin of X Hz to track
    during the frequency response analysis. A symbolic reference will always
    ensure the right bin is used, in cases such as looking at RF signal sidebands,
    `10e6+model.fsig.f.ref` and `10e6-model.fsig.f.ref` will always look at the
    upper and lower signal sideband around the +10MHz sideband.

    >>> import finesse
    >>> from finesse.analysis.actions import FrequencyResponse3
    >>> model = finesse.script.parse('''
    ... l l1
    ... bs bs1 R=1 T=0 xbeta=1e-6 ybeta=1e-9
    ... readout_dc A
    ... link(l1, bs1, A)
    ... fsig(1)
    ... modes(maxtem=1)
    ... gauss g1 l1.p1.o w=1m Rc=inf
    ... ''')
    >>> sol = model.run(
    ...     FrequencyResponse3(
    ...         [1, 10, 100],
    ...         [
    ...             ('bs1.p2.o', +model.fsig.f.ref),
    ...             ('bs1.p2.o', -model.fsig.f.ref)
    ...         ],
    ...         [
    ...             ('A.p1.i', +model.fsig.f.ref),
    ...             ('A.p1.i', -model.fsig.f.ref)
    ...         ]
    ...     )
    ... )
    """

    def __init__(self, f, inputs, outputs, *, name="frequency_response2"):
        super().__init__(name)

        if f is None:
            raise FinesseException("A frequency vector must be provided")
        try:
            self.f = np.array(f, dtype=np.float64, copy=True)
        except Exception:
            # If the f is a symbol...
            self.f = np.array(f.eval(), dtype=np.float64, copy=True)
        if self.f.size == 0:
            raise FinesseException("Frequency vector has size 0")
        if any(self.f <= 0):
            raise FinesseException(
                "Frequency vector must contain values greater than 0"
            )

        self.inputs = inputs
        self.outputs = outputs

        self.input_nodes = []
        self.input_freqs = []
        for node, freq in inputs:
            self.input_nodes.append(node)
            self.input_freqs.append(freq)

        self.output_nodes = []
        self.output_freqs = []
        for node, freq in outputs:
            self.output_nodes.append(node)
            self.output_freqs.append(freq)

        def process_node(x, input):
            if isinstance(x, DegreeOfFreedom):
                if input:
                    return x.AC.i.full_name
                else:
                    return x.AC.o.full_name
            elif isinstance(x, (str, np.str_)):
                return x
            else:  # Try and get full_name
                return x.full_name

        self.input_nodes = list(process_node(i, True) for i in self.input_nodes)
        self.output_nodes = list(process_node(o, False) for o in self.output_nodes)

    def _do(self, state, fsig_independant_outputs=None, fsig_dependant_outputs=None):
        input_rhs_indices = np.zeros(len(self.input_nodes), dtype=int)
        output_rhs_indices = np.zeros(len(self.output_nodes), dtype=int)

        # some signals will need to be scaled
        input_scaling = np.ones(len(self.input_nodes), dtype=float)
        output_scaling = np.ones(len(self.output_nodes), dtype=float)

        for i, (node, freq) in enumerate(
            zip(
                names_to_nodes(state.model, self.input_nodes, default_hints=("input",)),
                self.input_freqs,
            )
        ):
            if node.type is NodeType.OPTICAL:
                freq_obj = state.sim.signal.get_frequency_object(freq, node)
                freq_idx = freq_obj.index
                input_rhs_indices[i] = state.sim.signal.field(node, freq_idx, 0)
            else:
                raise FinesseException(
                    f"Optical nodes ({node}) must be used with the FrequencyResponse3 action"
                )

        for i, (node, freq) in enumerate(
            zip(
                names_to_nodes(
                    state.model, self.output_nodes, default_hints=("output",)
                ),
                self.output_freqs,
            )
        ):
            if node.type is NodeType.OPTICAL:
                freq_obj = state.sim.signal.get_frequency_object(freq, node)
                freq_idx = freq_obj.index
                output_rhs_indices[i] = state.sim.signal.field(node, freq_idx, 0)
            else:
                raise FinesseException(
                    f"Optical nodes ({node}) must be used with the FrequencyResponse3 action"
                )

        sol = FrequencyResponseSolution(self.name)
        sol.f = self.f
        sol.inputs = self.inputs
        sol.outputs = self.outputs
        state.sim.run_carrier()
        rtn = run_fsig_sweep3(
            state.sim,
            self.f,
            input_rhs_indices,
            output_rhs_indices,
            input_scaling,
            output_scaling,
            None,
            tuple(fsig_independant_outputs)
            if fsig_independant_outputs is not None
            else None,
            tuple(fsig_dependant_outputs)
            if fsig_dependant_outputs is not None
            else None,
        )
        if (fsig_dependant_outputs is not None) or (
            fsig_independant_outputs is not None
        ):
            sol.out = rtn[0]
            sol.extra_outputs = rtn[1]
        else:
            sol.out = rtn

        return sol

    def _requests(self, model, memo, first=True):
        for flist in [self.input_freqs, self.output_freqs]:
            for freq in flist:
                try:
                    if model.fsig.f.ref not in freq.parameters():
                        raise IndexError()
                except (AttributeError, IndexError):  # catch if freq not a symbol
                    raise FinesseException(
                        f"{self} requires frequencies to be specified as a symbolic expression which must include `model.fsig.f.ref`, not {repr(freq)}."
                    )

        memo["changing_parameters"].append("fsig.f")
        memo["keep_nodes"].extend((_, ("input",)) for _ in self.input_nodes)
        memo["keep_nodes"].extend((_, ("output",)) for _ in self.output_nodes)
