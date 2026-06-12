"""Basic DearPyGui interface for Cristify STL.

This module wires together a minimal workflow:

1. Load an STL file.
2. Apply :func:`cristify_mesh` to the mesh.
3. Save the result.

The interface deliberately keeps functionality simple.  It relies on the
``MeshViewer`` from :mod:`app.gui.viewer` to show a small preview of the
current mesh.  The goal is to demonstrate interaction rather than provide
an advanced editor.
"""

from __future__ import annotations

import dearpygui.dearpygui as dpg

from app.core.cristify import cristify_mesh
from app.core.io import load_mesh, save_mesh
from app.core import (
    repair_mesh,
    make_watertight,
    analyze_mesh,
    gaudify_mesh,
    wrap_mesh,
    simplify_mesh,
)
from app.core.texturize import make_organic_with_gravity
from app.gui.viewer import MeshViewer
from app.voronizer import PipelineConfig, run_pipeline

_current_mesh = None
_viewer: MeshViewer


def _open_load_dialog() -> None:
    dpg.show_item("load_dialog")


def _open_save_dialog() -> None:
    dpg.show_item("save_dialog")


def _on_load_dialog(sender, app_data: dict) -> None:  # pragma: no cover - UI
    global _current_mesh
    try:
        path = app_data.get("file_path_name")
        if path:
            _current_mesh = load_mesh(path)
            _viewer.set_mesh(_current_mesh)
    except Exception as exc:  # pragma: no cover - debug output
        print(f"Failed to load mesh: {exc}")


def _on_save_dialog(sender, app_data: dict) -> None:  # pragma: no cover - UI
    if _current_mesh is None:
        return
    try:
        path = app_data.get("file_path_name")
        if path:
            save_mesh(_current_mesh, path)
    except Exception as exc:  # pragma: no cover - debug output
        print(f"Failed to save mesh: {exc}")


def _apply_cristify() -> None:  # pragma: no cover - UI
    global _current_mesh
    if _current_mesh is None:
        return
    _current_mesh = cristify_mesh(
        _current_mesh,
        amount=dpg.get_value("cristify_amount"),
        axis=dpg.get_value("cristify_axis"),
    )
    _viewer.set_mesh(_current_mesh)


def _open_voronize_dialog() -> None:
    dpg.show_item("voro_dialog")


def _run_voronize(sender, app_data, user_data) -> None:  # pragma: no cover - UI
    config = PipelineConfig(
        FILE_NAME=dpg.get_value("voro_file"),
        MODEL=True,
        RESOLUTION=dpg.get_value("voro_resolution"),
        OUTPUT_DIR=dpg.get_value("voro_output_dir"),
        EXPORT_MESH=dpg.get_value("voro_export"),
    )
    run_pipeline(config)


def _apply_repair() -> None:  # pragma: no cover - UI
    """Repair the current mesh."""
    global _current_mesh
    if _current_mesh is None:
        return
    if dpg.get_value("repair_watertight"):
        _current_mesh = make_watertight(_current_mesh)
    else:
        _current_mesh = repair_mesh(_current_mesh)
    _viewer.set_mesh(_current_mesh)


def _analyze_current() -> None:  # pragma: no cover - UI
    if _current_mesh is None:
        return
    metrics = analyze_mesh(_current_mesh)
    text = "\n".join(f"{k}: {v}" for k, v in metrics.items())
    dpg.set_value("analysis_text", text)
    dpg.show_item("analysis_dialog")


def _apply_transform() -> None:  # pragma: no cover - UI
    global _current_mesh
    if _current_mesh is None:
        return
    op = dpg.get_value("transform_combo")
    if op == "Gaudify":
        _current_mesh = gaudify_mesh(
            _current_mesh,
            max_overhang_angle=dpg.get_value("gaudify_angle"),
            max_iterations=dpg.get_value("gaudify_iterations"),
        )
    elif op == "Simplify":
        _current_mesh = simplify_mesh(
            _current_mesh, target_reduction=dpg.get_value("simplify_reduction")
        )
    elif op == "Wrap":
        _current_mesh = wrap_mesh(
            _current_mesh, wrap_thickness=dpg.get_value("wrap_thickness")
        )
    elif op == "Texturize":
        _current_mesh = make_organic_with_gravity(
            _current_mesh,
            noise_strength=dpg.get_value("texturize_noise"),
            smooth_iterations=dpg.get_value("texturize_smooth"),
            g=dpg.get_value("texturize_gravity"),
        )
    _viewer.set_mesh(_current_mesh)


_TRANSFORM_GROUPS = {
    "Gaudify": "gaudify_params",
    "Simplify": "simplify_params",
    "Wrap": "wrap_params",
    "Texturize": "texturize_params",
}


