from typing import Dict
import os
import base64
from openai import AsyncAzureOpenAI, AzureOpenAI
import random
from dotenv import load_dotenv, find_dotenv

# Load environment variables from .env file
load_dotenv(find_dotenv())

# Constants for environment variable keys
API_KEY_ENV = "OPENAI_API_KEY"
API_BASE_ENV = "OPENAI_API_BASE"
DEPLOYMENT_NAME_ENV = "OPENAI_DEPLOYMENT_NAME"


class GPTClient:
    def __init__(
        self,
        temperature: float = 1.0,
        presence_penalty: float = 0.0,
        frequency_penalty: float = 0.0,
        image_detail: str = "high",
    ) -> None:
        """
        Initialize the GPTClient with specified parameters.

        Args:
            temperature (float): Sampling temperature to use.
                                 Lower values means deterministic results.
            presence_penalty (float): Penalize new tokens based on
                                      whether they appear in the text so far.
            frequency_penalty (float): Penalize new tokens based on their
                                       existing frequency in the text so far.

        Returns:
            None
        """
        self.temperature = temperature
        self.presence_penalty = presence_penalty
        self.frequency_penalty = frequency_penalty
        self.image_detail = image_detail

        api_key = os.getenv(API_KEY_ENV)
        azure_endpoint = os.getenv(API_BASE_ENV)

        self.async_client = AsyncAzureOpenAI(
            api_key=api_key, azure_endpoint=azure_endpoint
        )
        self.client = AzureOpenAI(
            api_key=api_key, azure_endpoint=azure_endpoint
        )

    @staticmethod
    def _encode_image(img_path: str) -> str:
        """
        Encode an image to base64 format.

        Args:
            img_path (str): The path to the image file.

        Returns:
            str: The base64 encoded string of the image.
        """
        with open(img_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def _create_messages(
        self,
        input_message: Dict,
        system_message: str,
        human_message: str,
        image_path: str,
    ) -> list:
        """
        Create a list of messages for the GPT model.

        Args:
            input_message (Dict): The input message data.
            system_message (str): The system message template.
            human_message (str): The human message template.
            image_path (str): The path to the image file.

        Returns:
            list: A list of messages formatted for the GPT model.
        """
        system_message = system_message.format(**input_message)
        human_message = human_message.format(**input_message)

        messages = [
            {"role": "system", "content": system_message},
            {
                "role": "user",
                "content": [{"type": "text", "text": human_message}],
            },
        ]

        if image_path:
            url = f"data:image/jpeg;base64,{self._encode_image(image_path)}"
            messages.append(
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": url,
                                "detail": self.image_detail,
                            },
                        }
                    ],
                }
            )
        return messages

    async def arun(
        self,
        input_message: Dict = {},
        system_message: str = "",
        human_message: str = "",
        image_path: str = "",
        response_format: str = "text",
        seed: int = random.randint(0, 9999),
    ) -> str:
        """
        Async function to get result from the GPT model.

        Args:
            input_message (Dict): The input message data.
            system_message (str): The system message template.
            human_message (str): The human message template.
            image_path (str): The path to the image file.
            response_format (str): The response format (default is "text").
                                   For json use "json_object".
            seed (int): The seed for random number generation.

        Returns:
            str: The response from the GPT model.
        """
        messages = self._create_messages(
            input_message, system_message, human_message, image_path
        )

        response = await self.async_client.chat.completions.create(
            model=os.getenv(DEPLOYMENT_NAME_ENV),
            response_format={"type": response_format},
            temperature=self.temperature,
            presence_penalty=self.presence_penalty,
            frequency_penalty=self.frequency_penalty,
            messages=messages,
            seed=seed,
        )

        return response.choices[0].message.content

    def run(
        self,
        input_message: Dict = {},
        system_message: str = "",
        human_message: str = "",
        image_path: str = "",
        response_format: str = "text",
        seed: int = random.randint(0, 9999),
    ) -> str:
        """
        Function to get result from the GPT model.

        Args:
            input_message (Dict): The input message data.
            system_message (str): The system message template.
            human_message (str): The human message template.
            image_path (str): The path to the image file.
            response_format (str): The response format (default is "text").
                                   For json use "json_object".
            seed (int): The seed for random number generation.

        Returns:
            str: The response from the GPT model.
        """
        messages = self._create_messages(
            input_message, system_message, human_message, image_path
        )

        response = self.client.chat.completions.create(
            model=os.getenv(DEPLOYMENT_NAME_ENV),
            response_format={"type": response_format},
            temperature=self.temperature,
            presence_penalty=self.presence_penalty,
            frequency_penalty=self.frequency_penalty,
            messages=messages,
            seed=seed,
        )

        return response.choices[0].message.content

    def __repr__(self) -> str:
        """
        Return a string representation of the GPTClient instance.

        Returns:
            str: A string representation of the GPTClient instance.
        """
        return (
            f"GPTClient(temperature={self.temperature}, "
            f"presence_penalty={self.presence_penalty}, "
            f"frequency_penalty={self.frequency_penalty})"
        )

    def __str__(self) -> str:
        """
        Return a string describing the GPTClient instance.

        Returns:
            str: A string describing the GPTClient instance.
        """
        return (
            f"GPTClient for calling the OpenAI GPT model client with params: "
            f"temperature={self.temperature}, "
            f"presence_penalty={self.presence_penalty}, "
            f"frequency_penalty={self.frequency_penalty}"
        )
