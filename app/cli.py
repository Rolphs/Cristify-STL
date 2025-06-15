"""Command-line interface for Cristify STL and Voronizer."""

from __future__ import annotations

import argparse
from typing import Sequence

from app.core.io import load_mesh, save_mesh
from app.core.cristify import cristify_mesh
from app.voronizer import PipelineConfig, run_pipeline


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
        config = PipelineConfig(
            FILE_NAME=opts.file_name,
            PRIMITIVE_TYPE=opts.primitive_type,
            RESOLUTION=opts.resolution,
            TPB=opts.tpb,
            MODEL=opts.model,
            SUPPORT=opts.support,
        )
        run_pipeline(config)
    else:
        raise ValueError("Unknown command")
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
