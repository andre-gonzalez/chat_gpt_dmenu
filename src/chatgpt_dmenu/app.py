import logging
import sys
import tempfile

from chatgpt_dmenu.chatgpt_client import ChatGPTClient
from chatgpt_dmenu.clipboard import Clipboard
from chatgpt_dmenu.config_loader import ConfigLoader, setup_logging
from chatgpt_dmenu.context_manager import ContextManager
from chatgpt_dmenu.dmenu_ui import DMenuUI
from chatgpt_dmenu.notifier import Notifier

logger = logging.getLogger(__name__)


class ChatGPTDMenuApp:
    """
    Main application orchestrating:
        - user input,
        - GPT prompt building,
        - and displaying results.
    """

    def __init__(self) -> None:
        self.config = ConfigLoader()

        log_level = str(self.config.get("log_level", "INFO"))
        log_file = str(
            self.config.get("log_file", tempfile.gettempdir() + "/chatgpt-dmenu.log")
        )
        setup_logging(level=log_level, logfile=log_file)

        self.context_manager = ContextManager(self.config)
        self.chatgpt = ChatGPTClient(self.config)
        self.ui = DMenuUI()
        self.clipboard = Clipboard()
        self.notifier = Notifier(self.config)

    def run(self) -> None:
        """
        Main run loop:
            - handles prompt selection,
            - formatting,
            - querying GPT,
            - and displaying result.
        """
        logger.info("Running ChatGPTDMenuApp...")

        choice = self.ui.select_option(self.context_manager.get_contexts())
        logger.debug("User selected context: %s", choice)
        if not choice:
            logger.warning("No context selected. Exiting.")
            sys.exit(0)

        if choice in ["Business Email", "Slack Message"]:
            audience = self.get_dmenu_or_custom("audiences", "Target Audience:")
            tone = self.get_dmenu_or_custom("tones", "Tone:")
            person = self.get_dmenu_or_custom("persons", "Person to address:")
            logger.debug(
                "User inputs - Audience: %s, Tone: %s, Person: %s",
                audience,
                tone,
                person,
            )
            prompt = self.context_manager.get_prompt(choice, audience, tone, person)
        else:
            prompt = self.context_manager.get_prompt(choice)

        user_input = self.clipboard.get()

        try:
            output = self.chatgpt.chat(prompt, user_input)
            main_text = output.split("---")[0].strip()
            self.clipboard.set(main_text)
            self.notifier.popup(output)
            self.notifier.notify("ChatGPT", "Response copied to clipboard")
        except RuntimeError as e:
            self.notifier.notify("ChatGPT Error", str(e))
            error_msg = str(e)
            logger.exception("API call failed: %s", error_msg)

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
