from datetime import datetime
from dalpha.logging.events import Event
from dalpha.logging.log_formatter import logger

class DalphaOpenAI:
    def __init__(self, api_key):
        from openai import OpenAI
        self.api_key = api_key
        self.client = OpenAI(api_key=self.api_key)

    def chat_completions_create_stream(self, **kwargs):
        stream = None
        if 'stream' in kwargs:
            stream = kwargs['stream']
        if not stream:
            kwargs['stream'] = True
        logger.info(
            message = "chat_completions_create_stream",
            event = Event.GPT,
            properties = {
                "model": kwargs['model']
            },
            data = {
                "messages" : kwargs['messages']
            }
        )
        yield from self.client.chat.completions.create(**kwargs)

    def chat_completions_create(self, **kwargs):
        stream = None
        account_id = None
        
        if 'stream' in kwargs:
            stream = kwargs['stream']
        if stream:
            raise ValueError('stream is not allowed, use chat_completions_create_stream')
        start = datetime.now()
        ret = self.client.chat.completions.create(**kwargs)
        end = datetime.now()

        logger.info(
            message = "chat_completions_create",
            event = Event.GPT,
            properties = {
                "latency": (end - start).total_seconds(),
                "completion_tokens": ret.usage.completion_tokens,
                "model": ret.model,
                "prompt_tokens": ret.usage.prompt_tokens,
                "total_tokens": ret.usage.total_tokens
            },
            data = {}
        )
        return ret