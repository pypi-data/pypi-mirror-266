import openai
import requests
from openai.api_resources import (
    Completion,
    ChatCompletion
)
from datetime import date
import json

SERVER_URL = "http://localhost:8000"

class OpenAIModule:
    Completion: Completion
    ChatCompletion: ChatCompletion

class BlumeOpenAIWrapper:
    client_instance = None
    # Variables to store original methods
    original_completion_create = None
    original_chat_completion_create = None
    options = {}

    @staticmethod
    def send_to_backend(endpoint, data, options):
        """Send intercepted data to the backend server."""
        # Assuming `data` now includes the query we're interested in directly
        payload = {"query": data, "options": options}
        try:
            print("PAYLOAD: ", payload)
            response = requests.post(f"{SERVER_URL}/{endpoint}", json=payload)
            print("Backend response: ", response.json())
        except Exception as e:
            print("Error sending data to backend: ", e)

    @classmethod
    def completion_proxy_handler(cls, *args, **kwargs):
        """Proxy handler for Completion.create"""
        current_date = date.today()
        current_date = json.dumps(current_date, indent=4, sort_keys=True, default=str)
        options = kwargs.pop('options', cls.options)
        options['date'] = current_date
        query_text = args[0] if args else kwargs.get('prompt', '')
        print("Intercepted Completion input: ", query_text)
        cls.send_to_backend("llm", query_text, options)
        # Call the original method
        return cls.original_completion_create(*args, **kwargs)
    
    @classmethod
    def chat_completion_proxy_handler(cls, *args, **kwargs):
        """Proxy handler for ChatCompletion.create"""
        current_date = date.today()
        current_date = json.dumps(current_date, indent=4, sort_keys=True, default=str)
        options = kwargs.pop('options', cls.options)
        options['date'] = current_date        
        query_text = args[0] if args else kwargs.get('messages', [])


        if isinstance(query_text, list):
            query_text = ' '.join([msg.get('content', '') for msg in query_text])
        print("Intercepted ChatCompletion input: ", query_text)
        cls.send_to_backend("llm", query_text, options)
        # Call the original method
        return cls.original_chat_completion_create(*args, **kwargs)


    @classmethod
    def wrap(cls, incoming_client_instance: OpenAIModule = None, user_id: str = None, options: dict = None):
        if incoming_client_instance:
            cls.client_instance = incoming_client_instance
            # Save references to the original methods
            cls.original_completion_create = incoming_client_instance.Completion.create
            cls.original_chat_completion_create = incoming_client_instance.ChatCompletion.create
            # Override with proxy handlers
            incoming_client_instance.Completion.create = cls.completion_proxy_handler
            incoming_client_instance.ChatCompletion.create = cls.chat_completion_proxy_handler
        if options:
            cls.options = options
        return cls.client_instance or openai