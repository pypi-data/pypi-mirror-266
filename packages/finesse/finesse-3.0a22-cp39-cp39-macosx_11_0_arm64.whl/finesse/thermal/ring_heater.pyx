"""Ring heater thermal equations for cylindrical mirrors

Equations all based on :cite:`Ramette:16`:

    J. Ramette, M. Kasprzack, A. Brooks, C. Blair,
    H. Wang, and M. Heintze, "Analytical model for ring heater
    thermal compensation in the Advanced Laser Interferometer
    Gravitational-wave Observatory," Appl. Opt.  55, 2619-2625 (2016).
"""

from scipy.special import iv
from scipy.optimize.cython_optimize cimport brentq

import numpy as np
cimport numpy as np

cdef double SIGMA_F = 5.6710e-8

cdef extern from "math.h":
    double tan(double arg) nogil

cdef struct f_args:
    double tau
    double h_2a

# find solutions of Eq 11
cdef double f_v_m(double x, void *args) noexcept:
    cdef f_args *fargs = <f_args*>args
    return x + fargs.tau * tan(x * fargs.h_2a)

cdef double f_u_m(double x, void *args) noexcept:
    cdef f_args *fargs = <f_args*>args
    return x - fargs.tau * 1/tan(x * fargs.h_2a)

cpdef zeros_v_m(double a, double h, double tau, int m_max, double accuracy) noexcept:
    """Compute the roots of the equation

    .. math::
        v_m + \tau tan(v_m h/(2a)) = 0

    Parameters
    ----------
    a : float
        Mirror radius [m]
    h : float
        Mirror thickness [m]
    tau : float
        Reduced radiation constant
    n_max : int
        Max bessel order to compute up to
    accuracy : double
        absolute error on zero finding brentq algorithm

    Returns
    -------
    v_m : array_like
        Array of m_max zeros
    """
    cdef:
        Py_ssize_t n
        double start = 0
        double dx = 0
        f_args args

    if tau == 0:
        raise RuntimeError("tau should be > 0")

    args.tau = tau
    args.h_2a = h/(2*a)

    cdef double[::1] zeros = np.zeros((m_max, ), dtype=np.float64)
    dx = np.pi/h*a # separation between each tan asymptote
    # the tan function needs an ever increasing offset to push
    # it past the infinity point back to a -inf where it looks
    # for a root above that x
    offset = 1e-15
    for n in range(0, m_max):
        start = dx*(2*n+1)
        while f_v_m(start+offset, &args) > 0:
            offset *= 10
        zeros[n] = brentq(f_v_m, start+offset, dx*(2*n+2), <f_args *> &args, accuracy, 0, 1000000, NULL)

    return np.asarray(zeros)


cpdef zeros_u_m(double a, double h, double tau, int m_max, double accuracy) noexcept:
    """Compute the roots of the equation

    .. math::
        u_m - \tau \cot(u_m h/(2a)) = 0

    Parameters
    ----------
    a : float
        Mirror radius [m]
    h : float
        Mirror thickness [m]
    tau : float
        Reduced radiation constant
    n_max : int
        Max bessel order to compute up to
    accuracy : double
        absolute error on zero finding brentq algorithm

    Returns
    -------
    u_m : array_like
        Array of m_max zeros
    """
    cdef:
        Py_ssize_t n
        double start = 0
        double end = 0
        double dx = 0
        f_args args

    if tau == 0:
        raise RuntimeError("tau should be > 0")

    args.tau = tau
    args.h_2a = h/(2*a)

    cdef double[::1] zeros = np.zeros((m_max, ), dtype=np.float64)
    dx = np.pi/h*a # separation between each tan asymptote
    # floating point errors in tan mean there has to be slight
    # offsets applied to the start and end bounds to ensure
    # a root is bound
    start_offset = 1e-15
    end_offset = 1e-15
    for n in range(0, m_max):
        start = dx*(2*n)
        end = dx*2*(n+1)
        while f_u_m(start+start_offset, &args) >= 0:
            start_offset *= 10
        while f_u_m(end-end_offset, &args) <= 0:
            end_offset *= 10
        zeros[n] = brentq(f_u_m, start+start_offset, end-end_offset, <f_args *> &args, accuracy, 0, 1000000, NULL)

    return np.asarray(zeros)


