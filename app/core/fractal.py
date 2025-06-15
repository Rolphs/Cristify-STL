"""Fractal geometry utilities."""

from __future__ import annotations

from typing import Iterable, Sequence, Tuple

import numpy as np


def generate_fractal_geometry(
    vertices: np.ndarray,
    edges: Iterable[Sequence[int]],
    iterations: int = 1,
) -> Tuple[np.ndarray, list[Tuple[int, int]]]:
    """Iteratively insert midpoints for each edge.

    Parameters
    ----------
    vertices:
        Array of vertex coordinates.
    edges:
        Iterable of edges defined by pairs of vertex indices.
    iterations:
        Number of subdivision passes to run.

    Returns
    -------
    numpy.ndarray
        The new array of vertices containing any newly added points.
    list of tuple[int, int]
        The original ``edges`` as a list of pairs.
    """

    if not isinstance(vertices, np.ndarray):
        raise TypeError("vertices must be a numpy array")

    edge_pairs = [tuple(map(int, e)) for e in edges]
    new_vertices = vertices.astype(float).tolist()

    for _ in range(iterations):
        edge_to_new = {}
        for edge in edge_pairs:
            ordered = tuple(sorted(edge))
            if ordered not in edge_to_new:
                midpoint = (vertices[ordered[0]] + vertices[ordered[1]]) / 2.0
                edge_to_new[ordered] = len(new_vertices)
                new_vertices.append(midpoint)
        vertices = np.asarray(new_vertices, dtype=float)

    return np.asarray(new_vertices, dtype=float), edge_pairs


__all__ = ["generate_fractal_geometry"]
