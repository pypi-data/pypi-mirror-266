cimport numpy as np

cpdef enum ParameterState:
    Numeric = 1,
    Unresolved = 2,
    Symbolic = 3,
    NONE =  4


cdef class Parameter:
    cdef:
        object __value
        double __cvalue
        type __datatype
        object __datatype_cast # function to cast value into __datatype
        str __units
        str __name
        str __full_name
        str __description
        bint __is_tunable
        object __weakref__
        type __owner_type
        public object __owner
        public bint _locked
        dict __external_setters # If set the value of this parameter is being set by some other external element and should not be user settable
        readonly ParameterState state
        readonly bint is_geometric
        object __validator
        bint __resolving
        bint __changeable_during_simulation
        bint __disable_state_type_change

        # TODO: (jwp) moved from GeometricParameter as temporary solution, see parameter.pyx
        readonly bint is_nr

    cdef __cdeepcopy__(self, Parameter new, dict memo) noexcept
    cdef __update_state(self) noexcept
    cdef bint _is_changing(self) noexcept
    cdef _get_value(self) noexcept
    cdef _set_value(self, value) noexcept
    cdef int set_double_value(self, double value) except -1


cdef class GeometricParameter(Parameter):
    cdef void update_abcd_matrices(self) noexcept
