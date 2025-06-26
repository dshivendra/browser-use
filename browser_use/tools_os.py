# @file purpose: define tool specs for OS interaction
"""Tool specifications for general OS operations.

Executing shell commands can be dangerous if user input is passed directly to
the shell. ``ShellCommandParams`` performs basic validation and rejects commands
containing common shell control characters to reduce the risk of command
injection. This validation is not a guarantee of safety, so never execute
commands from an untrusted source without additional precautions.
"""

from __future__ import annotations

import os
import signal
import subprocess
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from agentic_os import ToolSpec, register_spec
from browser_use.agent.views import ActionResult

# Characters that should not appear in a shell command for safety
_DISALLOWED_SHELL_CHARS = {";", "|", "&", "`", "$", ">", "<"}


class ShellCommandParams(BaseModel):
    """Parameters for run_shell_command."""

    command: str = Field(description="Command to execute in the shell")

    @field_validator("command")
    @classmethod
    def _validate_command(cls, v: str) -> str:
        if any(ch in v for ch in _DISALLOWED_SHELL_CHARS):
            raise ValueError(
                "Command contains unsafe characters; disallowed: ; | & ` $ > <"
            )
        return v


def run_shell_command(params: ShellCommandParams) -> ActionResult:
    """Execute a shell command and return stdout/stderr."""
    try:
        completed = subprocess.run(
            params.command, shell=True, check=False, capture_output=True, text=True
        )
        output = completed.stdout + completed.stderr
        return ActionResult(extracted_content=output, include_in_memory=True)
    except Exception as e:  # pragma: no cover - safeguard
        return ActionResult(error=str(e), include_in_memory=True)


class FilePathParams(BaseModel):
    """Parameters for file path operations."""

    path: str = Field(description="Path on the local filesystem")


def read_file(params: FilePathParams) -> ActionResult:
    """Read a file from disk."""
    try:
        with open(params.path, "r", encoding="utf-8") as f:
            data = f.read()
        return ActionResult(extracted_content=data, include_in_memory=True)
    except Exception as e:  # pragma: no cover - simple wrapper
        return ActionResult(error=str(e), include_in_memory=True)


def list_directory(params: FilePathParams) -> ActionResult:
    """List contents of a directory."""
    try:
        files = os.listdir(params.path)
        return ActionResult(
            extracted_content="\n".join(sorted(files)), include_in_memory=True
        )
    except Exception as e:  # pragma: no cover
        return ActionResult(error=str(e), include_in_memory=True)


class ManageProcessParams(BaseModel):
    """Parameters for manage_process."""

    action: str = Field(description="'start' or 'stop'")
    command: Optional[str] = Field(None, description="Command to run when starting")
    pid: Optional[int] = Field(None, description="PID of the process to stop")


def manage_process(params: ManageProcessParams) -> ActionResult:
    """Start or stop a process."""
    try:
        if params.action == "start" and params.command:
            proc = subprocess.Popen(params.command, shell=True)
            return ActionResult(
                extracted_content=f"Started process {proc.pid}",
                long_term_memory=str(proc.pid),
                include_in_memory=True,
            )
        if params.action == "stop" and params.pid is not None:
            os.kill(params.pid, signal.SIGTERM)
            return ActionResult(
                extracted_content=f"Stopped process {params.pid}",
                include_in_memory=True,
            )
        return ActionResult(error="Invalid parameters", include_in_memory=True)
    except Exception as e:  # pragma: no cover
        return ActionResult(error=str(e), include_in_memory=True)


# Register tool specifications -------------------------------------------------
register_spec(
    ToolSpec(
        id="run_shell_command",
        description="Run a shell command on the local OS and return output",
        input_model=ShellCommandParams,
        output_model=ActionResult,
        func=run_shell_command,
    )
)

register_spec(
    ToolSpec(
        id="read_os_file",
        description="Read a file from the local OS",  # avoid collision with browser action
        input_model=FilePathParams,
        output_model=ActionResult,
        func=read_file,
    )
)

register_spec(
    ToolSpec(
        id="list_directory",
        description="List contents of a directory on the local OS",
        input_model=FilePathParams,
        output_model=ActionResult,
        func=list_directory,
    )
)

register_spec(
    ToolSpec(
        id="manage_process",
        description="Start or stop a process by pid or command",
        input_model=ManageProcessParams,
        output_model=ActionResult,
        func=manage_process,
    )
)

__all__ = [
    "run_shell_command",
    "read_file",
    "list_directory",
    "manage_process",
]

