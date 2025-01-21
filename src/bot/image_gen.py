import os
import yaml
import asyncio
from websockets import connect
import aiohttp
import logging.config
import uuid
from PIL import Image
from io import BytesIO

# Load configuration from file
with open("./src/config/config.yaml", "r") as config_file:
    config = yaml.safe_load(config_file)

logging.config.fileConfig(config.get("logging_config_file"))
logger = logging.getLogger()

server_address = os.getenv("IMG_GEN_SERVER")
client_id = str(uuid.uuid4())


class RetryAsync:
    def __init__(self, retries=3, delay=2):
        self.retries = retries
        self.delay = delay

    def __call__(self, func):
        async def wrapper(*args, **kwargs):
            for attempt in range(self.retries):
                try:
                    logger.info(
                        f"Attempt {attempt + 1} for function {func.__name__}"
                    )
                    return await func(*args, **kwargs)
                except Exception as e:
                    logger.error(
                        f"Error on attempt {attempt + 1} for function "
                        f"{func.__name__}: {e}"
                    )
                    logger.info(f"Retrying in {self.delay} seconds...")
                    if attempt < self.retries - 1:
                        await asyncio.sleep(self.delay)
                    else:
                        logger.error(
                            f"All {self.retries} attempts failed for function "
                            f"{func.__name__}"
                        )
                        raise e

        return wrapper


@RetryAsync(retries=3, delay=2)
async def queue_prompt(prompt):
    url = f"http://{server_address}/prompt"
    data = {"prompt": prompt, "client_id": client_id}

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            response.raise_for_status()  # Raise error for HTTP 4xx/5xx
            print(f"Prompt queued successfully: {response.status}")
            print(f"Response: {await response.json()}")
            return await response.json()


@RetryAsync(retries=3, delay=2)
async def get_image(filename, subfolder, folder_type):
    url = f"http://{server_address}/view"
    params = {
        "filename": filename,
        "subfolder": subfolder,
        "type": folder_type,
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            response.raise_for_status()
            return await response.read()


@RetryAsync(retries=10, delay=30)
async def get_history(prompt_id):
    url = f"http://{server_address}/history/{prompt_id}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response.raise_for_status()
            history = await response.json()
            return history[prompt_id]


@RetryAsync(retries=5, delay=3)
async def generate_images(
    workflow, save_images=False, output_folder="output_images"
):
    async with connect(f"ws://{server_address}/ws"):
        wf_data = await queue_prompt(workflow)
        wf_id = wf_data[
            "prompt_id"
        ]  # Get the workflow ID as represented by prompt_id
        output_images = {}

        # Fetch history and images
        history = await get_history(wf_id)
        for node_id in history["outputs"]:
            node_output = history["outputs"][node_id]
            images_output = []
            if "images" in node_output:
                for image in node_output["images"]:
                    print(image["filename"], image["subfolder"], image["type"])
                    image_data = await get_image(
                        image["filename"], image["subfolder"], image["type"]
                    )
                    images_output.append(image_data)
            output_images[node_id] = images_output

        for idx, img in enumerate(output_images[node_id]):
            bytesIO = BytesIO(img)
            preview_image = Image.open(bytesIO)

            # Save the image
            if save_images:
                if not os.path.exists(output_folder):
                    os.makedirs(output_folder)
                image_path = f"{output_folder}/img_{idx}.png"
                preview_image.save(image_path)
                logger.info(f"Image saved as {image_path}")
        return output_images
