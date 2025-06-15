from app.cli import parse_args


def test_voronize_parse():
    opts = parse_args([
        "voronize",
        "--file-name",
        "sample.stl",
        "--model",
    ])
    assert opts.command == "voronize"
    assert opts.file_name == "sample.stl"
    assert opts.model is True
