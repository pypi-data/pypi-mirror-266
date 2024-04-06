cimport cython

# At some point we could make these all arrays and have some
# temperature dependence that could be interpolated
cdef struct material:
    double alpha   # coefficient of linear expansion
    double nr      # refractive Index
    double dndT    # dn/dt
    double kappa   # Thermal Conductivity
    double emiss   # Emissivity
    double poisson # Poisson ratio
    double E       # Youngs Modulus
    double rho     # Density
    double C       # Specific Heat
    double T       # reference temperature


@cython.auto_pickle(True)
cdef class Material(object):
    cdef:
        material values
