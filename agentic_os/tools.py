from dataclasses import dataclass
from typing import Any, Callable, Dict, Type

from pydantic import BaseModel


@dataclass
class ToolSpec:
    id: str
    description: str
    input_model: Type[BaseModel]
    output_model: Type[BaseModel]
    func: Callable[..., Any] | None = None


_registry: Dict[str, ToolSpec] = {}


def register_spec(spec: ToolSpec) -> None:
    """Register a tool specification."""
    _registry[spec.id] = spec


def get_registry() -> Dict[str, ToolSpec]:
    return _registry
