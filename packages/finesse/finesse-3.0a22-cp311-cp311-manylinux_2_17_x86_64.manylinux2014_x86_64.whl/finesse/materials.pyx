"""Material objects are a simple structure that contain commonly used
properties for calculations. By default this includes Fused Silica and
Silicon at 123K.

.. todo::

    At some point add in wavelenth and temperature dependence to these
    Material objects.
"""
cimport cython

@cython.auto_pickle(True)
cdef class Material(object):
    """"""
    def __init__(self, alpha, nr, dndT, kappa, emiss, poisson, E, rho, C, T):
        self.values.alpha   = alpha
        self.values.nr      = nr
        self.values.dndT    = dndT
        self.values.kappa   = kappa
        self.values.emiss   = emiss
        self.values.poisson = poisson
        self.values.E       = E
        self.values.T       = T
        self.values.C       = C
        self.values.rho     = rho

    @property
    def alpha(self):
        """Thermo expansion coefficient"""
        return self.values.alpha

    @property
    def nr(self):
        """Refractive index"""
        return self.values.nr

    @property
    def dndT(self):
        """Thermo refractive coefficient [K^-1]"""
        return self.values.dndT

    @property
    def kappa(self):
        """Thermal conductivity [Wm^-1]"""
        return self.values.kappa

    @property
    def emiss(self):
        """Emissitivity"""
        return self.values.emiss

    @property
    def poisson(self):
        """Poisson ratio"""
        return self.values.poisson

    @property
    def E(self):
        """Youngs Modulus [kg m^-3]"""
        return self.values.E

    @property
    def rho(self):
        """Density [kg m^-3]"""
        return self.values.rho

    @property
    def C(self):
        """Specific Heat [J kg^-1]"""
        return self.values.C

    @property
    def T(self):
        """The temperature materials properties are defined at [K]"""
        return self.values.T

FusedSilica = Material(
    0, # coefficient of linear expansion
    1,   # refractive Index
    0, # dn/dt
    0,   # Thermal Conductivity
    0,   # Emissivity
    0,   # Poisson ratio
    0, # Youngs Modulus
    0,   # density
    0,    # Specific heat
    0,    # reference temperature
)

FusedSilica = Material(
    5.5e-7, # coefficient of linear expansion
    1.45,   # refractive Index
    8.6E-6, # dn/dt
    1.38,   # Thermal Conductivity
    0.91,   # Emissivity
    0.17,   # Poisson ratio
    7.2e10, # Youngs Modulus
    2202,   # density
    772,    # Specific heat
    297,    # reference temperature
)

# Taken from Voyager GWINC
Silicon123K_sum = Material(
    1e-10,  # coefficient of linear expansion
    3.4,   # refractive Index @ 2um
    1e-4,  # dn/dt
    700,    # Thermal Conductivity
    0.7,    # Emissivity, https://www.sciencedirect.com/science/article/pii/S0017931019361289
    0.27,   # Poisson ratio
    155.8e9,# Youngs Modulus
    2329,   # density
    300,    # Specific heat
    123,    # reference temperature
)

CaF2_300K_2um = Material(
    18.5e-6,  # coefficient of linear expansion
    1.4239,   # refractive Index @ 2um
    -10e-6,   # dn/dt
    9.71,     # Thermal Conductivity
    0.88,     # Emissivity
    0.26,     # Poisson ratio
    75.8e9,   # Youngs Modulus
    3180,     # density
    854,      # Specific heat
    300,      # reference temperature
)

# Fused silica used for iLIGO
# reference CTE (NIST SRM  739)
Corning7940 = Material(
    4.869e-07,  # coefficient of linear expansio
    1.45,       # refractive Index
    9.6e-6,     # dn/dt
    1.367,      # Thermal Conductivity
    0.9,        # Emissivity
    0.167,      # Poisson ratio
    72.93E9,    # Youngs Modulus
    2220.00,    # density
    704.21,     # Specific heat
    293.15      # reference temperature
)

# Suprasil ref
# n, coefficient of linear expansion from data sheet
# https://www.heraeus.com/media/media/hca/doc_hca/products_and_solutions_8/optics/Data_and_Properties_Optics_fused_silica_EN.pdf
suprasil3002_2um = Material(
    5.9e-7,  # coefficient of linear expansion
    1.499,       # refractive Index
    8.89e-6,     # dn/dt
    1.38,      # Thermal Conductivity
    0.9,        # Emissivity
    0.17,      # Poisson ratio
    73.1E9,    # Youngs Modulus
    2203,    # density
    964,     # Specific heat
    293.15      # reference temperature
)

BK7_2um = Material(
    7.1e-6,  # coefficient of linear expansion
    1.4946,       # refractive Index
    8.94E-7,     # dn/dt
    1.114,      # Thermal Conductivity
    0.9,        # Emissivity
    0.206,      # Poisson ratio
    82e9,    # Youngs Modulus
    2510,    # density
    858,     # Specific heat
    293.15      # reference temperature
)

#   zblan reference   Zhu X., Peyghambarian N., High-Power ZBLAN Glass Fiber Lasers: Review and Prospect, 2010
ZBLAN_2um = Material(
    17.2e-6,  # coefficient of linear expansion
    1.4956,       # refractive Index
    -14.75e-6,     # dn/dt
    0.628,      # Thermal Conductivity
    0.9,        # Emissivity
    0.206,      # Poisson ratio
    58.5e9,    # Youngs Modulus
    4330,    # density
    151,     # Specific heat
    293.15      # reference temperature
)