def _on_transform_changed(sender, app_data) -> None:  # pragma: no cover - UI
    """Show only the parameter group of the selected transform."""
    for op, group in _TRANSFORM_GROUPS.items():
        if op == app_data:
            dpg.show_item(group)
        else:
            dpg.hide_item(group)


def main() -> None:  # pragma: no cover - manual run
    """Launch the GUI application."""

    dpg.create_context()

    global _viewer
    _viewer = MeshViewer()

    with dpg.window(label="Cristify STL", width=300, height=560):
        dpg.add_button(label="Load STL", callback=_open_load_dialog)
        dpg.add_separator()
        dpg.add_slider_float(
            label="Amount", tag="cristify_amount",
            default_value=1.0, min_value=0.0, max_value=2.0,
        )
        dpg.add_combo(
            ["x", "y", "z"], label="Axis", tag="cristify_axis", default_value="z"
        )
        dpg.add_button(label="Apply Cristify", callback=_apply_cristify)
        dpg.add_separator()
        dpg.add_button(label="Voronize", callback=_open_voronize_dialog)
        dpg.add_button(label="Repair", callback=_apply_repair)
        dpg.add_checkbox(label="Watertight", tag="repair_watertight")
        dpg.add_button(label="Analyze", callback=_analyze_current)
        dpg.add_separator()
        dpg.add_combo(
            ["Gaudify", "Simplify", "Wrap", "Texturize"],
            tag="transform_combo",
            default_value="Gaudify",
            callback=_on_transform_changed,
        )
        with dpg.group(tag="gaudify_params"):
            dpg.add_slider_float(
                label="Max overhang angle", tag="gaudify_angle",
                default_value=45.0, min_value=10.0, max_value=80.0,
            )
            dpg.add_slider_int(
                label="Max iterations", tag="gaudify_iterations",
                default_value=10, min_value=1, max_value=50,
            )
        with dpg.group(tag="simplify_params", show=False):
            dpg.add_slider_float(
                label="Reduction", tag="simplify_reduction",
                default_value=0.5, min_value=0.05, max_value=0.95,
            )
        with dpg.group(tag="wrap_params", show=False):
            dpg.add_slider_float(
                label="Thickness", tag="wrap_thickness",
                default_value=0.1, min_value=0.01, max_value=1.0,
            )
        with dpg.group(tag="texturize_params", show=False):
            dpg.add_slider_float(
                label="Noise strength", tag="texturize_noise",
                default_value=0.01, min_value=0.0, max_value=0.1,
            )
            dpg.add_slider_int(
                label="Smooth iterations", tag="texturize_smooth",
                default_value=200, min_value=0, max_value=500,
            )
            dpg.add_input_float(
                label="Gravity", tag="texturize_gravity",
                default_value=1e-3, step=1e-3, format="%.4f",
            )
        dpg.add_button(label="Apply Transform", callback=_apply_transform)
        dpg.add_separator()
        dpg.add_button(label="Save STL", callback=_open_save_dialog)

    with dpg.file_dialog(
        directory_selector=False,
        callback=_on_load_dialog,
        show=False,
        tag="load_dialog",
    ):
        dpg.add_file_extension(".stl", color=(0, 255, 0, 255))

    with dpg.file_dialog(
        directory_selector=False,
        callback=_on_save_dialog,
        show=False,
        tag="save_dialog",
        default_filename="cristified.stl",
    ):
        dpg.add_file_extension(".stl", color=(0, 255, 0, 255))

    with dpg.window(label="Voronize", modal=True, show=False, tag="voro_dialog"):
        dpg.add_input_text(label="STL file path", tag="voro_file")
        dpg.add_input_int(
            label="Resolution", tag="voro_resolution", default_value=300,
            min_value=16, max_value=600, min_clamped=True, max_clamped=True,
        )
        dpg.add_input_text(
            label="Output dir", tag="voro_output_dir",
            hint="default: ./Output",
        )
        dpg.add_checkbox(label="Export .ply", tag="voro_export", default_value=True)
        dpg.add_button(label="Run", callback=_run_voronize)

    with dpg.window(label="Analysis", modal=True, show=False, tag="analysis_dialog"):
        dpg.add_text(tag="analysis_text")
        dpg.add_button(label="Close", callback=lambda: dpg.hide_item("analysis_dialog"))

    dpg.create_viewport(title="Cristify STL", width=800, height=600)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    _viewer.show()
    dpg.start_dearpygui()
    dpg.destroy_context()


if __name__ == "__main__":  # pragma: no cover - manual launch
    main()
