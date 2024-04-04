from typing import Optional, List

from .mock_ai import MockAI

####### ENVIRONMENT VARIABLES ###################
mock_ai = MockAI()

def mock_completion(messages: List, model: Optional[str] = None, **kwargs):
    last_message = messages[-1]
    if isinstance(last_message, dict):
        if "content" in last_message:
            content = last_message.get("content")
            if isinstance(content, list) and all(isinstance(item, dict) and "text" in item for item in content):
                message = [item["text"] for item in content][0] #get the first of the texts
            else:
                message = str(last_message.get("content"))
        elif "text" in last_message:
            texts = last_message.get("text")
            if isinstance(texts, list) and all(isinstance(item, dict) and "content" in item for item in texts):
                message = [item["content"] for item in texts][0] #get the first of the texts
            else:
                message = str(last_message.get("text"))
        else:
            raise KeyError
    else:
        message = str(last_message)

    return mock_ai.get_completion(message)


def set_config(json_file_path: str):
    mock_ai.set_config(json_file_path)
