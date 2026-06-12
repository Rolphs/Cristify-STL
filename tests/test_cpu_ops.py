"""Tests for the CPU fallback of the voronizer pipeline."""

import numpy as np
import pytest

from app.voronizer import backend, cpu_ops


@pytest.fixture(autouse=True)
def force_cpu(monkeypatch):
    monkeypatch.setenv("CRISTIFY_FORCE_CPU", "1")


def test_backend_force_cpu():
    assert backend.cuda_available() is False


def test_boolean_ops():
    u = np.array([[[-1.0, 1.0]]])
    v = np.array([[[1.0, -1.0]]])
    assert np.array_equal(cpu_ops.union(u, v), np.array([[[-1.0, -1.0]]]))
    assert np.array_equal(cpu_ops.intersection(u, v), np.array([[[1.0, 1.0]]]))
    # subtract removes the cutting tool ``u`` from ``v``
    assert np.array_equal(cpu_ops.subtract(u, v), np.array([[[1.0, -1.0]]]))


def test_translate_wraps():
    u = np.zeros((3, 3, 3), dtype=np.float32)
    u[0, 0, 0] = -1
    v = cpu_ops.translate(u, 1, 0, 0)
    assert v[1, 0, 0] == -1
    assert v[0, 0, 0] == 0


def test_sphere_sdf_signs():
    x = np.linspace(-2, 2, 9)
    u = cpu_ops.sphere(x, x, x, 1.0)
    assert u[4, 4, 4] < 0  # center is inside
    assert u[0, 0, 0] > 0  # corner is outside


def test_rect_sdf_signs():
    x = np.linspace(-2, 2, 9)
    u = cpu_ops.rect(x, x, x, 2, 2, 2)
    assert u[4, 4, 4] < 0
    assert u[0, 4, 4] > 0


def test_toFRep():
    u = np.zeros((2, 2, 2), dtype=bool)
    u[0, 0, 0] = True
    v = cpu_ops.toFRep(u)
    assert v[0, 0, 0] == np.float32(-0.01)
    assert v[1, 1, 1] == np.float32(0.01)


def test_jumpFlood_distances():
    u = np.ones((8, 8, 8), dtype=np.float32)
    u[4, 4, 4] = -1  # single seed
    out = cpu_ops.jumpFlood(u)
    assert out[4, 4, 4, 3] == 0
    assert np.allclose(out[4, 4, 6, :3], [4, 4, 4])
    assert out[4, 4, 6, 3] == pytest.approx(2.0)


def test_SDF3D_signs():
    u = np.full((8, 8, 8), 0.01, dtype=np.float32)
    u[3:6, 3:6, 3:6] = -0.01
    sdf = cpu_ops.SDF3D(u)
    assert sdf[4, 4, 4] < 0
    assert sdf[0, 0, 0] > 0
    assert sdf[0, 0, 0] > sdf[2, 2, 2]  # farther outside, larger distance


def test_simplify_bands():
    u = np.full((6, 6, 6), 1.0, dtype=np.float32)
    u[2:4, 2:4, 2:4] = -1.0
    v = cpu_ops.simplify(u)
    assert set(np.unique(v)) <= {np.float32(-0.01), np.float32(0.0), np.float32(0.01)}
    assert v[2, 2, 2] == 0  # boundary voxel has both signs around it


def test_condense_crops_and_pads():
    u = np.full((20, 20, 20), 1.0, dtype=np.float32)
    u[8:12, 8:12, 8:12] = -1.0
    v = cpu_ops.condense(u, buffer=2, tpb=8)
    assert all(dim % 8 == 0 for dim in v.shape)
    assert np.min(v) < 0


def test_genRandPoints_inside_only():
    u = np.full((10, 10, 10), 1.0, dtype=np.float32)
    u[3:7, 3:7, 3:7] = -0.5
    pts = cpu_ops.genRandPoints(u, threshold=5.0)
    outside = pts[u >= 0]
    assert np.all(outside == 1)


def test_findVol(capsys):
    u = np.full((4, 4, 4), 1.0)
    u[0, 0, 0] = -1.0
    vol = cpu_ops.findVol(u, [2.0, 2.0, 2.0], 1.25, "Test")
    assert vol == pytest.approx(8.0)


def test_setColor():
    u = np.full((2, 2, 2), 1.0)
    u[0, 0, 0] = -1.0
    img = cpu_ops.setColor(u, [255, 0, 0], [0, 0, 255])
    assert tuple(img[0, 0, 0]) == (255, 0, 0)
    assert tuple(img[1, 1, 1]) == (0, 0, 255)


def test_voronize_end_to_end_cpu():
    """Full voronize() run on a small sphere using the CPU backend."""
    from app.voronizer import Frep as f
    from app.voronizer.voronize import voronize
    from app.voronizer.SDF3D import SDF3D

    x = np.linspace(-2, 2, 24)
    shape = SDF3D(f.sphere(x, x, x, 1.5))
    rng = np.random.default_rng(0)
    seeds = np.ones(shape.shape)
    seed_idx = rng.integers(4, 20, size=(8, 3))
    for i, j, k in seed_idx:
        seeds[i, j, k] = 0
    result = voronize(shape, seeds, cellThickness=2, shellThickness=1,
                      scale=[1, 1, 1])
    assert result.shape == shape.shape
    assert np.min(result) < 0  # produced solid walls
    assert np.max(result) > 0  # and empty cells
