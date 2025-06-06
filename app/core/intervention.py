"""Mesh intervention analysis utilities.

This module provides experimental heuristics for identifying areas of a mesh
that might benefit from geometric interventions. The logic is intentionally
lightweight and does not modify geometry. It returns scores that future
components can use to decide whether to apply transformations.
"""

from __future__ import annotations

from typing import Dict

import numpy as np
import trimesh


def analyze_mesh(mesh: trimesh.Trimesh) -> Dict[str, float | int | bool]:
    """Analyze a mesh and compute intervention metrics.

    Parameters
    ----------
    mesh:
        The :class:`trimesh.Trimesh` object to inspect.

    Returns
    -------
    dict
        Dictionary containing heuristic metrics.
    """
    if not isinstance(mesh, trimesh.Trimesh):
        raise TypeError("mesh must be a trimesh.Trimesh instance")

    result: Dict[str, float | int | bool] = {}

    result["has_holes"] = not mesh.is_watertight

    unique_idx, counts = np.unique(
        mesh.edges_unique_inverse,
        return_counts=True,
    )
    isolated_edges = mesh.edges_unique[counts == 1]
    result["isolated_edges"] = int(len(isolated_edges))

    normals = mesh.face_normals
    if normals.size:
        vertical = np.array([0.0, 0.0, 1.0])
        cos_angles = np.abs(normals.dot(vertical))
        flat_faces = cos_angles > 0.98
        result["flat_face_ratio"] = float(flat_faces.sum()) / len(normals)
    else:
        result["flat_face_ratio"] = 0.0

    score = 0.0
    if result["has_holes"]:
        score += 0.5
    if mesh.edges_unique.shape[0] > 0:
        score += 0.3 * (result["isolated_edges"] / mesh.edges_unique.shape[0])
    score += 0.2 * result["flat_face_ratio"]

    result["intervention_score"] = round(score, 3)
    return result
