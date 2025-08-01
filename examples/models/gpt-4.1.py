"""
Simple try of the agent.

@dev You need to add OPENAI_API_KEY to your environment variables.
"""

import asyncio

from dotenv import load_dotenv
from lmnr import Laminar

from agentic_os.browser_use import Agent
from agentic_os.browser_use.llm import ChatOpenAI

load_dotenv()


Laminar.initialize()

# All the models are type safe from OpenAI in case you need a list of supported models
llm = ChatOpenAI(model='gpt-4.1')
agent = Agent(
	task='Go to amazon.com, search for laptop, sort by best rating, and give me the price of the first result',
	llm=llm,
)


async def main():
	await agent.run(max_steps=10)
	input('Press Enter to continue...')


asyncio.run(main())
