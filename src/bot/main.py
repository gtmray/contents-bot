import yaml
import json
import random
import logging.config
from dotenv import load_dotenv, find_dotenv

from fetch_article import extract_news_content
from script_gen import generate_script, generate_prompts, generate_title_desc

from image_gen import generate_images
from tts.text_to_speech import generate_audio
from video_creator import create_video_with_audio
from video_uploader import upload_video, get_authenticated_service

# Load configuration from file
with open("./src/config/config.yaml", "r") as config_file:
    config = yaml.safe_load(config_file)

logging.config.fileConfig(config.get("logging_config_file"))

logger = logging.getLogger()

load_dotenv(find_dotenv())


async def main():
    url = ""
    num_images = 2
    seed = random.randint(0, 100000)

    title_desc_file = "./src/bot/title_desc.json"
    output_audio_file = "./src/bot/output_audio.wav"
    output_img_folder = "./src/bot/output_imgs"
    output_video_file = "./src/bot/output_video.mp4"

    yt_privacy_status = "private"

    article = extract_news_content(url)

    print(f"Article: {article}")
    print("*" * 100)
    script = generate_script(article)

    print(f"Script: {script}")
    print("*" * 100)
    prompts = generate_prompts(script)
    print(f"Prompts: {prompts}")
    print("*" * 100)

    title_desc = generate_title_desc(script)
    with open(title_desc_file, "w") as f:
        f.write(json.dumps(title_desc, indent=4))
    print(f"Title and Description: {title_desc}")
    print("*" * 100)
    generate_audio(script, save_audio=True, output_file=output_audio_file)
    print("*" * 100)

    # Generate images based on prompts
    with open(config.get("comfyui_api_json_path")) as f:
        workflow = json.loads(f.read())
    for prompt in prompts:
        # Update the workflow details
        workflow["6"]["inputs"]["text"] = prompt
        workflow["38"]["inputs"]["filename_prefix"] = "test_temp/t2"
        workflow["27"]["inputs"]["batch_size"] = num_images
        workflow["31"]["inputs"]["seed"] = seed

        images = await generate_images(
            workflow, save_images=True, output_folder=output_img_folder
        )
        print("Images received:", images)

    # Create Video
    create_video_with_audio(
        output_img_folder, output_audio_file, output_video_file
    )

    # Authenticate and upload
    youtube_service = get_authenticated_service()
    upload_video(
        youtube_service,
        output_video_file,
        title_desc["title"],
        title_desc["description"],
        yt_privacy_status,
    )


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
