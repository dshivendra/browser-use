from pytest import raises

from agentic_os.kernel.access import AccessManager


def test_basic_permissions(caplog):
	mgr = AccessManager({"a": ["tool"]})
	assert mgr.is_allowed("a", "tool")
	assert not mgr.is_allowed("a", "other")

	mgr.grant("a", "other")
	assert mgr.is_allowed("a", "other")

	mgr.revoke("a", "tool")
	assert not mgr.is_allowed("a", "tool")


def test_ensure_allowed():
	mgr = AccessManager({"a": ["t"]})
	mgr.ensure_allowed("a", "t")
	with raises(PermissionError):
		mgr.ensure_allowed("a", "x")
