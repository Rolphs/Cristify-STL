"""Utility helpers for cleaning and repairing meshes."""

from __future__ import annotations

import numpy as np
import trimesh
import open3d as o3d


def _to_open3d(mesh: trimesh.Trimesh) -> o3d.geometry.TriangleMesh:
    """Convert a :class:`trimesh.Trimesh` to an Open3D mesh."""
    vertices = o3d.utility.Vector3dVector(mesh.vertices)
    triangles = o3d.utility.Vector3iVector(mesh.faces)
    return o3d.geometry.TriangleMesh(vertices, triangles)


def _from_open3d(o3_mesh: o3d.geometry.TriangleMesh) -> trimesh.Trimesh:
    """Create a :class:`trimesh.Trimesh` from an Open3D mesh."""
    vertices = np.asarray(o3_mesh.vertices)
    faces = np.asarray(o3_mesh.triangles)
    return trimesh.Trimesh(vertices=vertices, faces=faces, process=False)


def repair_mesh(mesh: trimesh.Trimesh) -> trimesh.Trimesh:
    """Perform lightweight cleanup of a mesh.

    Operations include removal of degenerate and duplicate faces as well as
    merging of identical vertices. The original mesh is not modified.

    Parameters
    ----------
    mesh:
        Mesh to repair.

    Returns
    -------
    trimesh.Trimesh
        A new mesh instance with common defects removed.
    """

    if not isinstance(mesh, trimesh.Trimesh):
        raise TypeError("mesh must be a trimesh.Trimesh instance")

    o3_mesh = _to_open3d(mesh)
    o3_mesh.remove_duplicated_vertices()
    o3_mesh.remove_duplicated_triangles()
    o3_mesh.remove_degenerate_triangles()
    o3_mesh.remove_non_manifold_edges()
    o3_mesh.remove_unreferenced_vertices()

    cleaned = _from_open3d(o3_mesh)
    cleaned.remove_duplicate_faces()
    cleaned.remove_degenerate_faces()
    cleaned.remove_unreferenced_vertices()

    return cleaned


def make_watertight(mesh: trimesh.Trimesh) -> trimesh.Trimesh:
    """Attempt to make a mesh watertight by filling simple holes."""

    repaired = repair_mesh(mesh)
    trimesh.repair.fill_holes(repaired)
    repaired.remove_unreferenced_vertices()
    return repaired


__all__ = ["repair_mesh", "make_watertight"]
