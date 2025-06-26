---
title: "Migration to Agentic OS"
description: "Enable the Agentic OS module and configure OS-level actions"
icon: "gear"
---

Browser Use now ships with an optional **Agentic OS** module. This module lets agents execute actions that interact with the operating system such as manipulating files or launching local applications.

## Enabling Agentic OS

1. Create an `agentic_os.yaml` file at the root of your project:

```yaml
planner_model: gpt-4o
memory_backend: vector_db
toolhub_endpoint: https://toolhub.example.com
```

2. Start your agent normally. The configuration will be loaded automatically. If the file lives somewhere else, set the `AGENTIC_OS_CONFIG` environment variable to the YAML path:

```bash
export AGENTIC_OS_CONFIG=/path/to/agentic_os.yaml
```

## Security Considerations

<Warning>
Enabling OS-level actions gives the agent permission to run commands on your machine. Only enable this module in environments you trust and never expose the configuration file containing your credentials publicly.
</Warning>

