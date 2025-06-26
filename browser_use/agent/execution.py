# @file purpose: Execution helpers for interacting with the browser.
"""Asynchronous routines for running actions and replaying history.

These utilities support the :class:`Agent` by executing multiple actions
per step, replaying stored interaction history and updating action
indices when the DOM structure changes.
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Any

from browser_use.controller.registry.views import ActionModel
from browser_use.agent.views import (
    ActionResult,
    AgentHistory,
    AgentHistoryList,
    BrowserStateSummary,
)
from browser_use.dom.history_tree_processor.service import (
    DOMHistoryElement,
    HistoryTreeProcessor,
)
from browser_use.utils import time_execution_async

logger = logging.getLogger(__name__)


@time_execution_async('--multi_act')
async def multi_act(self, actions: list[ActionModel], check_for_new_elements: bool = True) -> list[ActionResult]:
    """Execute multiple actions"""
    results = []

    assert self.browser_session is not None, 'BrowserSession is not set up'
    cached_selector_map = await self.browser_session.get_selector_map()
    cached_path_hashes = {e.hash.branch_path_hash for e in cached_selector_map.values()}

    await self.browser_session.remove_highlights()

    for i, action in enumerate(actions):
        if i > 0 and action.model_dump(exclude_unset=True).get('done') is not None:
            msg = f'Done action is allowed only as a single action - stopped after action {i} / {len(actions)}.'
            logger.info(msg)
            break

        if action.get_index() is not None and i != 0:
            new_browser_state_summary = await self.browser_session.get_state_summary(cache_clickable_elements_hashes=False)
            new_selector_map = new_browser_state_summary.selector_map

            orig_target = cached_selector_map.get(action.get_index())  # type: ignore
            orig_target_hash = orig_target.hash.branch_path_hash if orig_target else None
            new_target = new_selector_map.get(action.get_index())  # type: ignore
            new_target_hash = new_target.hash.branch_path_hash if new_target else None
            if orig_target_hash != new_target_hash:
                msg = f'Element index changed after action {i} / {len(actions)}, because page changed.'
                logger.info(msg)
                results.append(
                    ActionResult(
                        extracted_content=msg,
                        include_in_memory=True,
                        long_term_memory=msg,
                    )
                )
                break

            new_path_hashes = {e.hash.branch_path_hash for e in new_selector_map.values()}
            if check_for_new_elements and not new_path_hashes.issubset(cached_path_hashes):
                msg = f'Something new appeared after action {i} / {len(actions)}, following actions are NOT executed and should be retried.'
                logger.info(msg)
                results.append(
                    ActionResult(
                        extracted_content=msg,
                        include_in_memory=True,
                        long_term_memory=msg,
                    )
                )
                break

        try:
            await self._raise_if_stopped_or_paused()

            result = await self.controller.act(
                action=action,
                browser_session=self.browser_session,
                file_system=self.file_system,
                page_extraction_llm=self.settings.page_extraction_llm,
                sensitive_data=self.sensitive_data,
                available_file_paths=self.settings.available_file_paths,
                context=self.context,
            )

            results.append(result)

            action_data = action.model_dump(exclude_unset=True)
            action_name = next(iter(action_data.keys())) if action_data else 'unknown'
            action_params = getattr(action, action_name, '')
            self.logger.info(f'☑️ Executed action {i + 1}/{len(actions)}: {action_name}({action_params})')
            if results[-1].is_done or results[-1].error or i == len(actions) - 1:
                break

            await asyncio.sleep(self.browser_profile.wait_between_actions)

        except asyncio.CancelledError:
            self.logger.info(f'Action {i + 1} was cancelled due to Ctrl+C')
            if not results:
                results.append(
                    ActionResult(
                        error='The action was cancelled due to Ctrl+C',
                        include_in_memory=True,
                    )
                )
            raise InterruptedError('Action cancelled by user')

    return results


async def rerun_history(
    self,
    history: AgentHistoryList,
    max_retries: int = 3,
    skip_failures: bool = True,
    delay_between_actions: float = 2.0,
) -> list[ActionResult]:
    if self.initial_actions:
        result = await self.multi_act(self.initial_actions)
        self.state.last_result = result

    results = []

    for i, history_item in enumerate(history.history):
        goal = history_item.model_output.current_state.next_goal if history_item.model_output else ''
        self.logger.info(f'Replaying step {i + 1}/{len(history.history)}: goal: {goal}')

        if (
            not history_item.model_output
            or not history_item.model_output.action
            or history_item.model_output.action == [None]
        ):
            self.logger.warning(f'Step {i + 1}: No action to replay, skipping')
            results.append(ActionResult(error='No action to replay'))
            continue

        retry_count = 0
        while retry_count < max_retries:
            try:
                result = await self._execute_history_step(history_item, delay_between_actions)
                results.extend(result)
                break

            except Exception as e:
                retry_count += 1
                if retry_count == max_retries:
                    error_msg = f'Step {i + 1} failed after {max_retries} attempts: {str(e)}'
                    self.logger.error(error_msg)
                    if not skip_failures:
                        results.append(ActionResult(error=error_msg))
                        raise RuntimeError(error_msg)
                else:
                    self.logger.warning(
                        f'Step {i + 1} failed (attempt {retry_count}/{max_retries}), retrying...'
                    )
                    await asyncio.sleep(delay_between_actions)

    return results


async def _execute_history_step(self, history_item: AgentHistory, delay: float) -> list[ActionResult]:
    assert self.browser_session is not None, 'BrowserSession is not set up'
    state = await self.browser_session.get_state_summary(cache_clickable_elements_hashes=False)
    if not state or not history_item.model_output:
        raise ValueError('Invalid state or model output')
    updated_actions = []
    for i, action in enumerate(history_item.model_output.action):
        updated_action = await self._update_action_indices(
            history_item.state.interacted_element[i],
            action,
            state,
        )
        updated_actions.append(updated_action)

        if updated_action is None:
            raise ValueError(f'Could not find matching element {i} in current page')

    result = await self.multi_act(updated_actions)

    await asyncio.sleep(delay)
    return result


async def _update_action_indices(
    self,
    historical_element: DOMHistoryElement | None,
    action: ActionModel,
    browser_state_summary: BrowserStateSummary,
) -> ActionModel | None:
    if not historical_element or not browser_state_summary.element_tree:
        return action

    current_element = HistoryTreeProcessor.find_history_element_in_tree(
        historical_element, browser_state_summary.element_tree
    )

    if not current_element or current_element.highlight_index is None:
        return None

    old_index = action.get_index()
    if old_index != current_element.highlight_index:
        action.set_index(current_element.highlight_index)
        self.logger.info(
            f'Element moved in DOM, updated index from {old_index} to {current_element.highlight_index}'
        )

    return action


async def load_and_rerun(self, history_file: str | Path | None = None, **kwargs) -> list[ActionResult]:
    if not history_file:
        history_file = 'AgentHistory.json'
    history = AgentHistoryList.load_from_file(history_file, self.AgentOutput)
    return await self.rerun_history(history, **kwargs)


async def _update_action_models_for_page(self, page) -> None:
    self.ActionModel = self.controller.registry.create_action_model(page=page)
    if self.settings.use_thinking:
        from browser_use.agent.views import AgentOutput
        self.AgentOutput = AgentOutput.type_with_custom_actions(self.ActionModel)
    else:
        from browser_use.agent.views import AgentOutput
        self.AgentOutput = AgentOutput.type_with_custom_actions_no_thinking(self.ActionModel)

    self.DoneActionModel = self.controller.registry.create_action_model(include_actions=['done'], page=page)
    if self.settings.use_thinking:
        from browser_use.agent.views import AgentOutput
        self.DoneAgentOutput = AgentOutput.type_with_custom_actions(self.DoneActionModel)
    else:
        from browser_use.agent.views import AgentOutput
        self.DoneAgentOutput = AgentOutput.type_with_custom_actions_no_thinking(self.DoneActionModel)
