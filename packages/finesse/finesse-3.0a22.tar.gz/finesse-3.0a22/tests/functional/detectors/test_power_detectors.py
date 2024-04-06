import finesse
import numpy as np


def test_issue_163():
    """power.pyx check_is_fsig wasn't working properly due to insufficient test cases
    between fsig/f symbols etc."""
    model = finesse.script.parse(
        """
    laser l1 P=1
    mod mod1 order=1 mod_type=pm f=80M midx=0.5
    m m1 R=0.5 L=0
    m m2 R=0.5 L=0
    link(l1,mod1,m1,10,m2)
    sgen sig m2.mech.z
    var dummy 1

    pd2 pd m1.p1.o 80M 0 100
    """
    )

    model.fsig.f = model.pd.f2.ref
    out0 = model.run("xaxis(pd.f2, log, 0.1, 100, 1)")

    # Check more complicated symbols
    model.fsig.f = -1 + model.pd.f2.ref + 1
    out1 = model.run("xaxis(pd.f2, log, 0.1, 100, 1)")

    model.fsig.f = 1 + model.dummy.ref - 1
    model.pd.f2 = model.dummy.ref
    out2 = model.run("xaxis(dummy, log, 0.1, 100, 1)")

    # Standard scanning
    model.fsig.f = 100
    model.pd.f2.value = model.fsig.f.ref
    out = model.run("xaxis(fsig, log, 0.1, 100, 1)")

    assert np.allclose(out["pd"], out0["pd"])
    assert np.allclose(out["pd"], out1["pd"])
    assert np.allclose(out["pd"], out2["pd"])
