from libc.stdlib cimport free, calloc
from libc.string cimport memcpy
from cpython.ref cimport Py_XINCREF, Py_XDECREF

from collections import defaultdict, ChainMap
import weakref
from copy import deepcopy
import logging

from .parameter cimport (
    Parameter,
    ParameterState,
    GeometricParameter,
)
from .exceptions import ModelParameterDefaultValueError, ContextualValueError
from .utilities.tables import Table
from .symbols import Symbol
from .freeze import canFreeze

LOGGER = logging.getLogger(__name__)


@canFreeze
class ModelElement:
    """Base for any object which can be an element of a :class:`.Model`.

    When added to a model it will attempt to call the method `_on_add` so that the element can do
    some initialisation if required.

    Parameters
    ----------
    name : str
        Name of newly created model element.
    """

    # A global dictionary to keep a record of all the declared
    # model parameters, validators, etc.
    _param_dict = defaultdict(list)
    _validators = defaultdict(dict)
    _setters = defaultdict(dict)
    _default_parameter_name = dict()
    _unique_element = False
    # Info parameters.
    _info_param_dict = defaultdict(dict)

    def __new__(cls, name, *args, **kwargs):
        instance = super(ModelElement, cls).__new__(cls)
        instance._unfreeze()
        instance._params = []
        instance._info_params = instance._info_param_dict[cls]
        instance._ModelElement__name = name
        instance._unique_element = bool(cls._unique_element)
        instance._ModelElement__model = None

        # Loop through each of the parameters that have been defined
        # in the class and instantiate an object to represent them
        # for this instance of the object
        for pinfo in instance._param_dict[cls]:
            if pinfo.is_geometric:
                p = GeometricParameter(pinfo, instance)
            else:
                p = Parameter(pinfo, instance)
            setattr(instance, f"__param_{pinfo.name}", p)
            instance._params.append(p)

        return instance

    def __init__(self, name):
        from finesse.utilities import check_name

        self._params_changing = None
        self._params_evald = None
        self._legacy_script_line_number = 0

        try:
            self.__name = check_name(name)
        except ValueError as e:
            raise ContextualValueError(
                {"name": name},
                "can only contain alphanumeric and underscore characters"
            )

        self._add_to_model_namespace = True
        self._namespace = (".", )

    def __str__(self):
        params = {param.name: str(param.value) for param in self.parameters}
        info_params = {param: str(getattr(self, param)) for param in self._info_params}
        values = [repr(self.name)] + [f"{k}={v}" for k, v in ChainMap(info_params, params).items()]
        return f"{self.__class__.__name__}({', '.join(values)})"

    def __repr__(self):
        return "❮'{}' @ {} ({})❯".format(
            self.name, hex(id(self)), self.__class__.__name__
        )

    def __deepcopy__(self, memo):
        new = object.__new__(type(self))
        memo[id(self)] = new

        # For debugging what causes deepcopy errors
        # try:
        #     for key in self.__dict__:
        #         new.__dict__[key] = deepcopy(self.__dict__[key], memo)
        # except Exception:
        #     print("ERROR on deepcopy", key)
        #     raise

        new.__dict__.update(deepcopy(self.__dict__, memo))

        # Manually update the weakrefs to be correct
        new.__model = weakref.ref(memo[id(self.__model())])
        return new

    def info(self):
        """Element information.

        Returns
        -------
        str
            The formatted info.
        """
        params = str(self.parameter_table())
        info_params = self.info_parameter_table()

        msg = f"{self.__class__.__name__} {self.name}\n"
        msg += "\nParameters:\n"
        if params is not None:
            msg += params
        else:
            msg += "n/a\n"

        if info_params is not None:
            msg += "\nInformation:\n"
            msg += str(self.info_parameter_table())

        return msg

    def parameter_table(self):
        """Model parameter table.

        Returns
        -------
        finesse.utilities.Table
            The formatted parameter info table.
        None
            If there are no parameters.
        """

        if not self.parameters:
            return

        table = [["Description", "Value"]]

        # Loop in reverse so we can keep the natural order of each element's parameters in its
        # corresponding model parameter class decorators.
        table += [
            [field.description, field]
            for field in reversed(self.parameters)
        ]

        return Table(table, headerrow = True, headercolumn = False)

    def info_parameter_table(self):
        """Info parameter table.

        This provides a table with useful fields in addition to those contained in
        :meth:`.parameter_table`.

        Parameters
        ----------

        Returns
        -------
        str
            The formatted extra info table.
        None
            If there are no info parameters.
        """

        if not self._info_params:
            return

        table = [["Description", "Value"]]

        # Loop in reverse so we can keep the natural order of each element's parameters in its
        # corresponding info parameter class decorators.
        table += [
            [description, getattr(self, name)]
            for name, (description, _) in reversed(self._info_params.items())
        ]

        return Table(table, headerrow=True, headercolumn=False)

    @property
    def parameters(self):
        """Returns a list of the parameters available for this element"""
        return self._params.copy()

    @property
    def default_parameter_name(self):
        """The default parameter to assume when the component is directly referenced.

        This is used for example in kat script when the component is directly referenced in an
        expression, instead of the model parameter, e.g. &l1 instead of &l1.P.

        Returns
        -------
        str
            The name of the default model parameter.

        None
            If there is no default.
        """
        return self._default_parameter_name.get(self.__class__)

    @property
    def name(self):
        """Name of the element.

        Returns
        -------
        str
            The name of the element.
        """
        return self.__name

    @property
    def ref(self):
        """
        Reference to the default model parameter, if set.

        Returns
        -------
        :class:`.ParameterRef`
            Reference to the default model parameter, if set.

        Raises
        ------
        ValueError
            If there is no default model parameter set for this element.
        """
        if self.default_parameter_name is None:
            raise ModelParameterDefaultValueError(self)

        return getattr(self, self.default_parameter_name).ref

    @property
    def _model(self):
        """
        Internal reference to the model this element has been added to.

        Raises
        ------
        ComponentNotConnected when not connected
        """
        from finesse.exceptions import ComponentNotConnected

        if self.__model is None:
            raise ComponentNotConnected(f"{self.name} is not connected to a model")
        else:
            return self.__model()

    @property
    def has_model(self):
        """Returns true if this element has been associated with a Model."""
        return self.__model is not None

    def _set_model(self, model):
        """
        A :class:`.Model` instance calls this to associate itself
        with the element.

        .. note::
            This method should never be called by the user, it should
            only be called internally by the :class:`.Model` class.

        Parameters
        ----------
        model : :class:`.Model`
            The model to associate with this element.

        Raises
        ------
        Exception
            If the model is already set for this element.
        """
        if model is not None and self.__model is not None:
            raise Exception("Model is already set for this element")
        if model is None:
            # The element has been removed from a model
            self.__model = None
        else:
            self.__model = weakref.ref(model)

    def _reset_model(self, new_model):
        """Resets the model that this element is associated with. Note, this should
        not be used in normal coding situations. It should only be used when writing
        new elements that override the `__deepcopy__` method.
        """
        self.__model = weakref.ref(new_model)

    def _setup_changing_params(self):
        """For any parameter that has been set to be changing during a simulation
        this method will store them and their evaluated values in the set `self._params_changing`
        and the dict `self._params_evald`.
        """
        # N.B. Decorators are evaluated from inside - out, so to make the order returned here match
        # the order defined, we must reverse self.parameters
        self._params_changing = set(
            p for p in reversed(self.parameters) if p.is_changing
        )
        try:
            self._params_evald = {}
            for p in reversed(self.parameters):
                self._params_evald[p.name] = (p.value.eval() if hasattr(p.value, "eval") else p.value)
        except ArithmeticError as ex:
            ex.args = (f"Error evaluating {p}: {str(ex)}",)
            raise ex

    def _clear_changing_params(self):
        """Sets the set `self._params_changing` and the dict `self._params_evald` to None
        after a simulation has completed."""
        self._params_changing = None
        self._params_evald = None

    def _eval_parameters(self):
        """
        Only call this methods when the model is built. It is optimised
        for returned changed parameter values in this state.

        To get a dictionary of parameter values in other cases use:

        >>>> values = {p.name:p.eval() for p in element.parameters}

        Returns
        -------
        params : dict(str:float)
            Dictionary of parameter values
        params_changing : set(str)
            A set of parameter names which are changing.
        """
        # Now we know which are evaluable so no need for repeated checks
        # Also reduce memory bashing creating a ton of dictionaries and
        # reuse just one.
        for p in self._params_changing:
            self._params_evald[p.name] = p.eval()

        return self._params_evald, self._params_changing


