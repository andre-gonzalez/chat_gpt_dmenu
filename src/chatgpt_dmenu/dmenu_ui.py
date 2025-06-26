import shutil
import subprocess


class DMenuUI:
    """Handles user interaction via dmenu."""

    def __init__(self) -> None:
        dmenu = shutil.which("dmenu")
        if dmenu is None:
            msg = "dmenu not found in PATH"
            raise FileNotFoundError(msg)
        self.dmenu: str = dmenu

    def select_option(self, options: list[str], prompt: str = "Select option:") -> str:
        """
        Displays a dmenu prompt and returns selected value.

        Args:
            options (List[str]): List of options to choose from.
            prompt (str): Prompt shown in dmenu.

        Returns:
            str: Selected option.
        """
        result = subprocess.run(
            [self.dmenu, "-p", prompt],
            input="\n".join(options),
            stdout=subprocess.PIPE,
            text=True,
            check=False,
        )

        return result.stdout.strip()

    def input_box(self, prompt: str = "Enter value:") -> str:
        """
        Displays a dmenu input prompt for free text.

        Args:
            prompt (str): Prompt shown in dmenu.

        Returns:
            str: User input.
        """
        result = subprocess.run(
            [self.dmenu, "-p", prompt],
            input=b"",
            stdout=subprocess.PIPE,
            text=True,
            check=False,
        )
        return result.stdout.decode().strip()
