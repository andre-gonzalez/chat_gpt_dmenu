import logging
import os
from typing import Literal

import yaml

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


def setup_logging(level: str = "INFO", logfile: str = "/tmp/chatgpt-dmenu.log") -> None:
    """
    Sets up logging based on level and logfile.

    Args:
        level (str): Logging level string (e.g., DEBUG, INFO).
        logfile (str): Full path to the log file.
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.FileHandler(logfile), logging.StreamHandler()],
    )

    logging.debug(f"Logging initialized at level: {level}, output to {logfile}")


class ConfigLoader:
    """
    Loads and provides access to configuration data from a YAML file.

    Args:
        path (Optional[str]): Optional path to the configuration file. If None, defaults to ~/.config/chatgpt-dmenu/config.yaml.
    """

    def __init__(self, path: str | None = None) -> None:
        home = os.environ.get("HOME")
        logging.debug(f"ENV HOME={home}")
        self.config_path = path or os.path.expanduser(
            "~/.config/chatgpt-dmenu/config.yaml"
        )
        logging.debug(f"Looking for config at {self.config_path}")
        if not os.path.exists(self.config_path):
            logging.error(f"Config file NOT found at {self.config_path}")
        else:
            logging.info(f"Config file found at {self.config_path}")
            self.config = self._load_config()

    def _load_config(self) -> dict:
        """Loads the YAML config file into a dictionary."""
        if not os.path.exists(self.config_path):
            logging.error(f"Config file not found: {self.config_path}")
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        with open(self.config_path) as f:
            logging.debug(f"Loading config from {self.config_path}")
            return yaml.safe_load(f)

    def get(self, key: str, default: object | None = None) -> object:
        """
        Retrieves a value from the config.

        Args:
            key (str): The config key.
            default (Optional[object]): Default value if key not found.

        Returns:
            object: Value from config or default.
        """
        return self.config.get(key, default)

    def get_contexts(self) -> dict[str, str]:
        """Returns the dictionary of named system prompts (contexts)."""
        return self.config.get("contexts", {})

    def get_list(self, key: str, default: list[str] | None = None) -> list[str]:
        """
        Retrieves a list from the config.

        Args:
            key (str): Key to look for.
            default (Optional[List[str]]): Default list if not found.

        Returns:
            List[str]: List of values.
        """
        return self.config.get(key, default or [])