class ElementValues:
    """Standard Python object which is used to store an Elements Parameter values.
    This is used in the default case where no optimised C class is provided."""
    pass


cdef class BaseCValues:
    """Base class that elements should use for storing their parameter
    values. This contains a generic method for storing a pointers to the
    double parameter values, which is intialised using `setup()`.

    Each Parameter of an element should result in a double. This won't handle
    any other types of data.
    """
    def __cinit__(self):
        self.ptr = NULL
        self.N = 0

    cdef setup(self, tuple params, Py_ssize_t data_size, double** data_start) noexcept:
        """Allocates the memory needed to store double values for the requested parameters.

        Examples
        --------
        An array of pointers to the double variables where each parameter should be copied across
        to.

        ctypedef (double*, double*) ptr_tuple_2 # data type of double points

        cdef class OpticalBandpassValues(BaseCValues):
            def __init__(self):
                cdef ptr_tuple_2 ptr = (&self.fc, &self.bandwidth) # array of ptrs to store parameter values at
                cdef tuple params = ("fc", "bandwidth") # names that match up in order with pointers
                self.setup(params, sizeof(ptr), <double**>&ptr) # call setup

        Parameters
        ----------
        params : tuple
            Tuple of Parameter names (case-sensitive) that an element has and needs to be stored in C values
        data_size : unsigned long
            number of double* pointers (or number of parameters)
        data_start : double**
            Pointer to array of double pointers where each parameter value should be stored
        """
        if self.ptr != NULL:
            raise ValueError("Memory already allocated")
        if data_start == NULL:
            raise ValueError("data_start == NULL")

        self.params = params
        self.N = data_size//sizeof(double)

        if len(self.params) != self.N:
            raise ValueError("Tuple of parameters and length of double pointers does not match")

        self.ptr = <double**> calloc(self.N, sizeof(double*))

        if not self.ptr:
            raise MemoryError()

        memcpy(self.ptr, data_start, data_size)

    def __dealloc__(self):
        if self.ptr != NULL:
            free(self.ptr)
            self.ptr = NULL

    cdef get_param_ptr(self, unicode name, double**ptr) noexcept:
        """Get a C pointer to where an elements parameter values should be stored.

        Parameters
        ----------
        name : unicode
            Name of the parameter
        ptr : double*
            Pointer to where the parameter pointer should be stored
        """
        if self.ptr == NULL:
            raise ValueError("Value storage pointers not set")
        if ptr == NULL:
            raise ValueError("ptr is NULL")

        idx = self.params.index(name)
        if self.ptr[idx] == NULL:
            raise ValueError(f"Pointer to {name} double is NULL")

        ptr[0] = self.ptr[idx]


