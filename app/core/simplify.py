"""Mesh simplification helpers."""

from __future__ import annotations

import numpy as np
import trimesh
import open3d as o3d


def simplify_mesh(mesh: trimesh.Trimesh, target_reduction: float = 0.5) -> trimesh.Trimesh:
    """Return a simplified copy of ``mesh`` using quadric decimation."""
    if not (0.0 < target_reduction < 1.0):
        raise ValueError("target_reduction must be between 0 and 1")

    target_faces = max(4, int(len(mesh.faces) * (1 - target_reduction)))

    o3_mesh = o3d.geometry.TriangleMesh(
        o3d.utility.Vector3dVector(mesh.vertices),
        o3d.utility.Vector3iVector(mesh.faces),
    )
    simplified = o3_mesh.simplify_quadric_decimation(target_faces)
    simplified.remove_degenerate_triangles()
    simplified.remove_duplicated_triangles()
    simplified.remove_duplicated_vertices()
    simplified.remove_non_manifold_edges()
    simplified.remove_unreferenced_vertices()

    vertices = np.asarray(simplified.vertices)
    faces = np.asarray(simplified.triangles)
    return trimesh.Trimesh(vertices=vertices, faces=faces, process=False)


__all__ = ["simplify_mesh"]
