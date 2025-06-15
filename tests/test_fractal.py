import numpy as np

from app.core.fractal import generate_fractal_geometry


def test_generate_fractal_geometry_single_iteration():
    verts = np.array(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [1.0, 1.0, 0.0],
            [0.0, 1.0, 0.0],
        ]
    )
    edges = [(0, 1), (1, 2), (2, 3), (3, 0)]
    new_v, new_e = generate_fractal_geometry(verts, edges, iterations=1)
    assert new_v.shape[0] == 8
    mid = (verts[0] + verts[1]) / 2.0
    assert any(np.allclose(mid, v) for v in new_v[4:])
    assert new_e == edges


def test_generate_fractal_geometry_multiple_iterations():
    verts = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]])
    edges = [(0, 1)]
    new_v, _ = generate_fractal_geometry(verts, edges, iterations=2)
    assert new_v.shape[0] == 4
