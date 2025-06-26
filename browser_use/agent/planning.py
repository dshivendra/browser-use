# @file purpose: Planner utilities for generating task strategies.
"""Classes for producing high level plans via language models."""

from __future__ import annotations

import json
import logging
import re

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from browser_use.agent.prompts import PlannerPrompt
from browser_use.exceptions import LLMException
from browser_use.llm.base import BaseChatModel
from browser_use.llm.messages import BaseMessage, UserMessage
from browser_use.utils import time_execution_async

logger = logging.getLogger(__name__)

THINK_TAGS = re.compile(r'<think>.*?</think>', re.DOTALL)
STRAY_CLOSE_TAG = re.compile(r'.*?</think>', re.DOTALL)


class PlannerContext(BaseModel):
"""Context information required for generating plans."""

	model_config = ConfigDict(arbitrary_types_allowed=True)

	llm: BaseChatModel = Field(description='LLM used to generate plans')
	messages: list[BaseMessage] = Field(default_factory=list, description='Message history to provide as context')
	available_actions: str = Field(default='', description='Actions the agent can take')
	is_planner_reasoning: bool = Field(default=False, description='Use chain-of-thought style planner reasoning')
	extend_planner_system_message: str | None = Field(default=None, description='Additional system prompt text')
	use_vision_for_planner: bool = Field(default=True, description='Allow images to be sent to the planner LLM')
	use_vision: bool = Field(default=False, description='Whether image messages are included in messages')


class Plan(BaseModel):
"""Structured plan returned by :class:`BrowserPlanner`."""
	
	state_analysis: str | None = None
	progress_evaluation: str | None = None
	challenges: str | None = None
	next_steps: str | None = None
	reasoning: str | None = None
raw: str = Field(description='Raw plan text returned by the LLM')


class BrowserPlanner:
	"""Utility for generating high level plans."""
	
	def __init__(self, llm: BaseChatModel, *, logger: logging.Logger | None = None):
	self.llm = llm
	self.logger = logger or logging.getLogger(__name__)
	
	async def generate_plan(self, task: str, *, context: PlannerContext) -> Plan:
	"""Generate a plan for ``task`` using the provided context."""
	messages = [
	PlannerPrompt(context.available_actions).get_system_message(
	is_planner_reasoning=context.is_planner_reasoning,
	extended_planner_system_prompt=context.extend_planner_system_message,
	),
	*context.messages,
	]
	
	if not context.use_vision_for_planner and context.use_vision and messages:
	last_state_message: UserMessage = messages[-1]  # type: ignore[assignment]
	new_msg = ''
	if isinstance(last_state_message.content, list):
	for msg in last_state_message.content:
	if msg.type == 'text':
	new_msg += msg.text
	else:
	new_msg = last_state_message.content  # type: ignore[assignment]
	messages[-1] = UserMessage(content=new_msg)
	
	try:
	response = await self.llm.ainvoke(messages)
	except Exception as e:
	status_code = getattr(e, 'status_code', None) or getattr(e, 'code', None) or 500
	self.logger.error(f'Failed to invoke planner: {e}')
	raise LLMException(status_code, f'Planner LLM API call failed: {type(e).__name__}: {e}') from e
	
	plan_str = response.completion
	if 'deepseek-r1' in self.llm.model or 'deepseek-reasoner' in self.llm.model:
	plan_str = _remove_think_tags(self, plan_str)
	
	parsed: dict[str, Any] | None = None
	try:
	parsed = json.loads(plan_str)
	self.logger.info(f'Planning Analysis:\n{json.dumps(parsed, indent=4)}')
	except json.JSONDecodeError:
	self.logger.info(f'Planning Analysis:\n{plan_str}')
	except Exception as e:
	self.logger.debug(f'Error parsing planning analysis: {e}')
	self.logger.info(f'Plan: {plan_str}')
	
	plan_data = parsed if isinstance(parsed, dict) else {}
	return Plan(raw=plan_str, **plan_data)


def _remove_think_tags(self, text: str) -> str:
    text = re.sub(THINK_TAGS, '', text)
    text = re.sub(STRAY_CLOSE_TAG, '', text)
    return text.strip()


@time_execution_async('--run_planner')
async def _run_planner(self) -> str | None:
    """Run the planner to analyze state and suggest next steps"""
    if not self.settings.planner_llm:
        return None

    assert self.browser_session is not None, 'BrowserSession is not set up'
    page = await self.browser_session.get_current_page()

    standard_actions = self.controller.registry.get_prompt_description()
    page_actions = self.controller.registry.get_prompt_description(page)

    all_actions = standard_actions
    if page_actions:
        all_actions += '\n' + page_actions

    planner_messages = [
        PlannerPrompt(all_actions).get_system_message(
            is_planner_reasoning=self.settings.is_planner_reasoning,
            extended_planner_system_prompt=self.settings.extend_planner_system_message,
        ),
        *self._message_manager.get_messages()[1:],
    ]

    if not self.settings.use_vision_for_planner and self.settings.use_vision:
        last_state_message: UserMessage = planner_messages[-1]
        new_msg = ''
        if isinstance(last_state_message.content, list):
            for msg in last_state_message.content:
                if msg.type == 'text':
                    new_msg += msg.text
                elif msg.type == 'image_url':
                    continue
        else:
            new_msg = last_state_message.content
        planner_messages[-1] = UserMessage(content=new_msg)

    try:
        response = await self.settings.planner_llm.ainvoke(planner_messages)
    except Exception as e:
        self.logger.error(f'Failed to invoke planner: {str(e)}')
        status_code = getattr(e, 'status_code', None) or getattr(e, 'code', None) or 500
        error_msg = f'Planner LLM API call failed: {type(e).__name__}: {str(e)}'
        raise LLMException(status_code, error_msg) from e

    plan = response.completion
    if self.settings.planner_llm and (
        'deepseek-r1' in self.settings.planner_llm.model or 'deepseek-reasoner' in self.settings.planner_llm.model
    ):
        plan = self._remove_think_tags(plan)
    try:
        plan_json = json.loads(plan)
        self.logger.info(f'Planning Analysis:\n{json.dumps(plan_json, indent=4)}')
    except json.JSONDecodeError:
        self.logger.info(f'Planning Analysis:\n{plan}')
    except Exception as e:
        self.logger.debug(f'Error parsing planning analysis: {e}')
        self.logger.info(f'Plan: {plan}')

    return plan
