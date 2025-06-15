import numpy as np
from scipy.spatial import KDTree
import trimesh
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_kd_tree(vertices: np.ndarray) -> KDTree:
    return KDTree(vertices)

def apply_gravitational_tension_model(input_mesh: trimesh.Trimesh, kd_tree: KDTree, g: float = 1e-3, tension: float = 0.1) -> np.ndarray:
    new_vertices = input_mesh.vertices.copy()
    for i, vertex in enumerate(input_mesh.vertices):
        distances, indices = kd_tree.query(vertex, k=10)
        force = np.zeros(3)
        for dist, index in zip(distances[1:], indices[1:]):
            direction = input_mesh.vertices[index] - vertex
            if dist > 0:
                force += g * direction / (dist ** 2)
        tension_force = tension * np.sum(new_vertices, axis=0) / len(new_vertices)
        new_vertices[i] += force - tension_force
    return new_vertices