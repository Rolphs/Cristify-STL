import numpy as np
import trimesh

from app.core.mesh_utils import (
    repair_mesh,
    make_watertight,
    repair_until_watertight,
)


def test_repair_mesh_removes_degenerate():
    box = trimesh.creation.box()
    mesh = box.copy()
    mesh.faces = np.vstack([mesh.faces, [0, 0, 0]])

    assert len(mesh.faces) == len(box.faces) + 1

    repaired = repair_mesh(mesh)

    assert len(repaired.faces) == len(box.faces)
    # original mesh unchanged
    assert len(mesh.faces) == len(box.faces) + 1


def test_make_watertight_fills_hole():
    box = trimesh.creation.box()
    mesh = box.copy()
    mesh.faces = mesh.faces[:-1]
    assert not mesh.is_watertight

    result = make_watertight(mesh)
    assert result.is_watertight
    # ensure original mesh unchanged
    assert not mesh.is_watertight

def test_repair_until_watertight():
    box = trimesh.creation.box()
    mesh = box.copy()
    mesh.faces = mesh.faces[:-1]
    assert not mesh.is_watertight

    result = repair_until_watertight(mesh, max_time_seconds=1)
    assert result.is_watertight
    assert not mesh.is_watertight
