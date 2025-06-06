"""Utility functions for loading and saving mesh files."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import trimesh


def load_mesh(path: str) -> trimesh.Trimesh:
    """Load a mesh from a file.

    Parameters
    ----------
    path : str
        Path to the mesh file.

    Returns
    -------
    trimesh.Trimesh
        The loaded mesh object.

    Raises
    ------
    FileNotFoundError
        If ``path`` does not exist.
    ValueError
        If the file cannot be loaded as a mesh.
    """
    file_path = Path(path)
    if not file_path.is_file():
        raise FileNotFoundError(f"Mesh file not found: {path}")

    try:
        mesh = trimesh.load(file_path, force="mesh")
    except Exception as exc:  # pragma: no cover - rely on trimesh exceptions
        raise ValueError(f"Failed to load mesh from {path}") from exc

    if not isinstance(mesh, trimesh.Trimesh):
        raise ValueError(f"File does not contain a valid mesh: {path}")

    return mesh


def save_mesh(mesh: trimesh.Trimesh, path: str) -> None:
    """Save a :class:`trimesh.Trimesh` to a file.

    Parameters
    ----------
    mesh : trimesh.Trimesh
        Mesh object to save.
    path : str
        Destination file path.

    Raises
    ------
    IOError
        If the mesh cannot be written.
    TypeError
        If ``mesh`` is not a ``trimesh.Trimesh`` instance.
    """
    if not isinstance(mesh, trimesh.Trimesh):
        raise TypeError("mesh must be a trimesh.Trimesh instance")

    file_path = Path(path)
    try:
        mesh.export(file_path)
    except FileNotFoundError:
        raise IOError(f"Directory does not exist for path: {path}") from None
    except Exception as exc:  # pragma: no cover - rely on trimesh exceptions
        raise IOError(f"Could not write mesh to {path}") from exc

