"""Collection of ABCD functions for standard optical components."""
import numpy as np
from finesse.exceptions import TotalReflectionError


def space(L, nr=1):
    """Propagation along a length `L`

    Parameters
    ----------
    L : float
        Length in metres
    nr : float
        refractive index of medium
    """
    return np.array([[1.0, L / nr], [0.0, 1.0]])


def lens(f):
    """Propagation through a thin lens.

    Parameters
    ----------
    f : float
        Focal lenth of thin lens in metres
    """
    return np.array([[1.0, 0.0], [-1.0 / f, 1.0]])


def mirror_refl(Rc, nr=1):
    """Reflection from a curved surface.

    Parameters
    ----------
    Rc : float
        Radius of curvature of the surface being reflected from.
        A positive Rc means the surface appears concave to the incident
        beam.
    nr : float
        refractive index of medium in which the reflection occurs
    """
    return np.array([[1.0, 0.0], [-2 * nr / Rc, 1.0]])


def mirror_trans(Rc, nr1=1, nr2=1):
    """Transmission through a curved surface.

    Parameters
    ----------
    Rc : float
        Radius of curvature of the surface being reflected from.
        A positive Rc means the surface appears concave to the incident
        beam.
    nr1 : float
        refractive index of medium the beam starts in
    nr2 : float
        refractive index of medium the beam ends up in
    """
    return np.array([[1.0, 0.0], [(nr2 - nr1) / Rc, 1.0]])


def beamsplitter_refl(Rc, alpha, nr1=1, nr2=1, direction="x"):
    """Reflection from a curved surface at an angle of incidence.

    Parameters
    ----------
    Rc : float
        Radius of curvature of the surface being reflected from.
        A positive Rc means the surface appears concave to the incident
        beam.
    alpha : float
        Angle of incidence in degrees
    nr1 : float
        refractive index of medium the reflection occurs in
    nr2 : float
        refractive index of medium on the other side of the surrface
    direction : str
        Which plane this reflection occurs in, either `x` or `y`.
    """
    alpha1 = np.radians(alpha)

    A = 1.0
    D = 1.0

    if direction == "x":
        C = -2 * nr1 / (Rc * np.cos(alpha1))
    else:
        C = -2 * nr1 * np.cos(alpha1) / Rc

    return np.array([[A, 0.0], [C, D]])


def beamsplitter_trans(Rc, alpha, nr1=1, nr2=1, direction="x"):
    """Transmission through a curved surface at an angle of incidence.

    Parameters
    ----------
    Rc : float
        Radius of curvature of the surface being reflected from.
        A positive Rc means the surface appears concave to the incident
        beam.
    alpha : float
        Angle of incidence in degrees
    nr1 : float
        refractive index of medium the beam starts in
    nr2 : float
        refractive index of medium the beam ends up in
    direction : str
        Which plane this reflection occurs in, either `x` or `y`.
    """
    alpha1 = np.radians(alpha)
    # we get alpha2 from Snell's law
    sin_alpha2 = (nr1 / nr2) * np.sin(alpha1)
    if abs(float(sin_alpha2)) > 1:
        raise TotalReflectionError("Total internal reflection")
    alpha2 = np.arcsin(sin_alpha2)
    cos_alpha1 = np.cos(alpha1)
    cos_alpha2 = np.cos(alpha2)

    if direction == "x":
        # Tangential
        A = cos_alpha2 / cos_alpha1
        D = cos_alpha1 / cos_alpha2
        delta_n = (nr2 * cos_alpha2 - nr1 * cos_alpha1) / (cos_alpha1 * cos_alpha2)
    else:
        # sagittal
        A = 1.0
        D = 1.0
        delta_n = nr2 * cos_alpha2 - nr1 * cos_alpha1
    C = delta_n / Rc

    return np.array([[A, 0.0], [C, D]])
