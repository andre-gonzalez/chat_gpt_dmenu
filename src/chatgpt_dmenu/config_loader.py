import logging
import os
import tempfile
from pathlib import Path
from typing import Literal

import yaml

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

logger = logging.getLogger(__name__)


def setup_logging(
    level: str = "INFO",
    logfile: str = str(Path(tempfile.gettempdir()) / "chatgpt-dmenu.log"),
) -> None:
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

    logger.debug("Logging initialized at level: %s, output to %s", level, logfile)


class ConfigLoader:
    """
    Loads and provides access to configuration data from a YAML file.

    Args:
        path (Optional[str]): Optional path to the configuration file.
            If None, defaults to ~/.config/chatgpt-dmenu/config.yaml.
    """

    def __init__(self, path: str | None = None) -> None:
        home = os.environ.get("HOME")
        logger.debug("ENV HOME=%s", home)

        self.config_path = (
            Path(path) if path else Path.home() / ".config/chatgpt-dmenu/config.yaml"
        )
        logger.debug("Looking for config at %s", self.config_path)

        if not self.config_path.exists():
            msg = f"Config file not found: {self.config_path}"
            logger.error(msg)
            raise FileNotFoundError(msg)

        logger.info("Config file found at %s", self.config_path)
        self.config = self._load_config()

    def _load_config(self) -> dict:
        """Loads the YAML config file into a dictionary."""
        if not self.config_path.exists():
            msg = "Config file not found: %s", self.config_path
            logger.error(msg)
            raise FileNotFoundError(msg)

        with self.config_path.open() as f:
            logger.debug("Loading config from %s", self.config_path)
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
