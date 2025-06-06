import trimesh

from app.core import analyze_mesh


def test_analyze_mesh_box():
    mesh = trimesh.primitives.Box()
    result = analyze_mesh(mesh)
    assert isinstance(result, dict)
    assert result["has_holes"] is False
    assert 0.0 <= result["intervention_score"] <= 1.0
