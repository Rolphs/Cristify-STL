"""Mesh transformation utilities for Cristify STL."""

from __future__ import annotations

import numpy as np
import trimesh


def cristify_mesh(mesh: trimesh.Trimesh, amount: float = 1.0) -> trimesh.Trimesh:
    """Project vertices downward to create a draped effect.

    Each vertex is translated along the negative ``Z`` axis by ``amount`` times
    its distance from the top of the mesh. The original mesh is not modified.

    Parameters
    ----------
    mesh:
        Input mesh to transform.
    amount:
        Scale factor for the downward displacement. ``1.0`` moves each vertex by
        its full distance from the top, ``0`` leaves the mesh unchanged.

    Returns
    -------
    trimesh.Trimesh
        A new mesh instance with transformed vertices.
    """

    if not isinstance(mesh, trimesh.Trimesh):
        raise TypeError("mesh must be a trimesh.Trimesh instance")

    if not np.isscalar(amount):
        raise TypeError("amount must be a scalar numeric value")

    vertices = mesh.vertices.view(np.ndarray)
    faces = mesh.faces.view(np.ndarray)

    max_z = float(vertices[:, 2].max()) if len(vertices) else 0.0

    new_vertices = vertices.copy()
    distances = max_z - vertices[:, 2]
    new_vertices[:, 2] -= distances * float(amount)

    new_mesh = trimesh.Trimesh(
        vertices=new_vertices,
        faces=faces.copy(),
        process=False,
    )

    return new_mesh

