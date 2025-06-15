"""Basic mesh wrapping utility."""

from __future__ import annotations

import numpy as np
import trimesh


def wrap_mesh(input_mesh: trimesh.Trimesh, wrap_thickness: float = 0.1) -> trimesh.Trimesh:
    """Return a copy of ``input_mesh`` with vertices offset along normals.

    Parameters
    ----------
    input_mesh:
        Mesh to wrap.
    wrap_thickness:
        Distance to offset each vertex along its normal.
    """
    if wrap_thickness <= 0:
        raise ValueError("wrap_thickness must be positive")

    mesh = input_mesh.copy()
    normals = mesh.vertex_normals
    if normals.shape[0] == 0:
        mesh.compute_vertex_normals()
        normals = mesh.vertex_normals
    mesh.vertices = mesh.vertices + wrap_thickness * normals
    return mesh


__all__ = ["wrap_mesh"]
