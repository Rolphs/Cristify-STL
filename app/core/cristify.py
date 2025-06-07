"""Mesh transformation utilities for Cristify STL."""

from __future__ import annotations

import numpy as np
import trimesh


def cristify_mesh(
    mesh: trimesh.Trimesh,
    amount: float = 1.0,
    *,
    axis: int | str = 2,
    floor: float | None = None,
) -> trimesh.Trimesh:
    """Project vertices downward to create a draped effect.

    Each vertex is translated along the negative chosen axis by ``amount``
    times its distance from the top of the mesh. The original mesh is not
    modified.

    Parameters
    ----------
    mesh:
        Input mesh to transform.
    amount:
        Scale factor for the downward displacement. ``1.0`` moves each
        vertex by its full distance from the top, ``0`` leaves the mesh
        unchanged.
    axis:
        Axis to project along. Can be ``0``, ``1``, ``2`` or ``"x"``, ``"y``,
        ``"z"``. Default is the Z axis.
    floor:
        Optional minimum coordinate value. Vertices will not be moved below
        this value after projection.

    Returns
    -------
    trimesh.Trimesh
        A new mesh instance with transformed vertices.
    """

    if not isinstance(mesh, trimesh.Trimesh):
        raise TypeError("mesh must be a trimesh.Trimesh instance")

    if not np.isscalar(amount):
        raise TypeError("amount must be a scalar numeric value")

    if isinstance(axis, str):
        axis_map = {"x": 0, "y": 1, "z": 2}
        if axis.lower() not in axis_map:
            raise ValueError("axis must be 0, 1, 2 or 'x', 'y', 'z'")
        axis_index = axis_map[axis.lower()]
    elif axis in (0, 1, 2):
        axis_index = int(axis)
    else:
        raise ValueError("axis must be 0, 1, 2 or 'x', 'y', 'z'")

    vertices = mesh.vertices.view(np.ndarray)
    faces = mesh.faces.view(np.ndarray)

    max_axis = float(vertices[:, axis_index].max()) if len(vertices) else 0.0

    new_vertices = vertices.copy()
    distances = max_axis - vertices[:, axis_index]
    new_vertices[:, axis_index] -= distances * float(amount)
    if floor is not None:
        new_vertices[:, axis_index] = np.maximum(
            new_vertices[:, axis_index],
            floor,
        )

    new_mesh = trimesh.Trimesh(
        vertices=new_vertices,
        faces=faces.copy(),
        process=False,
    )

    return new_mesh