cdef class ElementWorkspace:
    """
    This is the most basic workspace for a model element. It keeps track of the owner element and
    its parameter values in the `self.values` object.
    """
    def __cinit__(self, *args, **kwargs):
        self.num_changing_parameters = 0
        self.chprm = NULL
        self.chprm_target = NULL
        self.chprm_expr = NULL
        self.owner_id = -1
        self.first = True

    def __init__(self, object owner, object values=None):
        cdef:
            Parameter p
            int i
        self.owner = owner

        if values is None:
            self.values = ElementValues()
            self.type_c_values = None
            self.is_c_values = False
        else:
            if not isinstance(values, BaseCValues):
                raise Exception("Values object should be a derivative of BaseCValues")

            self.values = values
            self.type_c_values = type(values)
            self.is_c_values = True

            # Here we setup for fast parameter setting by storing
            # the pyobject pointers to Parameters and also a double
            # pointer to the value

            # Make sure that numeric parameters come before symbolic
            # parameters so that the latter get eval'd to the correct
            # value when calling cy_expr_eval
            numeric_params = []
            symbolic_params = []
            for p in owner.parameters:
                if p.is_changing:
                    self.num_changing_parameters += 1
                    if p.state == ParameterState.Symbolic:
                        symbolic_params.append(p)
                    else:
                        numeric_params.append(p)

            params = numeric_params + symbolic_params
            if self.num_changing_parameters > 0:
                if self.chprm != NULL or self.chprm_target != NULL or self.chprm_expr != NULL:
                    raise MemoryError()

                self.chprm = <PyObject**> calloc(self.num_changing_parameters, sizeof(PyObject*))
                if not self.chprm:
                    raise MemoryError()

                self.chprm_target = <double**> calloc(self.num_changing_parameters, sizeof(double*))
                if not self.chprm_target:
                    raise MemoryError()

                self.chprm_expr = <cy_expr**> calloc(self.num_changing_parameters, sizeof(cy_expr*))
                if not self.chprm_expr:
                    raise MemoryError()

                i = 0
                for p in params:
                    if p.is_changing:
                        if p.state == ParameterState.Symbolic:
                            self.chprm_expr[i] = cy_expr_new()

                        self.chprm[i] = <PyObject*>p
                        Py_XINCREF(self.chprm[i])
                        (<BaseCValues>self.values).get_param_ptr(p.name, &self.chprm_target[i])
                        i += 1
                        # Stop this changing parameter from changing the type of
                        # variable it is (See #476). Problem comes about when a
                        # non-symbolic changes to a symbolic after this code has
                        # run, so then things like cy_expr_new have not been run.
                        p.__disable_state_type_change = True

    cpdef int compile_cy_exprs(self) except -1:
        if not self.num_changing_parameters:
            return 0

        for i in range(self.num_changing_parameters):
            if (<Parameter>self.chprm[i]).state == ParameterState.Symbolic:
                try:
                    # occasionally expressions simplify and become a constant
                    # so need to check
                    expr = (<Parameter>self.chprm[i]).value.expand_symbols().eval(keep_changing_symbols=True)
                    if isinstance(expr, Symbol):
                        if cy_expr_init(
                            self.chprm_expr[i], expr
                        ) == -1:
                            return -1
                except:
                    raise RuntimeError(f"Issue compiling cython expression :: {(<Parameter>self.chprm[i]).full_name}={(<Parameter>self.chprm[i]).value}")
        return 0

    cpdef update_parameter_values(self) noexcept:
        """Updates the `self.values` container which holds the latest values
        of this elements parameters.
        """
        cdef unicode p

        if self.first or not self.is_c_values:
            # First go just fill everything.
            # This is fairly slow but robust for any python object...
            vals, _ = self.owner._eval_parameters()
            for p in vals:
                if vals[p] is not None:
                    setattr(self.values, p, vals[p])
                else:
                    setattr(self.values, p, 0)
            self.first = False

        elif self.num_changing_parameters > 0:
            # Here we do some lower level setting of parameters using pointers
            # to the workspace.value.parameter double variable to speed things up
            for i in range(self.num_changing_parameters):
                if self.chprm_target[i] == NULL or self.chprm[i] == NULL:
                    raise MemoryError()

                if (<Parameter>self.chprm[i]).state == ParameterState.Numeric:
                    self.chprm_target[i][0] = (<Parameter>self.chprm[i]).__cvalue
                elif (<Parameter>self.chprm[i]).state == ParameterState.NONE:
                    self.chprm_target[i][0] = 0 # maybe should be NaN?
                elif (<Parameter>self.chprm[i]).state == ParameterState.Symbolic:
                    self.chprm_target[i][0] = cy_expr_eval(self.chprm_expr[i])
                    # Make sure __cvalue of symbolic parameters get updated too so that
                    # anything that relies on address of this uses correct value
                    (<Parameter>self.chprm[i]).__cvalue = self.chprm_target[i][0]
                else:
                    raise ValueError("Parameter state was unexpected")

    def __dealloc__(self):
        errors = []
        if self.num_changing_parameters > 0:
            for i in range(self.num_changing_parameters):
                if (<Parameter>self.chprm[i]).state == ParameterState.Symbolic:
                    cy_expr_free(self.chprm_expr[i])

                if self.chprm[i] == NULL:
                    errors.append(i)
                else:
                    Py_XDECREF(self.chprm[i])

            if self.chprm != NULL:
                free(self.chprm)
                self.chprm = NULL
            if self.chprm_expr != NULL:
                free(self.chprm_expr)
                self.chprm_expr = NULL
            if self.chprm_target != NULL:
                free(self.chprm_target)
                self.chprm_target = NULL

            if len(errors) > 0:
                raise MemoryError(f"unexpected self.chprm indices {errors} were NULL")

    def __repr__(self):
        try:
            return "❮'{}' @ {} ({})❯".format(
                self.owner.name, hex(id(self)), self.__class__.__name__
            )
        except:
            return super().__repr__()
