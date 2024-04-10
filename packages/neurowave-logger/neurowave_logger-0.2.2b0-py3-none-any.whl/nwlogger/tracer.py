from typing import Any, Callable, Dict, Generator, List, Mapping, Optional, TypedDict
from functools import wraps
from time import perf_counter
from nwlogger.utils.openai_info import standardize_model_name, get_openai_token_cost_for_model, MODEL_COST_PER_1K_TOKENS

import requests

LOG_SERVER_URL = "https://api-dev.neurowave.ai/logs/chats"

all_meta_data = {
    "conversation" : {
        "messages": []
    }
}

def on_submit(meta_data):
    response = requests.post(LOG_SERVER_URL, json=meta_data)
    if not response.ok:
        print (f"Error logging to server: {response.status_code} - {response.text}")
    else:
        print (f"Successfully logging to server: {response.text}")

def valid_message(messages: List):
    if not isinstance(messages, List):
        raise TypeError("message must be an List")

    # check if index in messages
    if "index" not in messages[-1]:
        for index, message in enumerate(messages):
            message["index"] = len(all_meta_data["conversation"]["messages"]) + index
    return messages

def trace_llm(messages: List, response: List, latency: float, context: str = None) -> Dict:
    '''get infor for each llm call'''
    print ("log the llm call infomation")

    messages = valid_message(messages)
    model_name = standardize_model_name(response.model)

    # ==== we get answers and usage information
    answer = response.choices[0].message.content

    completion_tokens = response.usage.completion_tokens
    prompt_tokens = response.usage.prompt_tokens
    total_tokens = response.usage.total_tokens

    if model_name in MODEL_COST_PER_1K_TOKENS:
        completion_cost = get_openai_token_cost_for_model(
            model_name, completion_tokens, is_completion=True
        )
        prompt_cost = get_openai_token_cost_for_model(model_name, prompt_tokens)
        llm_cost = prompt_cost + completion_cost
    else:
        llm_cost = 0

    item = {
        "index": messages[-1]["index"] + 1,
        "role": "assistant",
        "content": answer,
        "llm_cost": round(llm_cost, 4),
        "llm_latency": latency,
        "llm_token_usage": total_tokens,
        "model_name": model_name
    }

    if context:
        item["context"] = context
    messages.append(item)
    return messages

def trace_chain(session_id: str, meta_data: Dict):
    '''put all infor from each llm call together'''
    print ("log the chain infomation")
    all_meta_data["session_id"] = session_id
    all_meta_data.update(meta_data)
    turn_latency = 0
    turn_cost = 0
    turn_token_usage = 0

    for item in all_meta_data["conversation"]["messages"]:
        if item["role"] != "assistant":
            continue

        if "llm_latency" in item:
            turn_latency += item["llm_latency"]

        if "llm_cost" in item:
            turn_cost += item["llm_cost"]

        if "llm_token_usage" in item:
            turn_token_usage += item["llm_token_usage"]

    all_meta_data["turn_latency"] = turn_latency
    all_meta_data["turn_cost"] = turn_cost
    all_meta_data["turn_token_usage"] = turn_token_usage
    # submit_to_server(all_meta_data)
    return all_meta_data

def traceable(run_type: str,
              context: str = None,
              session_id: Optional[str] = None,
              *,
              meta_data: Optional[Dict] = {},
              messages: Optional[List] = None,
             ):
    '''trace a OpenAI LLM call'''

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(
            *args: Any,
            **kwargs: Any,
        ) -> Any:
            start_time  = perf_counter()
            result = func(*args, **kwargs)
            end_call_time = perf_counter()
            latency = end_call_time - start_time
            if run_type == "llm":
                updated_messages = trace_llm(messages, result, latency, context)
                all_meta_data["conversation"]["messages"] += updated_messages
                return result.choices[0].message.content

            if run_type == "chain":
                data = trace_chain(session_id, meta_data)
            return data
        return wrapper

    return decorator
