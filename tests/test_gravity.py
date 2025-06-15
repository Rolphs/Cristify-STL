import numpy as np
import trimesh

from app.core.texturize import create_kd_tree
from app.core.gravity import apply_gravitational_tension_model


def test_apply_gravitational_tension_model():
    mesh = trimesh.primitives.Box()
    kd = create_kd_tree(mesh.vertices)
    new_verts = apply_gravitational_tension_model(mesh, kd, g=1e-2, tension=0.1)
    assert new_verts.shape == mesh.vertices.shape
    assert not np.allclose(new_verts, mesh.vertices)
