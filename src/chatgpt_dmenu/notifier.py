import logging
import shutil
import subprocess
import tempfile

from chatgpt_dmenu.config_loader import ConfigLoader

logger = logging.getLogger(__name__)


class Notifier:
    """
    Manages user notifications and output display using a terminal + Neovim.

    Args:
        config (ConfigLoader): Configuration loader to get terminal command.
    """

    def __init__(self, config: ConfigLoader) -> None:
        self.terminal: str = str(config.get("terminal", "alacritty"))

    def popup(self, text: str) -> None:
        """
        Opens a temporary file in Neovim inside a terminal window.

        Args:
            text (str): Text to display.
        """
        logger.info("Opening Neovim popup with response...")
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=".txt", mode="w", encoding="utf-8"
        ) as tmp:
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
        notify_send = shutil.which("notify-send") or "notify-send"
        subprocess.run([notify_send, summary, body], check=False)
