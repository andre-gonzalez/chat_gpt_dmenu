import logging
from typing import TYPE_CHECKING

from openai import OpenAI

if TYPE_CHECKING:
    from openai.types.chat import ChatCompletionMessageParam

from typing import cast

from chatgpt_dmenu.config_loader import ConfigLoader

logger = logging.getLogger(__name__)

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Models that only support default temperature (1) and don't accept
# custom temperature values
MODELS_WITHOUT_CUSTOM_TEMPERATURE: set[str] = set()


class OpenRouterClient:
    """
    Handles interaction with the OpenRouter API.

    Args:
        config (ConfigLoader): Provides API key, model, and temperature.
    """

    def __init__(self, config: ConfigLoader) -> None:
        api_key = cast("str | None", config.get("api_key"))
        self.client = OpenAI(api_key=api_key, base_url=OPENROUTER_BASE_URL)
        self.model = str(config.get("model", "openai/gpt-4o-mini"))
        temperature_value = config.get("temperature", 0.7)
        self.temperature = (
            float(temperature_value)
            if isinstance(temperature_value, int | float)
            else 0.7
        )

    def _supports_custom_temperature(self) -> bool:
        """
        Check if the current model supports custom temperature values.

        Returns:
            bool: True if the model supports custom temperature, False otherwise.
        """
        return self.model not in MODELS_WITHOUT_CUSTOM_TEMPERATURE

    def chat(self, system_prompt: str, user_input: str) -> str:
        """
        Sends a message to OpenRouter and returns the response.

        Args:
            system_prompt (str): The system-level instruction for the assistant.
            user_input (str): The user message to process.

        Returns:
            str: The model's response.
        """
        try:
            messages: list[ChatCompletionMessageParam] = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input},
            ]

            logger.info("Sending request to OpenRouter...")
            logger.debug("System prompt: %s", system_prompt)
            logger.debug("User input: %s", user_input[:200])

            # Build request parameters conditionally based on model support
            request_params: dict[str, object] = {
                "model": self.model,
                "messages": messages,
            }

            # Only include temperature if the model supports custom values
            if self._supports_custom_temperature():
                request_params["temperature"] = self.temperature
                logger.debug("Using custom temperature: %s", self.temperature)
            else:
                logger.debug(
                    "Model %s does not support custom temperature, using default (1)",
                    self.model,
                )

            response = self.client.chat.completions.create(**request_params)

            logger.info("Received response from OpenRouter.")
            content = response.choices[0].message.content
            if content is None:
                msg = "Expected response message content to be non-None"
                raise ValueError(msg)
            return content.strip()

        except Exception as e:
            msg = "OpenRouter API error: "
            logger.exception("%s", msg)
            raise RuntimeError(msg) from e
