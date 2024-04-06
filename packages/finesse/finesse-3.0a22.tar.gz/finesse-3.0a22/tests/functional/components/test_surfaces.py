"""Surface tests.

This tests the common parts shared by beamsplitter and mirrors in :class:`.Surface`.
"""

import pytest
from hypothesis import given, settings, HealthCheck
from finesse.components import Beamsplitter, Mirror
from testutils.data import RADII_OF_CURVATURES, RADII_OF_CURVATURE_PAIRS, RTL_SETS
from testutils.fuzzing import DEADLINE, rtl_sets

surfaces = pytest.mark.parametrize("surface", (Beamsplitter, Mirror))


@pytest.mark.parametrize("R,T,L", RTL_SETS)
@surfaces
def test_rtl(surface, R, T, L):
    """Test that a surface's R, T and L are correctly set by the constructor."""
    obj = surface("cmp1", R=R, T=T, L=L)
    assert float(obj.R) == R
    assert float(obj.T) == T
    assert float(obj.L) == L


@given(RTL=rtl_sets())
@settings(
    deadline=DEADLINE,
    suppress_health_check=[HealthCheck.filter_too_much, HealthCheck.too_slow],
)
@surfaces
def test_rtl_fuzzing(surface, RTL):
    """Test that a surface's R, T and L are correctly set by the constructor."""
    R, T, L = RTL
    obj = surface("cmp1", R=R, T=T, L=L)
    assert float(obj.R) == R
    assert float(obj.T) == T
    assert float(obj.L) == L


@pytest.mark.parametrize("R,T,L", RTL_SETS)
@surfaces
def test_rtl__two_from_three(surface, R, T, L):
    """Test that a surface's constructor correctly forces R+T+L = 1 from provided
    pairs."""

    def _do_two_from_three_test(specified_params, other_param_name):
        obj = surface("cmp1", **specified_params)
        value = float(getattr(obj, other_param_name))
        assert value == pytest.approx(rtl_data[other_param_name])

    rtl_data = dict(R=R, T=T, L=L)
    keys = list(rtl_data)

    data1 = dict(rtl_data)
    del data1[keys[0]]
    _do_two_from_three_test(data1, keys[0])

    data1 = dict(rtl_data)
    del data1[keys[1]]
    _do_two_from_three_test(data1, keys[1])

    data1 = dict(rtl_data)
    del data1[keys[2]]
    _do_two_from_three_test(data1, keys[2])


@pytest.mark.parametrize(
    "R,T,L", ((-1, 0.5, 0.5), (0.5, -0.5, 1), (0.5, 0.7, -0.2), (-1, -1, -1))
)
@surfaces
def test_rtl__negative_invalid(surface, R, T, L):
    """Test that a surface's R, T and L cannot be negative."""
    with pytest.raises(ValueError):
        surface("cmp1", R=R, T=T, L=L)


@pytest.mark.parametrize("Rc", (0, 0.0))
@surfaces
def test_rc__invalid(surface, Rc):
    """Test that a surface's radius of curvature cannot be 0."""
    with pytest.raises(ValueError):
        surface(name="cmp1", Rc=Rc)


@pytest.mark.parametrize("Rc", RADII_OF_CURVATURES)
@surfaces
def test_rc_sets_rcx_and_rcy__single(surface, Rc):
    """Test that setting a surface's Rc sets Rcx and Rcy to the same value."""
    obj = surface(name="cmp1")
    obj.Rc = Rc
    Rcx, Rcy = obj.Rc
    assert float(Rcx) == float(Rcy) == pytest.approx(Rc)


@pytest.mark.parametrize("Rc", RADII_OF_CURVATURE_PAIRS)
@surfaces
def test_rc_sets_rcx_and_rcy__separate(surface, Rc):
    """Test that setting a surface's Rc to a two-valued sequence sets Rcx and Rcy to
    those respective values."""
    obj = surface(name="cmp1")
    obj.Rc = Rc
    assert float(obj.Rc[0]) == pytest.approx(Rc[0])
    assert float(obj.Rc[1]) == pytest.approx(Rc[1])
