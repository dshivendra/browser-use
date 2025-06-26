import pytest

from browser_use.agent.memory_adapter import BrowserMemory


class TestBrowserMemory:
    async def test_store_and_retrieve(self):
        mem = BrowserMemory()
        await mem.store('one')
        await mem.store('two')
        all_entries = await mem.retrieve()
        assert [e.text for e in all_entries] == ['one', 'two']
        latest = await mem.retrieve(limit=1)
        assert [e.text for e in latest] == ['two']

    async def test_snapshot(self):
        mem = BrowserMemory()
        await mem.store('a')
        snap = await mem.snapshot()
        assert len(snap) == 1
        assert snap[0].text == 'a'
