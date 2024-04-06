# cython: profile=False

import logging

cimport numpy as np
import numpy as np
import cython
from libc.stdlib cimport free, malloc
from cpython.ref cimport PyObject
from finesse.cymath cimport complex_t
import finesse
from finesse.parameter cimport Parameter
from finesse.simulations.basematrix cimport CarrierSignalMatrixSimulation
from finesse.solutions.array import ArraySolution
from finesse.solutions.array cimport ArraySolution
from finesse.detectors.workspace import DetectorWorkspace
from finesse.detectors.workspace cimport DetectorWorkspace

from tqdm.auto import tqdm

LOGGER = logging.getLogger(__name__)


ctypedef object (*fptr_callback)(CarrierSignalMatrixSimulation)


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.initializedcheck(False)
cpdef run_fsig_sweep(
        CarrierSignalMatrixSimulation sim,
        double[::1] axis,
        long[::1] input_rhs_indices,
        long[::1] output_rhs_indices,
        double[::1] input_scaling,
        double[::1] output_scaling,
        complex_t[:,:,::1] out,
        bint compute_open_loop,
        tuple fsig_independant_outputs = None,
        tuple fsig_dependant_outputs = None,
    ) noexcept:
    """ Runs a simulation to sweep over a signal frequency axis.
    It does this in an optimised way for multiple inputs and outputs.
    It does not use detectors to compute outputs, it will just solve
    the matrix and return transfer functions between nodes. This is
    so it can be used internally for computing TFs without need to add
    detectors everywhere which the user has not specified.
    """
    cdef:
        int Na = len(axis)
        int Ni = len(input_rhs_indices)
        int No = len(output_rhs_indices)
        int i, o, j
        complex_t denom
        Parameter f = sim.model.fsig.f
        bint cast_out = False
        DetectorWorkspace dws
        dict other_outputs = None

    if out is None:
        out = np.zeros((Na, Ni, No), dtype=np.complex128)
        cast_out = True
    else:
        assert(out.shape[0] == Ni)
        assert(out.shape[1] == Na)
        assert(out.shape[2] == No)

    if (fsig_independant_outputs is not None) or (fsig_dependant_outputs is not None):
        other_outputs = {}

    # We'll be making our own RHS inputs for this simulation
    sim.signal.manual_rhs = True
    cdef double ifsig = sim.model_settings.fsig

    for j in range(Na):
        f.set_double_value(axis[j])
        sim.model_settings.fsig = axis[j]
        sim.signal.refill()
        # For each output that is fsig independant get and store the output
        if fsig_independant_outputs:
            for dws in fsig_independant_outputs:
                other_outputs[dws.oinfo.name] = dws.get_output()

        for i in range(Ni):
            sim.signal.clear_rhs()
            sim.signal.set_source_fast_2(
                input_rhs_indices[i], 1 * input_scaling[i]
            )
            sim.signal.solve()
            if not compute_open_loop:
                for o in range(No):
                    out[j][i][o] = sim.signal.out_view[output_rhs_indices[o]]

                    # scale output
                    out[j][i][o] = out[j][i][o] * output_scaling[o]
            else:
                for o in range(No):
                    out[j][i][o] = sim.signal.out_view[output_rhs_indices[o]]

                    if input_rhs_indices[i] == output_rhs_indices[o]:
                        out[j][i][o] = out[j][i][o] - 1 # remove injected signal
                        out[j][i][o] = out[j][i][o]/(1+out[j][i][o])
                    else:
                        # We can divide out the 1/(1-H) closed loop behaviours by
                        # using the coupling computed back into the same input node
                        denom = sim.signal.out_view[input_rhs_indices[i]] / input_scaling[i]
                        if denom.real == denom.imag == 0:
                            out[j][i][o] = 0
                        else:
                            out[j][i][o] = out[j][i][o] / denom

                    # scale output
                    out[j][i][o] = out[j][i][o] * output_scaling[o]

    sim.signal.manual_rhs = False
    sim.model_settings.fsig = ifsig
    f.set_double_value(ifsig)

    if other_outputs is not None:
        if cast_out:
            return np.array(out), other_outputs
        else:
            return out, other_outputs
    else:
        if cast_out:
            return np.array(out)
        else:
            return out


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.initializedcheck(False)
cpdef run_fsig_sweep2(
        CarrierSignalMatrixSimulation sim,
        double[::1] axis,
        long[::1] input_rhs_indices,
        long[::1] output_rhs_indices,
        double[::1] input_scaling,
        double[::1] output_scaling,
        complex_t[:, :, :, ::1] out,
        tuple fsig_independant_outputs = None,
        tuple fsig_dependant_outputs = None,
    ) noexcept:
    """ Runs a simulation to sweep over a signal frequency axis.
    It does this in an optimised way for multiple inputs and outputs.

    `run_fsig_sweep2` differs to `run_fsig_sweep` in that the inputs should be
    optical nodes. The transfer functions from each HOM at the input to every
    output will then be calculated. Outputs should be some readout signal nodes.

    Transfer functions for lower audio sides must be requested to conjugate, as
    internally the conjugate of the lower is solved for.

    Returns
    -------
    transfer_functions : array_like
        shape of (frequencies, outputs, inputs, HOMs)
    """
    cdef:
        int Nm = sim.signal.nhoms
        int Na = len(axis)
        int Ni = len(input_rhs_indices)
        int No = len(output_rhs_indices)
        int i, o, j, k
        Parameter f = sim.model.fsig.f
        bint cast_out = False
        DetectorWorkspace dws
        dict other_outputs = None

    if out is None:
        out = np.zeros((Na, No, Ni, Nm), dtype=np.complex128)
        cast_out = True
    else:
        assert(out.shape[0] == Ni)
        assert(out.shape[1] == Na)
        assert(out.shape[2] == No)
        assert(out.shape[3] == Nm)

    if fsig_independant_outputs or fsig_dependant_outputs:
        other_outputs = {}

    # We'll be making our own RHS inputs for this simulation
    sim.signal.manual_rhs = True
    cdef double ifsig = sim.model_settings.fsig

    for j in range(Na):
        f.set_double_value(axis[j])
        sim.model_settings.fsig = axis[j]
        sim.signal.refill()
        # For each output that is fsig independant get and store the output
        if fsig_independant_outputs:
            for dws in fsig_independant_outputs:
                other_outputs[dws.oinfo.name] = dws.get_output()

        for i in range(Ni):
            for k in range(Nm):
                sim.signal.clear_rhs()
                # Loop over each mode at this node
                sim.signal.set_source_fast_2(
                    input_rhs_indices[i] + k, 1 * input_scaling[i]
                )
                sim.signal.solve()
                for o in range(No):
                    out[j][o][i][k] = sim.signal.out_view[output_rhs_indices[o]]
                    # scale output
                    out[j][o][i][k] = out[j][o][i][k] * output_scaling[o]

    out /= np.sqrt(2) # normalise for the correct amplitude
    sim.signal.manual_rhs = False
    sim.model_settings.fsig = ifsig
    f.set_double_value(ifsig)

    if other_outputs is not None:
        if cast_out:
            return np.array(out), other_outputs
        else:
            return out, other_outputs
    else:
        if cast_out:
            return np.array(out)
        else:
            return out


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.initializedcheck(False)
cpdef run_fsig_sweep3(
        CarrierSignalMatrixSimulation sim,
        double[::1] axis,
        long[::1] input_rhs_indices,
        long[::1] output_rhs_indices,
        double[::1] input_scaling,
        double[::1] output_scaling,
        complex_t[:, :, :, :, ::1] out,
        tuple fsig_independant_outputs = None,
        tuple fsig_dependant_outputs = None,
    ) noexcept:
    """ Runs a simulation to sweep over a signal frequency axis.
    It does this in an optimised way for multiple inputs and outputs.

    `run_fsig_sweep3` differs to `run_fsig_sweep` in that the input and output nodes
    should be optical nodes. The transfer functions from each HOM at the input to every
    output will then be calculated.

    Transfer functions for lower audio sides must be requested to conjugate, as
    internally the conjugate of the lower is solved for.

    Returns
    -------
    transfer_functions : array_like
        shape of (frequencies, outputs, inputs, HOMs, HOMs)
    """
    cdef:
        int Nm = sim.signal.nhoms
        int Na = len(axis)
        int Ni = len(input_rhs_indices)
        int No = len(output_rhs_indices)
        int i, o, j, k, l
        Parameter f = sim.model.fsig.f
        bint cast_out = False
        DetectorWorkspace dws
        dict other_outputs = None

    if out is None:
        out = np.zeros((Na, No, Ni, Nm, Nm), dtype=np.complex128)
        cast_out = True
    else:
        assert(out.shape[0] == Ni)
        assert(out.shape[1] == Na)
        assert(out.shape[2] == No)
        assert(out.shape[3] == Nm) # output nodes
        assert(out.shape[4] == Nm) # input nodes

    if fsig_independant_outputs or fsig_dependant_outputs:
        other_outputs = {}

    # We'll be making our own RHS inputs for this simulation
    sim.signal.manual_rhs = True
    cdef double ifsig = sim.model_settings.fsig

    for j in range(Na):
        f.set_double_value(axis[j])
        sim.model_settings.fsig = axis[j]
        sim.signal.refill()
        # For each output that is fsig independant get and store the output
        if fsig_independant_outputs:
            for dws in fsig_independant_outputs:
                other_outputs[dws.oinfo.name] = dws.get_output()

        for i in range(Ni):
            for k in range(Nm):
                sim.signal.clear_rhs()
                # Loop over each mode at this node
                sim.signal.set_source_fast_2(
                    input_rhs_indices[i] + k, 1 * input_scaling[i]
                )
                sim.signal.solve()
                for o in range(No):
                    for l in range(Nm):
                        # select output mode and scale output
                        out[j][o][i][l][k] = sim.signal.out_view[output_rhs_indices[o]+l] * output_scaling[o]

    # Do not need this 1/sqrt{2} scaling as we're just doing optical to optical
    #out /= np.sqrt(2) # normalise for the correct amplitude
    sim.signal.manual_rhs = False
    sim.model_settings.fsig = ifsig
    f.set_double_value(ifsig)

    if other_outputs is not None:
        if cast_out:
            return np.array(out), other_outputs
        else:
            return out, other_outputs
    else:
        if cast_out:
            return np.array(out)
        else:
            return out


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.initializedcheck(False)
def run_axes_scan(
        object state,
        tuple axes,
        tuple params,
        double[:] offsets,
        tuple out_shape,
        ArraySolution solution,
        object pre_step,
        object post_step,
        bint progress_bar = False,
        str progress_bar_desc = ""
    ):
    cdef:
        CarrierSignalMatrixSimulation sim = state.sim
        int Np = len(params)
        int No = len(offsets)
        int Na = len(axes)
        int Nos = len(out_shape)
        int i, step
        np.ndarray[double, ndim=1, mode='c'] narr
        double** ptr_axes = NULL
        int* ptr_axes_len = NULL
        PyObject** ptr_params = NULL
        bint mask_this_point = False
        int[::1] IDX = np.zeros(Nos, dtype=np.int32)
        int Ntot

        Parameter param

    if(not (Np == No == Na == Nos)):
        raise Exception("Param, offsets, axes, and out_shape lengths are not the same")

    for p in params:
        if p.datatype not in (float, np.float64):
            raise Exception(f"Can only vary parameters with datatype float, not {p.full_name} with {p.datatype}")

    try:
        # Can't have a memory view of typed ndarray apparently.
        # So here we check the axes are double c-continuous and
        # then save the double pointer
        ptr_axes = <double**> malloc(Na*sizeof(double*))
        if not ptr_axes:
            raise MemoryError()

        ptr_axes_len = <int*> malloc(Na * sizeof(int))
        if not ptr_axes_len:
            raise MemoryError()

        for i in range(Na):
            narr = <np.ndarray[double, ndim=1, mode='c']?> axes[i]
            if narr.size != out_shape[i]:
                raise Exception(f"Out shape[{i}]={out_shape[i]} is not the correct size for the axes[i]={narr.size}")

            ptr_axes[i] = &narr[0]
            ptr_axes_len[i] = narr.size

        # Then to get around some annoying python referencing and issues
        # with accessing cdefs of extension types in a memory view we
        # make an array of PyObjects
        ptr_params = <PyObject**> malloc(Np*sizeof(PyObject*))
        if not ptr_params:
            raise MemoryError()
        for i in range(Np):
            ptr_params[i] = <PyObject*>(<Parameter?>params[i])

        Ntot = np.prod(out_shape)

        if progress_bar:
            pbar = tqdm(range(Ntot), leave=False, desc=progress_bar_desc, disable=not finesse.config.show_progress_bars)
        else:
            pbar = None

        # Now iterate over the all the axes
        #for step in range(Ntot):
        #for idx in np.ndindex(*out_shape):
        for step in range(Ntot):
            for i in range(Np):
                (<Parameter>ptr_params[i]).set_double_value(ptr_axes[i][IDX[i]] + offsets[i])
            # ------------------------------------------------------
            # PRE STEP
            # ------------------------------------------------------
            if pre_step is not None:
                pre_step._do(state)
            # ------------------------------------------------------
            # DO STEP
            # ------------------------------------------------------
            mask_this_point = not sim.run_carrier()

            if not mask_this_point and sim.signal:
                sim.run_signal()

            if progress_bar:
                pbar.update()
            # ------------------------------------------------------
            # POST STEP
            # ------------------------------------------------------
            if mask_this_point:
                values_str = ""
                for i in range(Np):
                    param = <Parameter>ptr_params[i]
                    if param.__units is not None:
                        param_units = " " + param.__units
                    else:
                        param_units = ""

                    values_str += (
                        param.__full_name
                        + " = "
                        + str(ptr_axes[i][IDX[i]] + offsets[i])
                        + param_units
                    )
                    if i != Np - 1:
                        values_str += ", "

                LOGGER.error("Masking simulation outputs at: %s", values_str)

            if solution.update(step, mask_this_point) == -1:
                raise RuntimeError("Exception calling solution update")

            if post_step is not None:
                post_step._do(state)

            # ------------------------------------------------------

            # Increment the index vector
            for i in range(No):
                i = Nos-i-1
                IDX[i] += 1
                if IDX[i] >= ptr_axes_len[i]:
                    IDX[i] = 0
                else:
                    break

    finally:
        # This forces pbar to show, even when leave=False
        if progress_bar:
            pbar.refresh()
            pbar.close()
        if ptr_axes != NULL: free(ptr_axes)
        if ptr_axes_len != NULL: free(ptr_axes_len)
        if ptr_params != NULL: free(ptr_params)
