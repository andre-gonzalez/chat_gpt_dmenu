import logging
import subprocess


class Clipboard:
    """Handles clipboard interaction using xclip."""

    @staticmethod
    def get() -> str:
        """Gets the current clipboard contents."""
        logging.debug("Reading from clipboard...")
        result = subprocess.run(
            ["xclip", "-selection", "clipboard", "-o"],
            stdout=subprocess.PIPE,
            check=False,
        )
        return result.stdout.decode()

    @staticmethod
    def set(text: str) -> None:
        """
        Sets the clipboard contents.

        Args:
            text (str): Text to copy to clipboard.
        """
        logging.debug("Writing to clipboard...")
        subprocess.run(
            ["xclip", "-selection", "clipboard"], input=text.encode(), check=False
        )
