import numpy as np
import trimesh

from app.core.texturize import (
    create_kd_tree,
    apply_gravitational_attraction,
    fractal_noise,
    smooth_mesh,
)


def test_create_kd_tree():
    vertices = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]])
    tree = create_kd_tree(vertices)
    dist, idx = tree.query([0.0, 0.0, 0.0], k=1)
    assert idx == 0
    assert np.isclose(dist, 0.0)


def test_apply_gravitational_attraction():
    mesh = trimesh.primitives.Box()
    kd = create_kd_tree(mesh.vertices)
    result = apply_gravitational_attraction(mesh, kd, g=1e-2)
    assert result.shape == mesh.vertices.shape
    assert not np.allclose(result, mesh.vertices)


def test_fractal_noise():
    verts = np.zeros((5, 3))
    noisy = fractal_noise(verts, scale=0.5, octaves=2)
    assert noisy.shape == verts.shape
    assert not np.allclose(noisy, verts)


def test_smooth_mesh():
    mesh = trimesh.primitives.Box()
    result = smooth_mesh(mesh.copy(), iterations=1)
    assert isinstance(result, trimesh.Trimesh)
    assert result.vertices.shape == mesh.vertices.shape
