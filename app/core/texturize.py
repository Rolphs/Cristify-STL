"""Utilities for procedurally texturizing meshes."""

from __future__ import annotations

import numpy as np
import trimesh
from scipy.spatial import KDTree


def create_kd_tree(vertices: np.ndarray) -> KDTree:
    """Return a :class:`KDTree` built from ``vertices``."""
    if not isinstance(vertices, np.ndarray):
        raise ValueError("vertices must be a numpy array")
    return KDTree(vertices)


def apply_gravitational_attraction(
    input_mesh: trimesh.Trimesh,
    kd_tree: KDTree,
    g: float = 1e-3,
) -> np.ndarray:
    """Apply a simple gravitational attraction among neighbouring vertices."""
    new_vertices = input_mesh.vertices.copy()
    k = min(10, len(input_mesh.vertices))
    for i, vertex in enumerate(input_mesh.vertices):
        distances, indices = kd_tree.query(vertex, k=k)
        force = np.zeros(3)
        for dist, index in zip(distances[1:], indices[1:]):
            direction = input_mesh.vertices[index] - vertex
            if dist > 0:
                force += g * direction / (dist ** 2)
        new_vertices[i] += force
    return new_vertices


def fractal_noise(vertices: np.ndarray, scale: float = 0.1, octaves: int = 4) -> np.ndarray:
    """Add fractal noise to ``vertices``."""
    if not isinstance(vertices, np.ndarray):
        raise ValueError("vertices must be a numpy array")
    noise = np.zeros_like(vertices)
    for octave in range(octaves):
        frequency = 2 ** octave
        amplitude = scale / frequency
        noise += amplitude * np.random.randn(*vertices.shape)
    return vertices + noise


def smooth_mesh(mesh: trimesh.Trimesh, iterations: int = 100) -> trimesh.Trimesh:
    """Run Taubin smoothing on ``mesh``."""
    working = trimesh.Trimesh(
        vertices=mesh.vertices.copy(), faces=mesh.faces.copy(), process=False
    )
    trimesh.smoothing.filter_taubin(working, iterations=iterations)
    return working


def make_organic_with_gravity(
    input_mesh: trimesh.Trimesh,
    noise_strength: float = 0.01,
    smooth_iterations: int = 200,
    g: float = 1e-3,
) -> trimesh.Trimesh:
    """Blend noise, smoothing and gravitational attraction."""
    noise = noise_strength * np.random.randn(*input_mesh.vertices.shape)
    input_mesh.vertices += noise
    trimesh.smoothing.filter_taubin(
        input_mesh, lamb=0.5, nu=-0.53, iterations=smooth_iterations
    )
    kd_tree = create_kd_tree(input_mesh.vertices)
    input_mesh.vertices = apply_gravitational_attraction(input_mesh, kd_tree, g)
    return input_mesh


__all__ = [
    "create_kd_tree",
    "apply_gravitational_attraction",
    "fractal_noise",
    "smooth_mesh",
    "make_organic_with_gravity",
]
