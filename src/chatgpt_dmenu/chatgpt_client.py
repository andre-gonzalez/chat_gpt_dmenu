import logging
from typing import TYPE_CHECKING

from openai import OpenAI

if TYPE_CHECKING:
    from openai.types.chat import ChatCompletionMessageParam

from typing import cast

from chatgpt_dmenu.config_loader import ConfigLoader

logger = logging.getLogger(__name__)


class ChatGPTClient:
    """
    Handles interaction with OpenAI's Chat API using the new SDK.

    Args:
        config (ConfigLoader): Provides API key, model, and temperature.
    """

    def __init__(self, config: ConfigLoader) -> None:
        api_key = cast("str | None", config.get("api_key"))
        self.client = OpenAI(api_key=api_key)
        self.model = str(config.get("model", "gpt-4o"))
        temperature_value = config.get("temperature", 0.7)
        self.temperature = (
            float(temperature_value)
            if isinstance(temperature_value, int | float)
            else 0.7
        )

    def chat(self, system_prompt: str, user_input: str) -> str:
        """
        Sends a message to ChatGPT and returns the response.

        Args:
            system_prompt (str): The system-level instruction for the assistant.
            user_input (str): The user message to process.

        Returns:
            str: ChatGPT's response.
        """
        try:
            messages: list[ChatCompletionMessageParam] = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input},
            ]

            logger.info("Sending request to ChatGPT...")
            logger.debug("System prompt: %s", system_prompt)
            logger.debug("User input: %s", user_input[:200])

            response = self.client.chat.completions.create(
                model=self.model, messages=messages, temperature=self.temperature
            )

            logger.info("Received response from ChatGPT.")
            content = response.choices[0].message.content
            if content is None:
                msg = "Expected response message content to be non-None"
                raise ValueError(msg)
            return content.strip()

        except Exception as e:
            msg = "OpenAI API error: "
            logger.exception("%s", msg)
            raise RuntimeError(msg) from e
