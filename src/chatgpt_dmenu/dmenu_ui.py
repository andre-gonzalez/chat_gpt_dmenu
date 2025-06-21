import subprocess
from typing import List

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
