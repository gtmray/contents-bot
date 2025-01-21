import os
import yaml
import logging.config
import requests
from bs4 import BeautifulSoup

# Load configuration from file
with open("./src/config/config.yaml", "r") as config_file:
    config = yaml.safe_load(config_file)

logging.config.fileConfig(config.get("logging_config_file"))

logger = logging.getLogger()


def download_image(url: str) -> None:
    """
    Downloads an image from the given URL and saves it to the 'images' folder.

    Args:
        url (str): The URL of the image to download.

    Raises:
        HTTPError: If the HTTP request for the image fails.

    """
    try:
        logger.info(f"Starting download of image from URL: {url}")

        # Download the image
        image_response = requests.get(url)
        image_response.raise_for_status()
        logger.info("Image downloaded successfully")

        # Save the image to the images folder
        image_folder = os.path.join(os.path.dirname(__file__), "images")
        os.makedirs(image_folder, exist_ok=True)
        logger.info(f"Image folder '{image_folder}' created or already exists")

        # Extract the image name up to .jpg
        image_name = os.path.basename(url).split("?")[0]
        image_path = os.path.join(image_folder, image_name)

        with open(image_path, "wb") as image_file:
            image_file.write(image_response.content)
        logger.info(f"Image saved successfully at '{image_path}'")

    except requests.HTTPError as e:
        logger.error(f"HTTP error occurred while downloading image: {e}")
        raise
    except Exception as e:
        logger.error(f"An error occurred while downloading image: {e}")
        raise


def extract_news_content(url: str) -> dict:
    """
    Extracts news content from a given URL.

    This function sends a GET request to the specified URL, parses the HTML
    content, and extracts the title, article content, and main image URL
    from the page.

    Args:
        url (str): The URL of the news article to extract content from.

    Returns:
        dict: A dictionary containing the extracted content with keys:
            - "title" (str): The title of the article.
            - "content" (str): The main content of the article.
            - "main_image_url" (str or None): The URL of the main image
            - "error" (str): An error message, if an exception occurred.
    """
    try:
        logger.info(f"Starting extraction of news content from URL: {url}")

        # Send a GET request to the URL
        response = requests.get(url)
        response.raise_for_status()
        logger.info("HTTP request successful")

        # Parse the HTML content of the page
        soup = BeautifulSoup(response.text, "html.parser")
        logger.info("HTML content parsed successfully")

        # Extract the title
        title = soup.find("h1").get_text(strip=True)
        logger.info(f"Title extracted: {title}")

        # Extract the article content
        article_body = soup.find_all("div", class_="article__content")
        content = "\n".join([p.get_text(strip=True) for p in article_body])
        logger.info("Article content extracted")

        # Extract the main image
        image_container = soup.find("div", class_="image__container")
        main_image_url = None
        if image_container:
            # Look for the <img> tag inside the container
            img_tag = image_container.find("img")
            if img_tag and img_tag.get("src"):
                main_image_url = img_tag["src"]
                logger.info(f"Main image URL extracted: {main_image_url}")
                download_image(main_image_url)
        else:
            logger.info("No main image found")

        return {
            "title": title,
            "content": content,
            "main_image_url": main_image_url,
        }

    except Exception as e:
        logger.error(f"An error occurred while extracting news content: {e}")
        return {"error": str(e)}


if __name__ == "__main__":
    cnn_url = ""
    result = extract_news_content(cnn_url)

    if "error" in result:
        print("Error:", result["error"])
    else:
        print("Title:", result["title"])
        print("Content:", result["content"])
        print("Main Image URL:", result["main_image_url"])
