import openai
from openai.api_resources import (
    Completion,
    ChatCompletion
)

class BlumeOpenAIInjector:
    client_instance = None

    @staticmethod
    def completion_proxy_handler(self, *args, **kwargs):
        print("Intercepted input: ", args, kwargs)
        return Completion.create(*args, **kwargs)
    
    @staticmethod
    def chat_completion_proxy_handler(self, *args, **kwargs):
        print("Intercepted input: ", args, kwargs)
        return ChatCompletion.create(*args, **kwargs)

    @staticmethod
    def inject(self, client_instance = None):
        if (client_instance):
            BlumeOpenAIInjector.client_instance = client_instance
            BlumeOpenAIInjector.client_instance.Completion.create = self.completion_proxy_handler
            BlumeOpenAIInjector.client_instance.ChatCompletion.create = self.chat_completion_proxy_handler
        return BlumeOpenAIInjector.client_instance or openai
