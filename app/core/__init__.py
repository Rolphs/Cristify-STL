"""Core functionality for Cristify STL."""

from .intervention import analyze_mesh
from .cristify import cristify_mesh
from .mesh_utils import repair_mesh, make_watertight, repair_until_watertight
from .fractal import generate_fractal_geometry
from .gaudify import (
    get_overhang_faces,
    modify_overhangs,
    gaudify_mesh,
    reorient_mesh_for_printing,
)
from .wrap import wrap_mesh
from .simplify import simplify_mesh

__all__ = [
    "analyze_mesh",
    "cristify_mesh",
    "repair_mesh",
    "make_watertight",
    "repair_until_watertight",
    "generate_fractal_geometry",
    "gaudify_mesh",
    "get_overhang_faces",
    "modify_overhangs",
    "reorient_mesh_for_printing",
    "wrap_mesh",
    "simplify_mesh",
]
