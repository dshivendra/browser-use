"""Tests for agentic OS configuration loader."""

from browser_use.agentic_os import load_agentic_os_config


class TestAgenticOSLoader:
	def test_load_from_path(self, tmp_path):
	    cfg = tmp_path / "cfg.yaml"
	    cfg.write_text("planner_model: foo\nmemory_backend: bar\n")
	    loaded = load_agentic_os_config(cfg)
	    assert loaded.planner_model == "foo"
	    assert loaded.memory_backend == "bar"

	def test_env_variable_path(self, tmp_path, monkeypatch):
	    cfg = tmp_path / "env.yaml"
	    cfg.write_text("toolhub_endpoint: http://x.com\n")
	    monkeypatch.setenv("AGENTIC_OS_CONFIG", str(cfg))
	    loaded = load_agentic_os_config()
	    assert loaded.toolhub_endpoint == "http://x.com"
