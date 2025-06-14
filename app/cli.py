"""Command-line interface for Cristify STL and Voronizer."""

from __future__ import annotations

import argparse
from typing import Sequence

from app.core.io import load_mesh, save_mesh
from app.core.cristify import cristify_mesh
from app.core.mesh_utils import repair_mesh, make_watertight
from app.core import (
    analyze_mesh,
    gaudify_mesh,
    wrap_mesh,
    simplify_mesh,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Cristify STL utilities")
    sub = parser.add_subparsers(dest="command", required=True)

    cristify = sub.add_parser("cristify", help="Cristify an STL mesh")
    cristify.add_argument("--input", required=True, help="Path to input STL file")
    cristify.add_argument("--output", required=True, help="Destination path for transformed mesh")
    cristify.add_argument("--amount", type=float, default=1.0, help="Cristify amount scale factor")
    cristify.add_argument("--axis", default="z", choices=["x", "y", "z"], help="Axis to project along")
    cristify.add_argument("--floor", type=float, default=None, help="Optional minimum coordinate after projection")

    voro = sub.add_parser("voronize", help="Run Voronizer pipeline")
    voro.add_argument("--file-name", default="", help="STL file name inside Input folder")
    voro.add_argument("--primitive-type", default="", help="Primitive shape type")
    voro.add_argument("--resolution", type=int, default=300)
    voro.add_argument("--tpb", type=int, default=8)
    voro.add_argument("--model", action="store_true", default=False)
    voro.add_argument("--support", action="store_true", default=False)

    repair = sub.add_parser("repair", help="Repair a mesh")
    repair.add_argument("--input", required=True, help="Path to input mesh file")
    repair.add_argument("--output", required=True, help="Destination path for repaired mesh")
    repair.add_argument("--watertight", action="store_true", default=False, help="Fill holes to make mesh watertight")

    analyze = sub.add_parser("analyze", help="Analyze a mesh")
    analyze.add_argument("--input", required=True, help="Path to input mesh file")

    gaudi = sub.add_parser("gaudify", help="Gaudify a mesh to reduce overhangs")
    gaudi.add_argument("--input", required=True, help="Path to input mesh file")
    gaudi.add_argument("--output", required=True, help="Destination path for processed mesh")
    gaudi.add_argument("--angle", type=float, default=45.0, help="Maximum overhang angle")
    gaudi.add_argument("--iterations", type=int, default=10, help="Maximum iterations")

    wrap = sub.add_parser("wrap", help="Offset mesh vertices outward")
    wrap.add_argument("--input", required=True, help="Path to input mesh file")
    wrap.add_argument("--output", required=True, help="Destination path for processed mesh")
    wrap.add_argument("--thickness", type=float, default=0.1, help="Offset distance")

    simp = sub.add_parser("simplify", help="Simplify a mesh")
    simp.add_argument("--input", required=True, help="Path to input mesh file")
    simp.add_argument("--output", required=True, help="Destination path for processed mesh")
    simp.add_argument("--reduction", type=float, default=0.5, help="Fraction of faces to remove")

    return parser


def parse_args(args: Sequence[str] | None = None) -> argparse.Namespace:
    return build_parser().parse_args(args)


def main(args: Sequence[str] | None = None) -> int:
    opts = parse_args(args)

    if opts.command == "cristify":
        mesh = load_mesh(opts.input)
        result = cristify_mesh(mesh, amount=opts.amount, axis=opts.axis, floor=opts.floor)
        save_mesh(result, opts.output)
    elif opts.command == "voronize":
        from app.voronizer import PipelineConfig, run_pipeline  # lazy import

        config = PipelineConfig(
            FILE_NAME=opts.file_name,
            PRIMITIVE_TYPE=opts.primitive_type,
            RESOLUTION=opts.resolution,
            TPB=opts.tpb,
            MODEL=opts.model,
            SUPPORT=opts.support,
        )
        run_pipeline(config)
    elif opts.command == "repair":
        mesh = load_mesh(opts.input)
        if opts.watertight:
            result = make_watertight(mesh)
        else:
            result = repair_mesh(mesh)
        save_mesh(result, opts.output)
    elif opts.command == "analyze":
        mesh = load_mesh(opts.input)
        analysis = analyze_mesh(mesh)
        print(analysis)
    elif opts.command == "gaudify":
        mesh = load_mesh(opts.input)
        result = gaudify_mesh(
            mesh,
            max_overhang_angle=opts.angle,
            max_iterations=opts.iterations,
        )
        save_mesh(result, opts.output)
    elif opts.command == "wrap":
        mesh = load_mesh(opts.input)
        result = wrap_mesh(mesh, wrap_thickness=opts.thickness)
        save_mesh(result, opts.output)
    elif opts.command == "simplify":
        mesh = load_mesh(opts.input)
        result = simplify_mesh(mesh, target_reduction=opts.reduction)
        save_mesh(result, opts.output)
    else:
        raise ValueError("Unknown command")
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
