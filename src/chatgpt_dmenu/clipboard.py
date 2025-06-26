import logging
import shutil
import subprocess

logger = logging.getLogger(__name__)


class Clipboard:
    """Handles clipboard interaction using xclip."""

    def __init__(self) -> None:
        xclip = shutil.which("xclip")
        if xclip is None:
            msg = "xclip not found in PATH"
            raise FileNotFoundError(msg)
        self.xclip: str = xclip

    def get(self) -> str:
        """Gets the current clipboard contents."""
        logger.debug("Reading from clipboard...")
        result = subprocess.run(
            [self.xclip, "-selection", "clipboard", "-o"],
            stdout=subprocess.PIPE,
            check=False,
        )
        return result.stdout.decode()

    def set(self, text: str) -> None:
        """
        Sets the clipboard contents.

        Args:
            text (str): Text to copy to clipboard.
        """
        logger.debug("Writing to clipboard...")
        subprocess.run(
            [self.xclip, "-selection", "clipboard"], input=text.encode(), check=False
        )
