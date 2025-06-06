"""Main GUI for Cristify STL using DearPyGui."""

from __future__ import annotations

from dearpygui import dearpygui as dpg

from app.core.io import load_mesh
from .viewer import show_mesh


def _file_selected(sender: int, app_data: dict[str, str]) -> None:
    """Callback when a file is chosen from the dialog."""
    path = app_data.get("file_path_name")
    if path:
        mesh = load_mesh(path)
        show_mesh(mesh)


def create_main_window() -> None:
    """Create the main application window."""
    with dpg.window(label="Cristify STL", tag="main_window"):
        dpg.add_button(label="Load STL", callback=lambda: dpg.show_item("file_dialog"))

    with dpg.file_dialog(
        directory_selector=False,
        show=False,
        callback=_file_selected,
        tag="file_dialog",
    ):
        dpg.add_file_extension(".stl", color=(150, 255, 150, 255))


def main() -> int:
    """Launch the GUI application."""
    dpg.create_context()
    create_main_window()
    dpg.create_viewport(title="Cristify STL")
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()
    return 0


if __name__ == "__main__":  # pragma: no cover - GUI entry point
    raise SystemExit(main())
