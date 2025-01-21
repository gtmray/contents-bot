import yaml
import logging.config
from bot.prompts import (
    script_gen_sys_prompt,
    script_gen_human_prompt,
    prompts_gen_sys_prompt,
    prompts_gen_human_prompt,
    title_gen_sys_prompt,
    title_gen_human_prompt,
)
from utils import extract_json, GPTClient

# Load configuration from file
with open("./src/config/config.yaml", "r") as config_file:
    config = yaml.safe_load(config_file)

logging.config.fileConfig(config.get("logging_config_file"))

logger = logging.getLogger()

gpt = GPTClient(temperature=config.get("temperature"))


def generate_script(article: str) -> str:
    """
    Generates a script based on the provided article using a GPT model.

    Args:
        article (str): The article content to generate the script from.

    Returns:
        str: The generated script.
    """
    logger.info("Starting script generation.")
    input_msg = {"article": article}
    logger.debug(f"Input message for GPT: {input_msg}")

    script = gpt.run(
        input_message=input_msg,
        system_message=script_gen_sys_prompt,
        human_message=script_gen_human_prompt,
    )

    logger.debug(f"Generated script: {script}")
    logger.info("Script generation completed.")
    return script


def generate_prompts(script: str) -> list:
    """
    Generates image prompts based on the provided script using a GPT model.

    Args:
        script (str): The input script for which image prompts need to be
                      generated.

    Returns:
        list: A list of image prompts extracted from the GPT model's response.
    """
    logger.info("Starting image prompts generation.")
    input_msg = {"script": script}
    logger.debug(f"Input message for GPT: {input_msg}")

    prompts = gpt.run(
        input_message=input_msg,
        system_message=prompts_gen_sys_prompt,
        human_message=prompts_gen_human_prompt,
    )

    logger.debug(f"Generated prompts: {prompts}")
    logger.info("Image prompts generation completed.")
    return extract_json(prompts)["image_prompts"]


def generate_title_desc(script: str) -> dict:
    """
    Generates a title and description for the given script using a GPT model.

    Args:
        script (str): The input script for which the title and description
                      need to be generated.

    Returns:
        dict: A dictionary containing the generated title and description.
    """
    logger.info("Starting title and description generation.")
    input_msg = {"script": script}
    logger.debug(f"Input message for GPT: {input_msg}")

    title_descriptions = gpt.run(
        input_message=input_msg,
        system_message=title_gen_sys_prompt,
        human_message=title_gen_human_prompt,
    )

    logger.debug(f"Generated title and description: {title_descriptions}")
    logger.info("Title and description generation completed.")
    return extract_json(title_descriptions)
