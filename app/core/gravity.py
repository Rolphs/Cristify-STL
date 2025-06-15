"""Utilities for mesh deformation using a gravity/tension model."""

from __future__ import annotations

import numpy as np
import trimesh
from scipy.spatial import KDTree


def apply_gravitational_tension_model(
    input_mesh: trimesh.Trimesh,
    kd_tree: KDTree,
    g: float = 1e-3,
    tension: float = 0.1,
) -> np.ndarray:
    """Apply gravitational attraction with a simple tension component."""
    new_vertices = input_mesh.vertices.copy()
    k = min(10, len(input_mesh.vertices))
    for i, vertex in enumerate(input_mesh.vertices):
        distances, indices = kd_tree.query(vertex, k=k)
        force = np.zeros(3)
        for dist, index in zip(distances[1:], indices[1:]):
            direction = input_mesh.vertices[index] - vertex
            if dist > 0:
                force += g * direction / (dist ** 2)
        tension_force = tension * np.sum(new_vertices, axis=0) / len(new_vertices)
        new_vertices[i] += force - tension_force
    return new_vertices


__all__ = ["apply_gravitational_tension_model"]
