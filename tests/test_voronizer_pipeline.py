import pytest

from app.voronizer import PipelineConfig, run_pipeline
import app.voronizer.main as main


def test_pipeline_config_defaults():
    config = PipelineConfig()
    assert config.MODEL is True
    assert config.SUPPORT is False
    assert config.RESOLUTION == 300


def test_pipeline_config_override():
    config = PipelineConfig(MODEL=False, SUPPORT=True, NET_THICKNESS=10)
    assert not config.MODEL
    assert config.SUPPORT is True
    assert config.NET_THICKNESS == 10


def test_run_pipeline_calls_main(tmp_path, monkeypatch):
    output_file = tmp_path / "result.txt"
    captured = {}

    def fake_main(config):
        captured["primitive"] = config.PRIMITIVE_TYPE
        output_file.write_text("done")

    monkeypatch.setattr(main, "main", fake_main)
    cfg = PipelineConfig(PRIMITIVE_TYPE="Cube", RESOLUTION=8, TPB=1)
    run_pipeline(cfg)
    assert output_file.exists()
    assert captured["primitive"] == "Cube"


def test_run_pipeline_invalid_config(capsys):
    cfg = PipelineConfig(MODEL=False, SUPPORT=False)
    run_pipeline(cfg)
    captured = capsys.readouterr()
    assert "You need at least the model or the support structure." in captured.out

