import pytest
import finesse
import numpy as np


@pytest.fixture
def solution():
    model = finesse.Model()
    model.parse(
        """
    l l1 P=1
    l l2 P=1 f=10M
    m m1 L=0 T=0
    link(l1, m1, l2)

    gauss g1 l1.p1.o w0=0.05 z=0
    modes(maxtem=2)
    """
    )
    model.l2.tem(0, 0, 0)
    model.l2.tem(0, 2, 1)
    return model.run("dc_fields()")


def test_get_node_name(solution):
    _ = solution[("l1.p1.i", "l1.p1.o"), :, :]
    with pytest.raises(KeyError):
        _ = solution["l1.p1."]
    with pytest.raises(TypeError):
        _ = solution(["l1.p1.i", "l1.p1.o"])


def test_values(solution):
    # all nodes in 0Hz not in 00 == 0
    assert np.allclose(solution[:, 0, 1:], 0)
    assert np.allclose(solution[("l1.p1.o", "m1.p1.i"), 0, 0], 1)
    # all nodes in 10MHz not in 02 == 0
    index = np.array([_ == [0, 2] for _ in solution.homs])
    assert np.allclose(solution[:, 1, ~index], 0)
    assert np.allclose(solution[("l2.p1.o", "m1.p2.i"), 1, index], 1)


def test_shapes(solution):
    sol = solution
    n_nodes = len(sol.nodes)
    n_freqs = 2
    n_homs = 6
    assert sol.fields.shape == (n_nodes, n_freqs, n_homs)
    assert sol["l2.p1.i"].shape == (1, n_freqs, n_homs)
    assert sol["l2.p1.i", :, 0].shape == (1, n_freqs)
    assert sol[("l2.p1.i", "m1.p1.o")].shape == (2, n_freqs, n_homs)
    assert sol[:, :, sol.homs.index([0, 1])].shape == (n_nodes, n_freqs)
    assert sol[5].shape == (n_freqs, n_homs)
    assert sol[1:3].shape == (2, n_freqs, n_homs)
    assert sol[1:3, 0].shape == (2, n_homs)
    assert sol[np.array([1, 3, 5, 7])].shape == (4, n_freqs, n_homs)
    idx = np.array([node.split(".")[-1] == "o" for node in sol.nodes])
    assert sol[idx].shape == (np.count_nonzero(idx), n_freqs, n_homs)