def substrate_temperature(r, z, a, b, c, h,  material, T_ext=293.15, m_max=10, root_accuracy=1e-12):
    """Computes the substrate temperature distribution per
    Watt absorbed ring heater power.

    Parameters
    ----------
    r : array_like
        Radial vector [m]
    z : array_like
        Longitudinal vector [m]
    a : float
        Mirror radius [m]
    b : float
        Ring heater lower boundary relative to center [m]
    c : float
        Ring heater upper boundary relative to center [m]
    h : float
        Mirror thickness [m]
    material : Material
        Mirror substrate material, see :py:mod:`finesse.material`
    T_ext : float, optional
        External temperature surrounding mirror
    m_max : int, optional
        Number of zeros to find, i.e. analytic order
    root_accuracy: float, optional
        Accuracy of root finding

    Returns
    -------
    T_rh_per_W : array_like
        2D Array of temperature distribution over [r, z]

    Notes
    -----
    Typo for A_m terms in manuscript, sin terms are functions of
    u_m, not v_m. See :cite:`Ramette:16`.
    """
    tau = 4 * material.emiss * SIGMA_F * T_ext**3 * a / material.kappa
    v_m = zeros_v_m(a, h, tau, m_max, root_accuracy)
    u_m = zeros_u_m(a, h, tau, m_max, root_accuracy)
    factor = 2 / (material.kappa*2*np.pi*a*(c-b))

    v_m_c_a = v_m * c / a
    v_m_b_a = v_m * b / a
    u_m_c_a = u_m * c / a
    u_m_b_a = u_m * b / a

    u_m_h_a = u_m * h / a
    v_m_h_a = v_m * h / a
    u_m_z_a = u_m * z[:, np.newaxis] / a
    u_m_r_a = u_m * r[:, np.newaxis] / a
    v_m_z_a = v_m * z[:, np.newaxis] / a
    v_m_r_a = v_m * r[:, np.newaxis] / a

    # Typo in paper for A_m, numerators sin terms are functions of u_m NOT v_m
    A_m = factor * (np.sin(u_m_c_a) - np.sin(u_m_b_a))
    A_m /= (u_m_h_a + np.sin(u_m_h_a)) * (iv(1, u_m) * u_m + iv(0, u_m)*tau) / a # Eq 18

    B_m = factor * (-np.cos(v_m_c_a) + np.cos(v_m_b_a))
    B_m /= (v_m_h_a - np.sin(v_m_h_a)) * (iv(1, v_m) * v_m + iv(0, v_m)*tau) / a # Eq 18

    T_ss_per_W = (A_m * np.cos(u_m_z_a)[:, np.newaxis] * iv(0, u_m_r_a) # Eq 9
            + B_m * np.sin(v_m_z_a)[:, np.newaxis] * iv(0, v_m_r_a)).sum(2) # Eq 10

    return T_ss_per_W


def thermal_lens(r, a, b, c, h, material, T_ext=293.15, m_max=10, root_accuracy=1e-12):
    """Computes the substrate thermal lens per
    Watt absorbed ring heater power.

    Parameters
    ----------
    r : array_like
        Radial vector [m]
    a : float
        Mirror radius [m]
    b : float
        Ring heater lower boundary relative to center [m]
    c : float
        Ring heater upper boundary relative to center [m]
    h : float
        Mirror thickness [m]
    material : Material
        Mirror substrate material, see :py:mod:`finesse.material`
    T_ext : float, optional
        External temperature surrounding mirror
    m_max : int, optional
        Number of zeros to find, i.e. analytic order
    root_accuracy: float, optional
        Accuracy of root finding

    Returns
    -------
    Z_rh_per_W : array_like
        1D radial vector of optical path difference from
        propagating through substrate.

    Notes
    -----
    Typo for A_m terms in manuscript, sin terms are functions of
    u_m, not v_m. See :cite:`Ramette:16`.
    """
    tau = 4 * material.emiss * SIGMA_F * T_ext**3 * a / material.kappa
    u_m = zeros_u_m(a, h, tau, m_max, root_accuracy)
    factor = 2 / (material.kappa*2*np.pi*a*(c-b))

    u_m_c_a = u_m * c / a
    u_m_b_a = u_m * b / a
    u_m_h_a = u_m * h / a
    u_m_r_a = u_m * r[:, np.newaxis] / a

    # Typo in paper for A_m, numerators sin terms are functions of u_m NOT v_m
    A_m = factor * (np.sin(u_m_c_a) - np.sin(u_m_b_a))
    A_m /= (u_m_h_a + np.sin(u_m_h_a)) * (iv(1, u_m) * u_m + iv(0, u_m)*tau) / a # Eq 18
    # This result isn't in the paper direct but found by integrating Eq.9 over z = -h/2 -> h/2
    # Eq. 10 drops out due to sin asymmetry
    Z_ss_per_W = (material.dndT * (2*a/u_m * A_m * np.sin(u_m/a*h/2)) * iv(0, u_m_r_a)).sum(1)
    return Z_ss_per_W - abs(Z_ss_per_W).min()
