# %%
import pytest
import numpy as np
import finesse
from finesse.analysis.actions import (
    FrequencyResponse,
    FrequencyResponse2,
    FrequencyResponse3,
)


def test_sqz_sideband_frequency_response_phase():
    model = finesse.script.parse(
        """
    sq SQZ 0
    bs BS L=0 T=1e-14
    laser L0 P=1/1e-14 phase=-90
    readout_dc PD
    link(SQZ, 1000, BS.p1, BS.p2, PD)
    link(L0, BS.p4)
    fsig(1)
    """
    )

    sol = model.run(
        FrequencyResponse(
            np.geomspace(0.1, 1000, 3),
            [model.SQZ.upper, model.SQZ.lower_conj],
            model.PD.DC.o,
        )
    )
    # conjugate of lower and upper have same phase propagation
    assert np.allclose(
        sol["SQZ.upper", "PD.DC.o"],
        sol["SQZ.lower_conj", "PD.DC.o"],
    )


def test_sqz_sideband_frequency_response_2_phase():
    model = finesse.script.parse(
        """
    sq SQZ 0
    bs BS L=0 T=1e-14
    laser L0 P=1/1e-14 phase=-90
    readout_dc PD
    link(SQZ, 1000, BS.p1, BS.p2, PD)
    link(L0, BS.p4)
    fsig(1)
    """
    )

    sol = model.run(
        FrequencyResponse2(
            np.geomspace(0.1, 1000),
            [(model.SQZ.p1.o, model.fsig.f.ref), (model.SQZ.p1.o, -model.fsig.f.ref)],
            [model.PD.DC.o],
        )
    )
    upper = sol.out[:, 0, 0, 0]
    lower = sol.out[:, 0, 1, 0]
    # frequency response 2 will output the un-conjugate lower sideband
    assert np.allclose(
        upper,
        lower,
    )


def test_sqz_sideband_frequency_response_3_phase():
    model = finesse.script.parse(
        """
    sq SQZ 0
    bs BS L=0 T=1e-14
    laser L0 P=1/1e-14 phase=-90
    readout_dc PD
    link(SQZ, 1000, BS.p1, BS.p2, PD)
    link(L0, BS.p4)
    fsig(1)
    """
    )
    f_u = +model.fsig.f.ref
    f_l = -model.fsig.f.ref

    sol = model.run(
        FrequencyResponse3(
            np.geomspace(0.1, 1000, 10),
            [(model.SQZ.p1.o, f_u), (model.SQZ.p1.o, f_l)],
            [(model.PD.p1.i, f_u), (model.PD.p1.i, f_l)],
        )
    )
    u2u = sol.out[:, 0, 0]
    u2l = sol.out[:, 1, 0]
    l2u = sol.out[:, 0, 1]
    l2l = sol.out[:, 1, 1]
    assert np.allclose(u2l, l2u)
    assert np.allclose(u2u, l2l)
    assert np.allclose(abs(u2u), 1)
    assert np.allclose(abs(l2l), 1)
    assert np.allclose(abs(u2l), 0)
    assert np.allclose(abs(l2u), 0)


@pytest.mark.parametrize("f", [1, "fsig.f"])
def test_frequency_response2_exception(f):
    model = finesse.script.parse(
        """
    sq SQZ 0
    bs BS L=0 T=1e-14
    laser L0 P=1/1e-14 phase=-90
    readout_dc PD
    link(SQZ, 1000, BS.p1, BS.p2, PD)
    link(L0, BS.p4)
    fsig(1)
    """
    )
    if isinstance(f, str):
        f_u = "+" + f
        f_l = "-" + f
    else:
        f_u = +f
        f_l = -f

    action = FrequencyResponse2(
        np.geomspace(0.1, 1000, 1),
        [(model.SQZ.p1.o, f_u), (model.SQZ.p1.o, f_l)],
        ["PD.DC"],
    )

    with pytest.raises(finesse.exceptions.FinesseException):
        model.run(action)


@pytest.mark.parametrize("f", [1, "fsig.f"])
def test_frequency_response3_exception(f):
    model = finesse.script.parse(
        """
    sq SQZ 0
    bs BS L=0 T=1e-14
    laser L0 P=1/1e-14 phase=-90
    readout_dc PD
    link(SQZ, 1000, BS.p1, BS.p2, PD)
    link(L0, BS.p4)
    fsig(1)
    """
    )
    if isinstance(f, str):
        f_u = "+" + f
        f_l = "-" + f
    else:
        f_u = +f
        f_l = -f

    action = FrequencyResponse3(
        np.geomspace(0.1, 1000, 1),
        [(model.SQZ.p1.o, f_u), (model.SQZ.p1.o, f_l)],
        [(model.PD.p1.i, f_u), (model.PD.p1.i, f_l)],
    )

    with pytest.raises(finesse.exceptions.FinesseException):
        model.run(action)


@pytest.mark.parametrize("F_Hz", [[1], [1, 2], [1, 2, 3]])
def test_output_shape(F_Hz):
    F_Hz = np.asarray(F_Hz)
    from finesse import Model
    import finesse.analysis.actions as act
    from finesse.components import Squeezer, Mirror, Cavity, ReadoutDC

    model = Model()
    model.add(Squeezer("SQZ", db=10, angle=0))
    model.add(Mirror("ITM", T=0.014, L=0, Rc=1935))
    model.add(Mirror("ETM", T=0, L=0, Rc=2245))
    model.connect(model.ITM.p1, model.ETM.p1, 4e3)
    model.connect(model.SQZ.p1, model.ITM.p2)
    model.add(Cavity("cavARM", model.ETM.p1.o))
    model.add(ReadoutDC("REFL", model.ETM.p1.o, output_detectors=True))
    model.modes(maxtem=2)
    model.fsig.f = 1

    def run_fresp_actions(F_Hz):
        fsig = model.fsig.f.ref
        sol = model.run(
            act.Series(
                act.FrequencyResponse(
                    F_Hz,
                    ["SQZ.upper", "SQZ.lower_conj"],
                    ["REFL.DC.o"],
                    name="fresp1",
                ),
                act.FrequencyResponse2(
                    F_Hz,
                    [
                        ("SQZ.p1", +fsig),
                        ("SQZ.p1", -fsig),
                    ],
                    ["REFL.DC.o"],
                    name="fresp2",
                ),
                act.FrequencyResponse3(
                    F_Hz,
                    [
                        ("SQZ.p1.o", +fsig),
                        ("SQZ.p1.o", -fsig),
                    ],
                    [
                        ("ETM.p1.i", +fsig),
                        ("ETM.p1.i", -fsig),
                    ],
                    name="fresp3",
                ),
            )
        )
        return sol

    sol = run_fresp_actions(F_Hz)
    assert sol["fresp1"].out.shape == (F_Hz.size, 2, 1)
    assert sol["fresp2"].out.shape == (F_Hz.size, 1, 2, 6)
    assert sol["fresp3"].out.shape == (F_Hz.size, 2, 2, 6, 6)


# %%
