# Migrating to `agentic_os`

The `browser_use` package can now be accessed as `agentic_os.browser_use`.
Existing imports such as:

```python
from browser_use import Agent
```

should be updated to:

```python
from agentic_os.browser_use import Agent
```

The previous `browser_use` namespace remains available for backward
compatibility, so existing code will continue to run without changes.
