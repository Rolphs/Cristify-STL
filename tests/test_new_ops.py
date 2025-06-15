import subprocess
import sys
import trimesh
import numpy as np

from app.core.gaudify import gaudify_mesh
from app.core.wrap import wrap_mesh
from app.core.simplify import simplify_mesh
from app.core.io import load_mesh


def test_gaudify_function():
    mesh = trimesh.creation.box()
    result = gaudify_mesh(mesh, max_overhang_angle=45.0, max_iterations=1)
    assert isinstance(result, trimesh.Trimesh)
    assert len(result.faces) >= len(mesh.faces)


def test_wrap_function():
    mesh = trimesh.creation.box()
    wrapped = wrap_mesh(mesh, wrap_thickness=0.05)
    assert not np.allclose(wrapped.vertices, mesh.vertices)
    assert wrapped.faces.shape == mesh.faces.shape


def test_simplify_function():
    mesh = trimesh.creation.icosphere(subdivisions=2)
    simplified = simplify_mesh(mesh, target_reduction=0.5)
    assert simplified.faces.shape[0] < mesh.faces.shape[0]


def test_cli_gaudify(tmp_path):
    input_path = tmp_path / "g_in.stl"
    output_path = tmp_path / "g_out.stl"
    trimesh.creation.box().export(input_path)
    subprocess.check_call([
        sys.executable,
        "-m",
        "app.cli",
        "gaudify",
        "--input",
        str(input_path),
        "--output",
        str(output_path),
    ])
    assert output_path.exists()
    result = load_mesh(str(output_path))
    assert isinstance(result, trimesh.Trimesh)


def test_cli_wrap(tmp_path):
    input_path = tmp_path / "w_in.stl"
    output_path = tmp_path / "w_out.stl"
    trimesh.creation.box().export(input_path)
    subprocess.check_call([
        sys.executable,
        "-m",
        "app.cli",
        "wrap",
        "--input",
        str(input_path),
        "--output",
        str(output_path),
    ])
    assert output_path.exists()


def test_cli_simplify(tmp_path):
    input_path = tmp_path / "s_in.stl"
    output_path = tmp_path / "s_out.stl"
    trimesh.creation.icosphere().export(input_path)
    subprocess.check_call([
        sys.executable,
        "-m",
        "app.cli",
        "simplify",
        "--input",
        str(input_path),
        "--output",
        str(output_path),
        "--reduction",
        "0.5",
    ])
    assert output_path.exists()
