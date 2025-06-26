from agentic_os.kernel.context import ContextManager
from browser_use.llm.messages import UserMessage


class TestContextManager:
	def test_trim_messages(self):
		cm = ContextManager(max_tokens=5)
		cm.add_message(UserMessage(content='one two'))
		cm.add_message(UserMessage(content='three four five'))
		cm.add_message(UserMessage(content='six seven'))
		msgs = [m.text for m in cm.get_messages()]
		assert msgs == ['three four five', 'six seven']

	def test_snapshot_restore(self):
		cm = ContextManager(max_tokens=5)
		cm.add_message(UserMessage(content='a b c'))
		snap = cm.snapshot()
		cm.add_message(UserMessage(content='d e f'))
		cm.restore(snap)
		msgs = [m.text for m in cm.get_messages()]
		assert msgs == ['a b c']
		assert cm.max_tokens == 5
