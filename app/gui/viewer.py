"""Simple 3D viewer utilities."""

from __future__ import annotations

import open3d as o3d
import trimesh

__all__ = ["show_mesh"]


def _mesh_to_o3d(mesh: trimesh.Trimesh) -> o3d.geometry.TriangleMesh:
    """Convert :class:`trimesh.Trimesh` to :class:`open3d.geometry.TriangleMesh`."""
    o3d_mesh = o3d.geometry.TriangleMesh()
    o3d_mesh.vertices = o3d.utility.Vector3dVector(mesh.vertices)
    o3d_mesh.triangles = o3d.utility.Vector3iVector(mesh.faces)
    o3d_mesh.compute_vertex_normals()
    return o3d_mesh


def show_mesh(mesh: trimesh.Trimesh) -> None:
    """Display a mesh in a basic Open3D viewer."""
    o3d_mesh = _mesh_to_o3d(mesh)
    o3d.visualization.draw_geometries([o3d_mesh])
