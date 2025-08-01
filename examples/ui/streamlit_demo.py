"""
To use it, you'll need to install streamlit, and run with:

python -m streamlit run streamlit_demo.py

"""

import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from dotenv import load_dotenv

load_dotenv()

import streamlit as st  # type: ignore

from agentic_os.browser_use import Agent
from agentic_os.browser_use.browser import BrowserSession
from agentic_os.browser_use.controller.service import Controller

if os.name == 'nt':
	asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


# Function to get the LLM based on provider
def get_llm(provider: str):
	if provider == 'anthropic':
		from agentic_os.browser_use.llm import ChatAnthropic

		api_key = os.getenv('ANTHROPIC_API_KEY')
		if not api_key:
			st.error('Error: ANTHROPIC_API_KEY is not set. Please provide a valid API key.')
			st.stop()

		return ChatAnthropic(model='claude-3-5-sonnet-20240620', temperature=0.0)
	elif provider == 'openai':
		from agentic_os.browser_use.llm import ChatOpenAI

		api_key = os.getenv('OPENAI_API_KEY')
		if not api_key:
			st.error('Error: OPENAI_API_KEY is not set. Please provide a valid API key.')
			st.stop()

		return ChatOpenAI(model='gpt-4o', temperature=0.0)
	else:
		st.error(f'Unsupported provider: {provider}')
		st.stop()
		return None  # Never reached, but helps with type checking


# Function to initialize the agent
def initialize_agent(query: str, provider: str):
	llm = get_llm(provider)
	controller = Controller()
	browser_session = BrowserSession()

	return Agent(
		task=query,
		llm=llm,  # type: ignore
		controller=controller,
		browser_session=browser_session,
		use_vision=True,
		max_actions_per_step=1,
	), browser_session


# Streamlit UI
st.title('Automated Browser Agent with LLMs 🤖')

query = st.text_input('Enter your query:', 'go to reddit and search for posts about browser-use')
provider = st.radio('Select LLM Provider:', ['openai', 'anthropic'], index=0)

if st.button('Run Agent'):
	st.write('Initializing agent...')
	agent, browser_session = initialize_agent(query, provider)

	async def run_agent():
		with st.spinner('Running automation...'):
			await agent.run(max_steps=25)
		st.success('Task completed! 🎉')

	asyncio.run(run_agent())

	st.button('Close Browser', on_click=lambda: asyncio.run(browser_session.close()))
