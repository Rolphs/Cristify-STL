"""Example invoking :func:`app.core.mesh_utils.repair_until_watertight`."""

import trimesh
from app.core.mesh_utils import repair_until_watertight

if __name__ == "__main__":
    mesh = trimesh.creation.box()
    broken = mesh.copy()
    broken.faces = broken.faces[:-1]
    fixed = repair_until_watertight(broken, max_time_seconds=1)
    print(f"Watertight: {fixed.is_watertight}")
