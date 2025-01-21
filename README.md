# Automated YouTube Video Creator and Uploader from News Articles

This project automates the creation and uploading of YouTube videos directly from news articles. It scrapes the given news article URL, generates a video script, converts text to audio, creates visuals, combines them into a video, and uploads the final video to YouTube using the YouTube Data API. This is intended for educational purposes only.

## Features
- **News Article Scraping**: Extracts content from a given news article URL.
- **Script Generation**: Automatically generates a script based on the article.
- **Image Generation**: Creates images using the Flux model based on the script.
- **Text-to-Speech Conversion**: Converts the script into audio using advanced TTS models.
- **Video Creation**: Combines generated audio and images into a video.
- **YouTube Upload**: Automatically uploads the final video to YouTube with a generated title and description.

## How It Works
### Pipeline Overview
1. **Input**: Provide a news article URL.
2. **Article Scraping**: Extract the text content using `fetch_article.py`.
3. **Script Generation**: Use GPT models to generate a script, prompts, and a YouTube title and description.
4. **Image Generation**: Use the Flux model to generate images based on prompts.
5. **Audio Creation**: Convert the script to audio using TTS models.
6. **Video Assembly**: Combine images and audio into a video.
7. **YouTube Upload**: Use the YouTube Data API to upload the video with appropriate metadata.


## Prerequisites
- Python 3.9+
- Poetry (for dependency management)
- GPT Model, YouTube Data API credentials
- GPU-enabled server for image generation

## Installation
1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd <repository_name>
   ```
2. Install dependencies using Poetry:
   ```bash
   poetry install
   ```
3. Set up environment variables:
   - Create a `.env` file in the root directory.
   - Add required API keys and configuration values.

4. Configure the Flux model:
   - Set up a server with the Flux model enabled (or change your model accordingly).


## Usage
1. Edit the `main.py` file to include your desired news article URL.
2. Run the pipeline:
   ```bash
   poetry run python src/bot/main.py
   ```
3. Check the generated video in the `src/bot/` directory and confirm its upload status on YouTube.

## Configuration
- **Logging**: Modify `logging_config.ini` in the `config` directory to adjust log levels and formatting.
- **Flux Model**: Update `flux_dev.json` for custom workflows or image generation parameters.
- **YouTube Privacy Settings**: Adjust the `yt_privacy_status` variable in `main.py` to set video visibility (`public`, `private`, or `unlisted`).

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.

## Acknowledgments
- [Flux Model](https://blackforestlabs.ai/)
- [Text-to-Speech Model](https://huggingface.co/hexgrad/Kokoro-82M)
- [YouTube Data API](https://developers.google.com/youtube/v3)

---
For questions or contributions, please create an issue or submit a pull request!
