def get_default():
    return {
          "id": "chatcmpl-xxxxxxxxxxxxxxxxxxxxxxxxxxxx",
          "object": "chat.completion",
          "created": 1700051346,
          "model": "gpt-35-turbo",
          "choices": [
            {
              "index": 0,
              "finish_reason": "stop",
              "message": {
                "role": "assistant",
                "content": "MockAI is awesome"
              }
            }
          ],
          "usage": {
            "prompt_tokens": 19,
            "completion_tokens": 10,
            "total_tokens": 29
          }
    }