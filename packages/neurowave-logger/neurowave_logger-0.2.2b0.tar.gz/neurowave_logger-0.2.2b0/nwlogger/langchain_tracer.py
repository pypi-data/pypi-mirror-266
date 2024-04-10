"""Callback Handler that writes to a file."""
import json
from typing import Any, Dict, Optional, TextIO, cast, List, Generator
import uuid, os

from langchain_core.agents import AgentAction, AgentFinish
from langchain.callbacks.base import BaseCallbackHandler
from langchain.callbacks.openai_info import OpenAICallbackHandler
from langchain_core.outputs import LLMResult
from langchain_core.tracers.context import register_configure_hook
from contextvars import ContextVar
from time import perf_counter

from contextlib import contextmanager

import requests
from .utils.openai_info import standardize_model_name, get_openai_token_cost_for_model, MODEL_COST_PER_1K_TOKENS

LOG_SERVER_URL = "https://api-dev.neurowave.ai/logs/chats"

class CoevalLogger(BaseCallbackHandler):
    """Callback Handler that writes to a file."""

    def __init__(
        self, session_id: str, **kwargs: Any
    ) -> None:
        """Initialize callback handler."""

        self.meta_data = kwargs.get("meta_data", {})

        self.session_id = session_id
        self.conversation = {
            "messages": []
        }

        self.turn_cost = 0
        self.turn_latency = 0
        self.turn_token_usage = 0
        self.model_name = None

    def __repr__(self) -> str:
        return self.meta_data

    def _get_model_name_from_llm(self, serialized: Dict[str, Any]) -> str:
        """
        get model name from llm
        """
        llm_infor_exists = serialized.get("kwargs", {}).get("llm", None)
        if llm_infor_exists:
            model_name = llm_infor_exists.get("kwargs").get("model", "gpt-3.5-turbo")
            if not self.model_name:
                self.model_name = model_name
        else:
            self.model_name = "gpt-3.5-turbo"

    def on_chain_start(
        self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any
    ) -> None:
        """Print out that we are entering a chain."""

        class_name = serialized.get("name", serialized.get("id", ["<unknown>"])[-1])
        print(
            f"\n\n\033[1m> Entering new {class_name} chain...\033[0m",
            end="\n",
        )
        self._get_model_name_from_llm(serialized)

    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> None:
        """Print out that we finished a chain."""
        print("\n\033[1m> Finished chain.\033[0m", end="\n")

    def on_agent_action(
        self, action: AgentAction, color: Optional[str] = None, **kwargs: Any
    ) -> Any:
        """Run on agent action."""
        print(action.log)

    def on_tool_end(
        self,
        output: str,
        color: Optional[str] = None,
        observation_prefix: Optional[str] = None,
        llm_prefix: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """If not the final action, print out observation."""

        if observation_prefix is not None:
            print(f"\n{observation_prefix}")
        print(output)
        if llm_prefix is not None:
            print(f"\n{llm_prefix}")

    def on_text(
        self, text: str, color: Optional[str] = None, end: str = "", **kwargs: Any
    ) -> None:
        """Run when agent ends."""
        pass

    def on_agent_finish(
        self, finish: AgentFinish, color: Optional[str] = None, **kwargs: Any
    ) -> None:
        """Run on agent end."""
        print(finish.log, end="\n")

    def on_llm_start(
            self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
        ) -> None:
            """Print out the prompts."""

            # LLM start
            self.llm_start_time  = perf_counter()

            if len(self.conversation["messages"]) > 0 and self.conversation["messages"][-1].get("role") == "user":
                self.conversation["messages"][-1]["prompts"] = prompts[0]
            else:
                pass

    def log_question(self, question: str) -> None:
        item = {
            "content": question,
            "role": "user",
            "index": len(self.conversation["messages"]),
        }
        self.conversation["messages"].append(item)

    def log_context(self, context: str) -> None:

        if len(self.conversation["messages"]) > 0 and self.conversation["messages"][-1].get("role") == "assistant":
            self.conversation["messages"][-1]["context"] = context
        else:
            pass

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Collect token usage."""

        if response.llm_output is None:
            return None
        if "token_usage" not in response.llm_output:
            return None

        token_usage = response.llm_output["token_usage"]
        completion_tokens = token_usage.get("completion_tokens", 0)
        prompt_tokens = token_usage.get("prompt_tokens", 0)
        llm_token_llm_token_usage = token_usage.get("total_tokens", 0)

        model_name = standardize_model_name(response.llm_output.get("model_name", ""))
        if model_name in MODEL_COST_PER_1K_TOKENS:
            completion_cost = get_openai_token_cost_for_model(
                model_name, completion_tokens, is_completion=True
            )
            prompt_cost = get_openai_token_cost_for_model(model_name, prompt_tokens)
            llm_cost = prompt_cost + completion_cost

        self.llm_end_time  = perf_counter()
        llm_latency = self.llm_end_time - self.llm_start_time

        item = {
            "role": "assistant",
            "content": response.generations[0][0].message.content,
            "index": len(self.conversation["messages"]),
            "llm_cost": llm_cost,
            "llm_token_usage": llm_token_llm_token_usage,
            "llm_latency": llm_latency
        }

        self.conversation["messages"].append(item)
        self.turn_cost += llm_cost
        self.turn_latency += llm_latency
        self.turn_token_usage = token_usage

    def format_final_response_to_submit(self):
        meta_data = {
            "session_id": self.session_id,
            "model_name": self.model_name,
            "conversation": self.conversation,
            "turn_token_usage": self.turn_token_usage,
            "turn_cost": self.turn_cost,
            "turn_latency": self.turn_latency,
        }
        self.meta_data.update(meta_data)

    def on_submit(self) -> None:
        """
        """
        self.format_final_response_to_submit()
        print(f"logging to server ...")
        response = requests.post(LOG_SERVER_URL, json=self.meta_data)
        if not response.ok:
            print(f"Error logging to server: {response.status_code} - {response.text}")
        else:
            print(f"logged to server ...")
        return self.meta_data

coeval_callback_var: ContextVar[Optional[CoevalLogger]] = ContextVar(
    "coeval_callback", default=None
)
register_configure_hook(coeval_callback_var, True)

@contextmanager
def get_coeval_logger(session_id, **kwargs: Any) -> Generator[CoevalLogger, None, None]:
    # session_id = kwargs.get("session_id")
    cb = CoevalLogger(session_id=session_id, **kwargs)
    coeval_callback_var.set(cb)
    yield cb
    coeval_callback_var.set(None)
