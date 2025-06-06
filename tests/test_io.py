import os

import pytest
import trimesh

from app.core.io import load_mesh, save_mesh


def test_load_save_roundtrip(tmp_path):
    mesh = trimesh.primitives.Box()
    path = tmp_path / "box.stl"

    save_mesh(mesh, os.fspath(path))
    loaded = load_mesh(os.fspath(path))

    assert isinstance(loaded, trimesh.Trimesh)
    assert loaded.vertices.shape == mesh.vertices.shape
    assert loaded.faces.shape == mesh.faces.shape


def test_load_missing_file(tmp_path):
    missing = tmp_path / "missing.stl"
    with pytest.raises(FileNotFoundError):
        load_mesh(os.fspath(missing))


def test_save_invalid_directory(tmp_path):
    mesh = trimesh.primitives.Box()
    invalid_path = tmp_path / "no_dir" / "mesh.stl"
    with pytest.raises(IOError):
        save_mesh(mesh, os.fspath(invalid_path))
