"""Minimal DearPyGui based 3D viewer.

This module provides a :class:`MeshViewer` used by ``main_gui.py`` to
display a very small preview of the currently loaded mesh.  It avoids
any heavyweight OpenGL features so it can run in constrained
environments where a full graphics stack may not be available.  The
viewer simply projects mesh triangles onto the XY plane after applying
a small rotation.  The result is drawn using DearPyGui's draw list
API.  The implementation is intentionally lightweight but gives a
useful approximation of the model inside the GUI.
"""

from __future__ import annotations

from typing import Optional

import numpy as np
import dearpygui.dearpygui as dpg
import trimesh


class MeshViewer:
    """Very small helper to render a mesh inside a DearPyGui drawlist."""

    def __init__(self, *, tag: str = "viewer_window", size: int = 400) -> None:
        self._mesh: Optional[trimesh.Trimesh] = None
        self._rotation: float = 0.0
        self.size = size

        with dpg.window(label="Preview", tag=tag):
            self.drawlist = dpg.add_drawlist(width=size, height=size)
        self.window_tag = tag

    # ------------------------------------------------------------------
    def set_mesh(self, mesh: trimesh.Trimesh) -> None:
        """Set the mesh to display and redraw."""

        self._mesh = mesh
        self._rotation = 0.0
        self._draw()

    # ------------------------------------------------------------------
    def rotate(self, degrees: float) -> None:
        """Rotate the preview and redraw."""

        if self._mesh is None:
            return
        self._rotation += float(degrees)
        self._draw()

    # ------------------------------------------------------------------
    def show(self) -> None:
        """Make sure the preview window is visible."""

        dpg.show_item(self.window_tag)

    # ------------------------------------------------------------------
    def _draw(self) -> None:
        """Internal helper to draw the projected mesh."""

        dpg.delete_item(self.drawlist, children_only=True)
        if self._mesh is None or self._mesh.vertices.size == 0:
            return

        verts = self._mesh.vertices
        faces = self._mesh.faces

        angle = np.deg2rad(self._rotation)
        rot = np.array(
            [
                [np.cos(angle), 0.0, np.sin(angle)],
                [0.0, 1.0, 0.0],
                [-np.sin(angle), 0.0, np.cos(angle)],
            ]
        )

        projected = (verts @ rot.T)[:, :2]

        min_xy = projected.min(axis=0)
        max_xy = projected.max(axis=0)
        extent = float(max(max_xy - min_xy))
        if extent == 0.0:
            extent = 1.0
        scale = (self.size - 40) / extent
        offset = (min_xy + max_xy) / 2.0

        projected = (projected - offset) * scale + self.size / 2.0

        for tri in faces:
            pts = projected[tri]
            dpg.draw_triangle(
                self.drawlist,
                *pts[0],
                *pts[1],
                *pts[2],
                color=(200, 200, 200, 255),
                fill=(100, 150, 230, 100),
            )

