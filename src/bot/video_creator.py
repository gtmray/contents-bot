import os
from PIL import Image
import logging.config
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
from moviepy.audio.io.AudioFileClip import AudioFileClip

logging.config.fileConfig("../config/logging_config.ini")
logger = logging.getLogger()


def preprocess_images(images_folder: str, target_resolution: tuple) -> list:
    """
    Resize all images in the folder to the target resolution.

    Args:
        images_folder (str): Path to the folder containing image files.
        target_resolution (tuple): Tuple (width, height) for resizing images.

    Returns:
        list: List of paths to the resized images.
    """
    resized_images = []
    temp_folder = os.path.join(images_folder, "resized")
    os.makedirs(temp_folder, exist_ok=True)
    logger.info(
        f"Created temporary folder for resized images at {temp_folder}"
    )

    for img_file in sorted(os.listdir(images_folder)):
        if img_file.lower().endswith(("png", "jpg", "jpeg", "webp")):
            img_path = os.path.join(images_folder, img_file)
            try:
                with Image.open(img_path) as img:
                    img_resized = img.resize(
                        target_resolution, Image.Resampling.LANCZOS
                    )
                    resized_path = os.path.join(temp_folder, img_file)
                    img_resized.save(resized_path)
                    resized_images.append(resized_path)
                    logger.info(
                        f"Resized and saved image {img_file} to {resized_path}"
                    )
            except Exception as e:
                logger.error(f"Failed to process image {img_file}: {e}")

    if not resized_images:
        logger.warning(
            "No images were resized. Please check the images folder."
        )

    return resized_images


def create_video_with_audio(
    images_folder: str,
    audio_file: str,
    output_file: str,
    target_resolution: tuple = (1080, 1080),
) -> None:
    """
    Create a video from a folder of images and an audio file.

    Args:
        images_folder (str): Path to the folder containing image files.
        audio_file (str): Path to the audio file.
        output_file (str): Path to the output video file.
        target_resolution (tuple, optional): Tuple (width, height) for resizing
                                             images. Defaults to (1080, 1080).

    Returns:
        None
    """
    logger.info("Starting video creation process")
    logger.info(f"Images folder: {images_folder}")
    logger.info(f"Audio file: {audio_file}")
    logger.info(f"Output file: {output_file}")
    logger.info(f"Target resolution: {target_resolution}")

    # Preprocess images to ensure they have the same resolution
    try:
        resized_images = preprocess_images(images_folder, target_resolution)
    except Exception as e:
        logger.error(f"Error during image preprocessing: {e}")
        raise

    if not resized_images:
        logger.error("No images found in the specified folder.")
        raise ValueError("No images found in the specified folder.")

    # Load the audio file
    try:
        audio = AudioFileClip(audio_file)
        logger.info(f"Loaded audio file: {audio_file}")
    except Exception as e:
        logger.error(f"Error loading audio file: {e}")
        raise

    # Calculate the duration each image should be displayed
    total_audio_duration = audio.duration
    image_duration = total_audio_duration / len(resized_images)
    logger.info(f"Total audio duration: {total_audio_duration} seconds")
    logger.info(f"Each image will be displayed for: {image_duration} seconds")

    # Use ImageSequenceClip for better performance
    try:
        video = ImageSequenceClip(
            resized_images, durations=[image_duration] * len(resized_images)
        )
        logger.info("Created video sequence from images")
    except Exception as e:
        logger.error(f"Error creating video sequence: {e}")
        raise

    # Set the audio to the video
    video.audio = audio

    try:
        video.write_videofile(
            output_file,
            codec="libx264",
            audio_codec="libmp3lame",
            audio_bitrate="192k",
            fps=24,
        )
        logger.info(f"Video file created successfully: {output_file}")
    except Exception as e:
        logger.error(f"Error writing video file: {e}")
        raise


if __name__ == "__main__":

    images_folder = "./images"
    audio_file = "./outputs/output.wav"
    output_file = "./outputs/v1.mp4"

    create_video_with_audio(images_folder, audio_file, output_file)
