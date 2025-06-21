import logging
from typing import List
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from chatgpt_dmenu.config_loader import ConfigLoader

class ChatGPTClient:

    """
    Handles interaction with OpenAI's Chat API using the new SDK.

    Args:
        config (ConfigLoader): Provides API key, model, and temperature.
    """
    def __init__(self, config: ConfigLoader) -> None:
        self.client = OpenAI(api_key=config.get("api_key"))
        self.model: str = config.get("model", "gpt-4o")
        self.temperature: float = config.get("temperature", 0.7)

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
            messages: List[ChatCompletionMessageParam] = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ]

            logging.info("Sending request to ChatGPT...")
            logging.debug(f"System prompt: {system_prompt}")
            logging.debug(f"User input: {user_input[:200]}")  # Don't log full text

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature
            )

            logging.info("Received response from ChatGPT.")
            return response.choices[0].message.content.strip()

        except Exception as e:
            logging.error(f"OpenAI API error: {e}")
            raise RuntimeError(f"API error: {e}")
