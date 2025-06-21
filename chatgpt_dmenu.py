import subprocess
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
import os
import sys
import yaml
import tempfile
from typing import Optional, List, Dict


class ConfigLoader:
    """
    Loads and provides access to configuration data from a YAML file.

    Args:
        path (Optional[str]): Optional path to the configuration file. If None, defaults to ~/.config/chatgpt-dmenu/config.yaml.
    """
    def __init__(self, path: Optional[str] = None) -> None:
        self.config_path: str = path or os.path.expanduser("~/.config/chatgpt-dmenu/config.yaml")
        self.config: dict = self._load_config()

    def _load_config(self) -> dict:
        """Loads the YAML config file into a dictionary."""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        with open(self.config_path, "r") as f:
            return yaml.safe_load(f)

    def get(self, key: str, default: Optional[object] = None) -> object:
        """
        Retrieves a value from the config.

        Args:
            key (str): The config key.
            default (Optional[object]): Default value if key not found.

        Returns:
            object: Value from config or default.
        """
        return self.config.get(key, default)

    def get_contexts(self) -> Dict[str, str]:
        """Returns the dictionary of named system prompts (contexts)."""
        return self.config.get("contexts", {})

    def get_list(self, key: str, default: Optional[List[str]] = None) -> List[str]:
        """
        Retrieves a list from the config.

        Args:
            key (str): Key to look for.
            default (Optional[List[str]]): Default list if not found.

        Returns:
            List[str]: List of values.
        """
        return self.config.get(key, default or [])


class ContextManager:
    """
    Manages ChatGPT prompt contexts and dynamically formats them.

    Args:
        config (ConfigLoader): Instance of ConfigLoader containing the context config.
    """
    def __init__(self, config: ConfigLoader) -> None:
        self.contexts: Dict[str, str] = config.get_contexts()

    def get_contexts(self) -> List[str]:
        """Returns the list of context names."""
        return list(self.contexts.keys())

    def get_prompt(self, name: str, audience: Optional[str] = None,
                   tone: Optional[str] = None, person: Optional[str] = None) -> str:
        """
        Returns a context prompt with placeholders filled.

        Args:
            name (str): Context name.
            audience (Optional[str]): Target audience for the prompt.
            tone (Optional[str]): Tone to be used in the output.
            person (Optional[str]): Person the message is addressed to.

        Returns:
            str: Final formatted prompt.
        """
        prompt = self.contexts.get(name, "")
        return (
            prompt.replace("{audience}", audience or "the recipient")
                  .replace("{tone}", tone or "friendly but professional")
                  .replace("{person}", person or "there")
        )


class Clipboard:
    """Handles clipboard interaction using xclip."""

    @staticmethod
    def get() -> str:
        """Gets the current clipboard contents."""
        result = subprocess.run(["xclip", "-selection", "clipboard", "-o"], stdout=subprocess.PIPE)
        return result.stdout.decode()

    @staticmethod
    def set(text: str) -> None:
        """
        Sets the clipboard contents.

        Args:
            text (str): Text to copy to clipboard.
        """
        subprocess.run(["xclip", "-selection", "clipboard"], input=text.encode())


class DMenuUI:
    """Handles user interaction via dmenu."""

    @staticmethod
    def select_option(options: List[str], prompt: str = "Select option:") -> str:
        """
        Displays a dmenu prompt and returns selected value.

        Args:
            options (List[str]): List of options to choose from.
            prompt (str): Prompt shown in dmenu.

        Returns:
            str: Selected option.
        """
        result = subprocess.run(["dmenu", "-p", prompt],
                                input="\n".join(options).encode(),
                                stdout=subprocess.PIPE)
        return result.stdout.decode().strip()

    @staticmethod
    def input_box(prompt: str = "Enter value:") -> str:
        """
        Displays a dmenu input prompt for free text.

        Args:
            prompt (str): Prompt shown in dmenu.

        Returns:
            str: User input.
        """
        result = subprocess.run(["dmenu", "-p", prompt], input=b"", stdout=subprocess.PIPE)
        return result.stdout.decode().strip()


class Notifier:
    """
    Manages user notifications and output display using a terminal + Neovim.

    Args:
        config (ConfigLoader): Configuration loader to get terminal command.
    """
    def __init__(self, config: ConfigLoader) -> None:
        self.terminal: str = config.get("terminal", "alacritty")

    def popup(self, text: str, title: str = "ChatGPT Result") -> None:
        """
        Opens a temporary file in Neovim inside a terminal window.

        Args:
            text (str): Text to display.
            title (str): Title for popup window (ignored in this version).
        """
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8") as tmp:
            tmp.write(text)
            tmp_path = tmp.name

        subprocess.Popen([self.terminal, "-e", "nvim", tmp_path])

    @staticmethod
    def notify(summary: str, body: str) -> None:
        """
        Sends a desktop notification.

        Args:
            summary (str): Notification title.
            body (str): Notification body text.
        """
        subprocess.run(["notify-send", summary, body])


class ChatGPTClient:
    """
    Handles interaction with OpenAI's Chat API using the new SDK.

    Args:
        config (ConfigLoader): Provides API key, model, and temperature.
    """
    def __init__(self, config: ConfigLoader) -> None:
        self.client = OpenAI(api_key=config.get("api_key"))
        self.model: str = config.get("model", "gpt-4o")
        self.temperature: float = config.get("temperature", 0.7)

    def chat(self, system_prompt: str, user_input: str) -> str:
        """
        Sends a message to ChatGPT and returns the response.

        Args:
            system_prompt (str): The system-level instruction for the assistant.
            user_input (str): The user message to process.

        Returns:
            str: ChatGPT's response.
        """
        try:
            messages: List[ChatCompletionMessageParam] = [
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
    """
    Main application orchestrating user input, GPT prompt building, and displaying results.
    """
    def __init__(self) -> None:
        self.config = ConfigLoader()
        self.context_manager = ContextManager(self.config)
        self.chatgpt = ChatGPTClient(self.config)
        self.ui = DMenuUI()
        self.clipboard = Clipboard()
        self.notifier = Notifier(self.config)

    def run(self) -> None:
        """Main run loop: handles prompt selection, formatting, querying GPT, and displaying result."""
        choice = self.ui.select_option(self.context_manager.get_contexts())
        if not choice:
            sys.exit(0)

        if choice == "Business Email":
            audience = self.get_dmenu_or_custom("audiences", "Target Audience:")
            tone = self.get_dmenu_or_custom("tones", "Tone:")
            person = self.get_dmenu_or_custom("persons", "Person to address:")
            prompt = self.context_manager.get_prompt(choice, audience, tone, person)
        else:
            prompt = self.context_manager.get_prompt(choice)

        user_input = self.clipboard.get()

        try:
            output = self.chatgpt.chat(prompt, user_input)
            self.clipboard.set(output)
            self.notifier.popup(output, title=f"ChatGPT: {choice}")
            self.notifier.notify("ChatGPT", "Response copied to clipboard")
        except RuntimeError as e:
            self.notifier.notify("ChatGPT Error", str(e))
            print(str(e))

    def get_dmenu_or_custom(self, key: str, prompt: str) -> str:
        """
        Shows a dmenu selector with an option to enter a custom value.

        Args:
            key (str): Config key for predefined options (e.g., "audiences").
            prompt (str): Prompt label to show in dmenu.

        Returns:
            str: Selected or entered custom value.
        """
        options = self.config.get_list(key, [])
        options.append("Other...")
        choice = self.ui.select_option(options, prompt)
        if choice == "Other...":
            choice = self.ui.input_box(f"Enter custom {key[:-1]}:")
        return choice
