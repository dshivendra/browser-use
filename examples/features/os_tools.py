import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dotenv import load_dotenv

load_dotenv()

import browser_use.tools_os  # registers OS tool specs
from agentic_os.browser_use import Agent
from agentic_os.browser_use.llm import ChatOpenAI


async def main() -> None:
    agent = Agent(
        task="Run 'echo hello' using run_shell_command then list the current directory.",
        llm=ChatOpenAI(model="gpt-4o"),
    )
    await agent.run()


if __name__ == "__main__":
    asyncio.run(main())
