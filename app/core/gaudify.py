"""Utilities for Gaudification of meshes.

This module provides simple heuristics for transforming a mesh to
reduce overhangs by converting them into gothic-like arches.
The implementation is adapted from an earlier prototype script.
"""

from __future__ import annotations

import logging
from typing import Iterable

import numpy as np
import trimesh


def reorient_mesh_for_printing(mesh: trimesh.Trimesh) -> trimesh.Trimesh:
    """Orient ``mesh`` using its oriented bounding box."""
    mesh = mesh.copy()
    mesh.rezero()
    orientation = mesh.bounding_box_oriented.primitive.transform
    mesh.apply_transform(orientation)
    return mesh


def get_overhang_faces(input_mesh: trimesh.Trimesh, max_overhang_angle: float = 45.0) -> np.ndarray:
    """Return indices of faces exceeding ``max_overhang_angle`` from vertical."""
    angles = input_mesh.face_normals[:, 2]
    overhang_faces = np.where(np.degrees(np.arccos(angles)) > max_overhang_angle)[0]
    return overhang_faces


def modify_overhangs(input_mesh: trimesh.Trimesh, overhang_faces: Iterable[int]) -> trimesh.Trimesh:
    """Replace ``overhang_faces`` with simple gothic arch structures."""
    mesh = input_mesh.copy()
    new_faces: list[list[int]] = []
    new_vertices_list: list[np.ndarray] = []

    for face_index in overhang_faces:
        face = mesh.faces[face_index]
        vertices = mesh.vertices[face]

        center = vertices.mean(axis=0)
        center[2] += 0.01

        new_vertex_indices = []
        for _ in range(3):
            new_vertices_list.append(center)
            new_vertex_indices.append(len(mesh.vertices) + len(new_vertices_list) - 1)

        for i in range(3):
            new_faces.append([face[i], face[(i + 1) % 3], new_vertex_indices[i]])

    if new_vertices_list:
        new_vertices_array = np.array(new_vertices_list)
        mesh.vertices = np.vstack((mesh.vertices, new_vertices_array))

    # remove original overhang faces then append new ones
    remaining = np.delete(mesh.faces, list(overhang_faces), axis=0)
    if new_faces:
        new_faces_array = np.array(new_faces)
        mesh.faces = np.vstack((remaining, new_faces_array))
    else:
        mesh.faces = remaining

    return mesh


def gaudify_mesh(
    input_mesh: trimesh.Trimesh,
    max_overhang_angle: float = 45.0,
    max_iterations: int = 10,
) -> trimesh.Trimesh:
    """Iteratively modify overhangs until none remain or ``max_iterations`` is reached."""
    mesh = input_mesh.copy()
    iteration = 0

    while iteration < max_iterations:
        overhang_faces = get_overhang_faces(mesh, max_overhang_angle)
        if len(overhang_faces) == 0:
            break
        mesh = modify_overhangs(mesh, overhang_faces)
        iteration += 1
        if not mesh.is_watertight:
            logging.warning(
                "Mesh is not watertight after modification; continuing without repair"
            )
        if mesh.faces.shape[0] == 0:
            logging.error("Mesh has no faces after modification; stopping")
            break
    return mesh


__all__ = [
    "reorient_mesh_for_printing",
    "get_overhang_faces",
    "modify_overhangs",
    "gaudify_mesh",
]
