"""Tests for portable input/output handling in the voronizer pipeline."""

import numpy as np
import pytest
import trimesh

from app.cli import parse_args
from app.voronizer import PipelineConfig, run_pipeline
from app.voronizer.main import resolve_input, resolve_output_dir


@pytest.fixture(autouse=True)
def headless(monkeypatch):
    monkeypatch.setenv("CRISTIFY_FORCE_CPU", "1")
    monkeypatch.setenv("MPLBACKEND", "Agg")


def _write_box_stl(path):
    mesh = trimesh.creation.box(extents=(10, 10, 10))
    mesh.export(str(path))
    return path


def test_resolve_input_accepts_path(tmp_path):
    stl = _write_box_stl(tmp_path / "box.stl")
    assert resolve_input(str(stl)) == str(stl)


def test_resolve_input_missing_file():
    with pytest.raises(FileNotFoundError):
        resolve_input("definitely_not_there.stl")


def test_resolve_output_dir_creates_custom_dir(tmp_path):
    out = tmp_path / "my_output"
    cfg = PipelineConfig(OUTPUT_DIR=str(out))
    assert resolve_output_dir(cfg) == str(out)
    assert out.is_dir()


def test_resolve_output_dir_defaults_to_cwd(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    cfg = PipelineConfig()
    result = resolve_output_dir(cfg)
    assert result == str(tmp_path / "Output")
    assert (tmp_path / "Output").is_dir()


def test_missing_input_reports_error(tmp_path, capsys):
    cfg = PipelineConfig(FILE_NAME="missing.stl", MODEL=True,
                         OUTPUT_DIR=str(tmp_path))
    run_pipeline(cfg)
    assert "Input file not found" in capsys.readouterr().out


def test_cli_parses_io_flags():
    opts = parse_args([
        "voronize",
        "--file-name", "/tmp/model.stl",
        "--model",
        "--output-dir", "/tmp/out",
        "--export",
        "--export-name", "result",
    ])
    assert opts.file_name == "/tmp/model.stl"
    assert opts.output_dir == "/tmp/out"
    assert opts.export is True
    assert opts.export_name == "result"


def test_pipeline_exports_ply_to_custom_dir(tmp_path):
    """Full non-interactive pipeline run from an arbitrary STL path."""
    import matplotlib
    matplotlib.use("Agg")
    np.random.seed(0)
    stl = _write_box_stl(tmp_path / "box.stl")
    out = tmp_path / "results"
    cfg = PipelineConfig(
        FILE_NAME=str(stl),
        MODEL=True,
        RESOLUTION=24,
        MODEL_THRESH=50,
        EXPORT_MESH=True,
        OUTPUT_DIR=str(out),
    )
    run_pipeline(cfg)
    assert (out / "box_Voronoi.ply").is_file()
