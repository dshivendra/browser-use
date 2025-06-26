from __future__ import annotations

import json
import logging
import re

from browser_use.agent.prompts import PlannerPrompt
from browser_use.exceptions import LLMException
from browser_use.llm.messages import UserMessage
from browser_use.utils import time_execution_async

logger = logging.getLogger(__name__)

THINK_TAGS = re.compile(r'<think>.*?</think>', re.DOTALL)
STRAY_CLOSE_TAG = re.compile(r'.*?</think>', re.DOTALL)


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
