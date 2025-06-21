import sys
import logging
from chatgpt_dmenu.config_loader import ConfigLoader, setup_logging
from chatgpt_dmenu.context_manager import ContextManager
from chatgpt_dmenu.chatgpt_client import ChatGPTClient
from chatgpt_dmenu.dmenu_ui import DMenuUI
from chatgpt_dmenu.clipboard import Clipboard
from chatgpt_dmenu.notifier import Notifier

class ChatGPTDMenuApp:
    """
    Main application orchestrating user input, GPT prompt building, and displaying results.
    """
    def __init__(self) -> None:
        self.config = ConfigLoader()

        log_level = self.config.get("log_level", "INFO")
        log_file = self.config.get("log_file", "/tmp/chatgpt-dmenu.log")
        setup_logging(level=log_level, logfile=log_file)

        self.context_manager = ContextManager(self.config)
        self.chatgpt = ChatGPTClient(self.config)
        self.ui = DMenuUI()
        self.clipboard = Clipboard()
        self.notifier = Notifier(self.config)

    def run(self) -> None:
        """Main run loop: handles prompt selection, formatting, querying GPT, and displaying result."""
        logging.info("Running ChatGPTDMenuApp...")

        choice = self.ui.select_option(self.context_manager.get_contexts())
        logging.debug(f"User selected context: {choice}")
        if not choice:
            logging.warning("No context selected. Exiting.")
            sys.exit(0)

        if choice == "Business Email":
            audience = self.get_dmenu_or_custom("audiences", "Target Audience:")
            tone = self.get_dmenu_or_custom("tones", "Tone:")
            person = self.get_dmenu_or_custom("persons", "Person to address:")
            logging.debug(f"User inputs - Audience: {audience}, Tone: {tone}, Person: {person}")
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
