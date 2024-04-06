import finesse
import numpy as np


def test_field_detector_conjugate():
    model = finesse.script.parse(
        """
    l l1
    nothing n1
    link(l1.p1, 10, n1.p1)
    sgen sg l1.amp.i
    fsig(10000)
    fd E n1.p1.i 0
    fd u n1.p1.i +fsig
    fd l n1.p1.i -fsig
    gauss g1 l1.p1.o w0=1m z=0
    """
    )

    sol = model.run()
    assert np.allclose(sol["u"], sol["l"].conj())
