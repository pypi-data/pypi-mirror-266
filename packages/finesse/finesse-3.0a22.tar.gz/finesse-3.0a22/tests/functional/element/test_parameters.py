"""Parameter unit tests."""

from finesse.symbols import Constant


def test_parameter_equality_checks(model):
    """Test that parameters can be directly compared to numbers and other symbols."""
    model.parse("laser l1 P=3.14")
    assert model.l1.P == 3.14
    assert model.l1.P == Constant(3.14)
    assert model.l1.P == (Constant(3.14) + Constant(3.14)) / 2
    assert model.l1.P.ref == model.l1.P


def test_parameter_ref_substitution(model):
    """Test that parameter refs can be subsituted for in expressions."""
    model.parse("laser l1 P=3.14")
    assert model.l1.P.eval() == 3.14
    assert (model.l1.P.ref + 1).eval(subs={model.l1.P: 4}) == 5


def test_bool_parameter_checks(model):
    """Test bool parameters get boolean checked properly."""
    from finesse.parameter import bool_parameter
    from finesse.element import ModelElement

    @bool_parameter("bool", "")
    class TEST(ModelElement):
        pass

    model.add(TEST("test"))
    model.test.bool = True
    assert model.test.bool
    assert model.test.bool.ref
    model.test.bool = False
    assert not model.test.bool
    assert not model.test.bool.ref
