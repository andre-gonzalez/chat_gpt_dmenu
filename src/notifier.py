import subprocess
import tempfile
import logging
from src.config_loader import ConfigLoader

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
        logging.info("Opening Neovim popup with response...")
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
