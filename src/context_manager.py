import logging
from typing import Optional, List, Dict
from src.config_loader import ConfigLoader

class ContextManager:
    """
    Manages ChatGPT prompt contexts and dynamically formats them.

    Args:
        config (ConfigLoader): Instance of ConfigLoader containing the context config.
    """
    def __init__(self, config: ConfigLoader) -> None:
        self.contexts: Dict[str, str] = config.get_contexts()

    def get_contexts(self) -> List[str]:
        """Returns the list of context names."""
        return list(self.contexts.keys())

    def get_prompt(self, name: str, audience: Optional[str] = None,
                   tone: Optional[str] = None, person: Optional[str] = None) -> str:
        """
        Returns a context prompt with placeholders filled.

        Args:
            name (str): Context name.
            audience (Optional[str]): Target audience for the prompt.
            tone (Optional[str]): Tone to be used in the output.
            person (Optional[str]): Person the message is addressed to.

        Returns:
            str: Final formatted prompt.
        """
        prompt = self.contexts.get(name, "")
        logging.debug(f"Building prompt for context='{name}', audience='{audience}', tone='{tone}', person='{person}'")
        return (
            prompt.replace("{audience}", audience or "the recipient")
                  .replace("{tone}", tone or "friendly but professional")
                  .replace("{person}", person or "there")
        )
