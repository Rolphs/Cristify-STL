import pytest
import numpy as np
import trimesh

from app.core import cristify_mesh


def test_cristify_box_basic():
    mesh = trimesh.primitives.Box(extents=(1, 1, 1))
    original_min_z = mesh.vertices[:, 2].min()
    original_max_z = mesh.vertices[:, 2].max()

    result = cristify_mesh(mesh, amount=1.0)

    # original mesh should remain unchanged
    assert mesh.vertices[:, 2].min() == pytest.approx(original_min_z)
    assert mesh.vertices[:, 2].max() == pytest.approx(original_max_z)

    # transformed mesh
    assert isinstance(result, trimesh.Trimesh)
    assert result is not mesh

    assert result.vertices[:, 2].max() == pytest.approx(original_max_z)
    expected_min = original_min_z - (original_max_z - original_min_z)
    assert result.vertices[:, 2].min() == pytest.approx(expected_min)


def test_cristify_zero_amount():
    mesh = trimesh.primitives.Box(extents=(1, 1, 1))
    result = cristify_mesh(mesh, amount=0.0)
    assert np.allclose(mesh.vertices, result.vertices)


def test_cristify_axis_y():
    mesh = trimesh.primitives.Box(extents=(1, 1, 1))
    original_min_y = mesh.vertices[:, 1].min()
    original_max_y = mesh.vertices[:, 1].max()

    result = cristify_mesh(mesh, amount=1.0, axis="y")

    assert result.vertices[:, 1].max() == pytest.approx(original_max_y)
    expected_min = original_min_y - (original_max_y - original_min_y)
    assert result.vertices[:, 1].min() == pytest.approx(expected_min)


def test_cristify_with_floor():
    mesh = trimesh.primitives.Box(extents=(1, 1, 1))
    floor = -0.25
    result = cristify_mesh(mesh, amount=1.0, floor=floor)
    assert result.vertices[:, 2].min() >= floor
