import subprocess
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
import os
import sys
import yaml

class ConfigLoader:
    def __init__(self, path=None):
        self.config_path = path or os.path.expanduser("~/.config/chatgpt-dmenu/config.yaml")
        self.config = self._load_config()

    def _load_config(self):
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        with open(self.config_path, "r") as f:
            return yaml.safe_load(f)

    def get(self, key, default=None):
        return self.config.get(key, default)


class ContextManager:
    def __init__(self):
        self.contexts = {
            "Business Email": "You are an expert business communication assistant. Revise the following email in perfect business English.",
            "Slack Message": "You are a casual but clear communication expert. Rewrite the following message to fit Slack.",
            "Code Assistant": "You are a helpful programming assistant. Improve or explain the code given."
        }

    def get_contexts(self):
        return list(self.contexts.keys())

    def get_prompt(self, name):
        return self.contexts.get(name)


class Clipboard:
    @staticmethod
    def get():
        result = subprocess.run(["xclip", "-selection", "clipboard", "-o"], stdout=subprocess.PIPE)
        return result.stdout.decode()

    @staticmethod
    def set(text):
        subprocess.run(["xclip", "-selection", "clipboard"], input=text.encode())


class DMenuUI:
    @staticmethod
    def select_option(options, prompt="Select context:"):
        result = subprocess.run(
            ["dmenu", "-p", prompt],
            input="\n".join(options).encode(),
            stdout=subprocess.PIPE
        )
        return result.stdout.decode().strip()


class Notifier:
    @staticmethod
    def popup(text, title="ChatGPT Result"):
        subprocess.run([
            "zenity", "--text-info", "--title", title,
            "--width=600", "--height=400"
        ], input=text.encode())

    @staticmethod
    def notify(summary, body):
        subprocess.run(["notify-send", summary, body])


class ChatGPTClient:
    def __init__(self, config: ConfigLoader):
        self.client = OpenAI(api_key=config.get("api_key"))
        self.model = config.get("model", "gpt-4o")
        self.temperature = config.get("temperature", 0.7)

    def chat(self, system_prompt, user_input):
        try:
            messages: list[ChatCompletionMessageParam] = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ]

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature
            )
            return response.choices[0].message.content.strip()

        except Exception as e:
            raise RuntimeError(f"API error: {e}")


class ChatGPTDMenuApp:
    def __init__(self):
        self.config = ConfigLoader()
        self.context_manager = ContextManager()
        self.chatgpt = ChatGPTClient(self.config)
        self.ui = DMenuUI()
        self.clipboard = Clipboard()
        self.notifier = Notifier()

    def run(self):
        choice = self.ui.select_option(self.context_manager.get_contexts())
        if not choice:
            sys.exit(0)

        system_prompt = self.context_manager.get_prompt(choice)
        user_input = self.clipboard.get()

        try:
            output = self.chatgpt.chat(system_prompt, user_input)
            self.clipboard.set(output)
            # self.notifier.popup(output, title=f"ChatGPT: {choice}")
            self.notifier.notify("ChatGPT", "Response copied to clipboard")
        except RuntimeError as e:
            self.notifier.notify("ChatGPT Error", str(e))
            print(str(e))
