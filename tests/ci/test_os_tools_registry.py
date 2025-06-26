import browser_use.tools_os  # register OS specs
from agentic_os import get_registry
from browser_use.tools_os import (
    ShellCommandParams,
    FilePathParams,
    ManageProcessParams,
)
import pytest
from pydantic import ValidationError


def test_os_tool_specs_registered():
    registry = get_registry()
    assert "run_shell_command" in registry
    assert "read_os_file" in registry
    assert "list_directory" in registry
    assert "manage_process" in registry


def test_os_tool_callable(tmp_path):
    registry = get_registry()
    run_cmd = registry["run_shell_command"].func
    read_file = registry["read_os_file"].func
    list_dir = registry["list_directory"].func

    # create temp file
    f = tmp_path / "example.txt"
    f.write_text("hello")

    # run shell command
    result_cmd = run_cmd(ShellCommandParams(command="echo hi"))
    assert "hi" in result_cmd.extracted_content

    result_read = read_file(FilePathParams(path=str(f)))
    assert result_read.extracted_content == "hello"

    result_list = list_dir(FilePathParams(path=str(tmp_path)))
    assert "example.txt" in result_list.extracted_content


def test_shell_command_validation():
    with pytest.raises(ValidationError):
        ShellCommandParams(command="echo hi; rm -rf /")
