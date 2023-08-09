from threading import Lock
import openai, openai.api_requestor
from claude_api import Client
from datetime import datetime

from lib.bot import Bot


class LLM:

    def __init__(self):
        self.mutex = Lock()

    def get_response(self, role_desc: str, prompt: str) -> (str, float):
        """Returns (response, costs) from the LLM API"""
        shortened_role_desc = role_desc[:50]
        shortened_prompt = prompt[:50]
        print(f"Generating response for prompt: <{shortened_prompt}> with role description: <{shortened_role_desc}>")
        pass


class ChatGPT(LLM):

    def __init__(self, openai_org_id, openai_api_key):
        super().__init__()
        openai.organization = openai_org_id
        openai.api_key = openai_api_key

    def _get_response(self, role_desc: str, prompt: str, max_tokens: int) -> (str, float):
        """Generates a response from the given message"""
        super().get_response(role_desc, prompt)
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": role_desc
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            n=1,
            max_tokens=max_tokens
        )

        costs = response.usage.prompt_tokens * 0.03 + response.usage.completion_tokens * 0.06
        costs = costs / 1000
        return response.choices[0].message.content, costs

    def get_response(self, role_desc: str, prompt: str, max_tokens: int = 256) -> (str, float):
        """Returns a response from the ChadGPT API"""
        with self.mutex:
            response, costs = self._get_response(role_desc, prompt, max_tokens)
        return response, costs


class Claude(LLM):

    def __init__(self, claude_session_cookie):
        super().__init__()
        self.client_api = Client(claude_session_cookie)

    def _craft_prompt(self, role_desc: str, prompt: str) -> str:
        """Crafts a prompt from the given message"""
        return f'Your role description: "{role_desc}"\n\n' \
               f'User input / your task: "{prompt}"\n\n' \
               f'Now, with respect to your role description and the respective user input, react accordingly.'

    def _get_latest_reply(self, uuid: str) -> str:
        history = self.client_api.chat_conversation_history(uuid)
        sorted_entries = sorted(history["chat_messages"],
                                key=lambda entry: datetime.strptime(entry["created_at"], "%Y-%m-%dT%H:%M:%S.%f%z"))
        return sorted_entries[-1]["text"] if sorted_entries[-1]["sender"] == "assistant" else ""

    def _get_response(self, role_desc: str, prompt: str, file_paths: []) -> (str, float):
        """Generates a response from the given message"""
        super().get_response(role_desc, prompt)
        new_chat = self.client_api.create_new_chat()
        new_chat_id = new_chat["uuid"]
        file = file_paths[0] if file_paths else None
        self.client_api.send_message(self._craft_prompt(role_desc, prompt), new_chat_id, file)
        response = self._get_latest_reply(new_chat_id)
        # Claude is not charging for the chat
        costs = 0
        return response, costs

    def get_response(self, role_desc: str, prompt: str, file_paths=None) -> (str, float):
        """Returns a response from the Claude API"""
        if file_paths is None:
            file_paths = []
        with self.mutex:
            response, costs = self._get_response(role_desc, prompt, file_paths)
        return response, costs


# static instances
_chat_gpt = None
_claude = None


def chat_gpt(bot: Bot):
    global _chat_gpt
    if not _chat_gpt:
        _chat_gpt = ChatGPT(bot.config.openai_org_id, bot.config.openai_api_key)
    return _chat_gpt


def claude(bot: Bot):
    global _claude
    if not _claude:
        _claude = Claude(bot.config.claude_session_cookie)
    return _claude
