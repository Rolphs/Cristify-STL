"""Example usage of :func:`app.core.fractal.generate_fractal_geometry`."""

import numpy as np
from app.core.fractal import generate_fractal_geometry

if __name__ == "__main__":
    verts = np.array([[0, 0, 0], [1, 0, 0]])
    edges = [(0, 1)]
    new_verts, _ = generate_fractal_geometry(verts, edges, iterations=1)
    print(new_verts)
