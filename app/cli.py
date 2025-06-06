"""Command-line interface for Cristify STL."""

from __future__ import annotations

import argparse
from typing import Sequence

from app.core.io import load_mesh, save_mesh
from app.core.cristify import cristify_mesh


def parse_args(args: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Cristify an STL mesh")
    parser.add_argument("--input", required=True, help="Path to input STL file")
    parser.add_argument(
        "--output", required=True, help="Destination path for transformed mesh"
    )
    parser.add_argument(
        "--amount",
        type=float,
        default=1.0,
        help="Cristify amount scale factor",
    )
    return parser.parse_args(args)


def main(args: Sequence[str] | None = None) -> int:
    opts = parse_args(args)

    mesh = load_mesh(opts.input)
    result = cristify_mesh(mesh, amount=opts.amount)
    save_mesh(result, opts.output)
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
