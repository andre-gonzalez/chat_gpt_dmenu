import logging

from chatgpt_dmenu.config_loader import ConfigLoader

logger = logging.getLogger(__name__)


class ContextManager:
    """
    Manages ChatGPT prompt contexts and dynamically formats them.

    Args:
        config (ConfigLoader): Instance of ConfigLoader containing the context config.
    """

    def __init__(self, config: ConfigLoader) -> None:
        self.contexts: dict[str, str] = config.get_contexts()

    def get_contexts(self) -> list[str]:
        """Returns the list of context names."""
        return list(self.contexts.keys())

    def get_prompt(
        self,
        name: str,
        audience: str | None = None,
        tone: str | None = None,
        person: str | None = None,
    ) -> str:
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
        logger.debug(
            "Building prompt for context='%s', audience='%s', tone='%s', person='%s'",
            name,
            audience,
            tone,
            person,
        )
        return (
            prompt.replace("{audience}", audience or "the recipient")
            .replace("{tone}", tone or "friendly but professional")
            .replace("{person}", person or "there")
        )
