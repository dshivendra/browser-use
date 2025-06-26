"""Loader for agentic OS configuration."""

import os
from pathlib import Path

import yaml
from pydantic import BaseModel


class AgenticOSConfig(BaseModel):
	"""Settings loaded from ``agentic_os.yaml``."""

	planner_model: str | None = None
	memory_backend: str | None = None
	toolhub_endpoint: str | None = None


DEFAULT_CONFIG_PATH = Path(os.getenv('AGENTIC_OS_CONFIG', 'agentic_os.yaml'))


def load_agentic_os_config(path: str | Path | None = None) -> AgenticOSConfig:
	"""Load agentic OS settings from a YAML file."""
	cfg_path = Path(path) if path else DEFAULT_CONFIG_PATH
	if not cfg_path.is_file():
	    return AgenticOSConfig()
	with cfg_path.open() as f:
	    data = yaml.safe_load(f) or {}
	if not isinstance(data, dict):
	    return AgenticOSConfig()
	return AgenticOSConfig(**data)


AGENTIC_OS_CONFIG = load_agentic_os_config()
