import json

import pytest

from mockai.main import mock_completion, set_config

set_config('config.json')

with open('mock_responses/default.json', 'r') as json_file:
    DEFAULT_RESPONSE = json.load(json_file)



def test_mock_completion():
    # Test with last message as a string
    messages = ["/default"]
    completion = mock_completion(messages)
    assert completion == DEFAULT_RESPONSE

    # Test with last message as a dictionary with 'text' key
    messages = [{"text": "/default"}]
    completion = mock_completion(messages)
    assert completion == DEFAULT_RESPONSE

    # Test with last message as a dictionary with 'content' key
    messages = [{"content": "/default"}]
    completion = mock_completion(messages)
    assert completion == DEFAULT_RESPONSE

    # Test with last message as a dictionary without 'text' or 'content' key
    messages = [{"role": "john", "field": "/default"}]
    with pytest.raises(KeyError):
        mock_completion(messages)

    # Test with empty message list
    messages = []
    with pytest.raises(IndexError):
        mock_completion(messages)
