import subprocess
import sys

import trimesh

from app.core.io import load_mesh


def test_cli_cristify(tmp_path):
    input_path = tmp_path / "in.stl"
    output_path = tmp_path / "out.stl"

    trimesh.primitives.Box().export(input_path)

    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "app.cli",
            "--input",
            str(input_path),
            "--output",
            str(output_path),
            "--amount",
            "0.5",
        ]
    )

    assert output_path.exists()
    result = load_mesh(str(output_path))
    assert isinstance(result, trimesh.Trimesh)
    original = trimesh.load(str(input_path))
    assert result.vertices[:, 2].min() < original.vertices[:, 2].min()
