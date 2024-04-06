from cpython.ref cimport PyObject

#cdef struct cy_expr

from .cyexpr cimport (
    cy_expr,
    cy_expr_new,
    cy_expr_init,
    cy_expr_free,
    cy_expr_eval,
)

cdef class BaseCValues:
    cdef:
        Py_ssize_t N
        double **ptr
        tuple params

    cdef setup(self, tuple params, Py_ssize_t data_size, double** data_start) noexcept
    cdef get_param_ptr(self, unicode name, double**ptr) noexcept


cdef class ElementWorkspace:
    cdef:
        readonly bint _unique_element # Only a single element of this type can be added to a model
        readonly object owner # Model element that owns this workspace
        public int owner_id # Owner's id for this particular simualation
        readonly object values
        bint is_c_values
        type type_c_values
        int num_changing_parameters
        PyObject** chprm
        double** chprm_target
        cy_expr** chprm_expr # Compiled changing symbolic expressions array
        bint first

    cpdef int compile_cy_exprs(self) except -1
    cpdef update_parameter_values(self) noexcept
