import os
import re
import numpy as np
import torch
import logging.config
from dotenv import load_dotenv, find_dotenv
from scipy.io.wavfile import write
from .model import build_model
from .kokoro import tokenize, phonemize, generate

logging.config.fileConfig("../config/logging_config.ini")
logger = logging.getLogger()

load_dotenv(find_dotenv())

# Constants
DEFAULT_MODEL_PATH = os.getenv("DEFAULT_MODEL_PATH")
DEFAULT_VOICES_DIR = os.getenv("DEFAULT_VOICES_DIR")
DEFAULT_VOICE_INDEX = 2
MAX_TOKENS = 500
SAMPLE_RATE = 24000


class KokoroVoiceModel:
    """
    A class to handle the initialization and use of the Kokoro model
    """

    def __init__(
        self,
        model_path=DEFAULT_MODEL_PATH,
        voice_index=DEFAULT_VOICE_INDEX,
        voices_dir=DEFAULT_VOICES_DIR,
    ):
        """
        Initializes the Kokoro model and loads the specified voice pack.

        Args:
            model_path (str): Path to the model file.
            voice_index (int): Index of the voice to use from the VOICE_NAME
            voices_dir (str): Directory where voice packs are stored.
        """
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = self._load_model(model_path)
        self.voicepack, self.voice_name = self._load_voicepack(
            voice_index, voices_dir
        )

    def _load_model(self, model_path):
        """
        Loads and returns the Kokoro model.

        Args:
            model_path (str): Path to the model file.

        Returns:
            torch.nn.Module: The loaded model.
        """
        return build_model(model_path, self.device)

    def _load_voicepack(self, voice_index, voices_dir):
        """
        Loads the voice pack and returns the voice tensor with voice name

        Args:
            voice_index (int): Index of the voice to use.
            voices_dir (str): Directory where voice packs are stored.

        Returns:
            tuple: (voicepack, voice_name)
        """
        voice_names = [
            "af",
            "af_bella",
            "af_sarah",
            "am_adam",
            "am_michael",
            "bf_emma",
            "bf_isabella",
            "bm_george",
            "bm_lewis",
            "af_nicole",
            "af_sky",
        ]
        if not (0 <= voice_index < len(voice_names)):
            raise ValueError(f"Invalid voice index: {voice_index}")

        voice_name = voice_names[voice_index]
        voicepack_path = f"{voices_dir}/{voice_name}.pt"
        print(f"Loading voice pack from {voicepack_path}...")
        voicepack = torch.load(voicepack_path, weights_only=True).to(
            self.device
        )

        return voicepack, voice_name


def split_text_by_sentences(text):
    """
    Splits a given text into sentences based on punctuation and whitespace.

    Args:
        text (str): The text to split.

    Returns:
        list: A list of sentences.
    """
    return re.split(r"(?<=[.!?]) +", text.strip())


def tokenize_sentence(sentence, lang="a"):
    """
    Tokenizes and phonemizes a sentence.

    Args:
        sentence (str): The sentence to tokenize.
        lang (str): Language code for phonemization (default "a").

    Returns:
        list: A list of tokens.
    """
    phonemized_sentence = phonemize(sentence, lang)
    return tokenize(phonemized_sentence)


def process_text_chunks(text, lang="a", max_tokens=MAX_TOKENS):
    """
    Splits text into manageable chunks of tokens if they exceed max_tokens.

    Args:
        text (str): The text to process.
        lang (str): Language code for phonemization (default "a").
        max_tokens (int): Maximum number of tokens per chunk.

    Returns:
        list: A list of text chunks.
    """
    sentences = split_text_by_sentences(text)
    chunks = []
    current_chunk = []
    current_token_count = 0

    for sentence in sentences:
        tokens = tokenize_sentence(sentence, lang)
        token_count = len(tokens)

        if current_token_count + token_count > max_tokens:
            chunks.append(" ".join(current_chunk))
            current_chunk = [sentence]
            current_token_count = token_count
        else:
            current_chunk.append(sentence)
            current_token_count += token_count

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


def save_audio_output(audio_data, filename, sample_rate=SAMPLE_RATE):
    """
    Saves a 1D numpy array of audio data to a .wav file.

    Args:
        audio_data (numpy array): The audio data to save.
        filename (str): The output .wav file name.
        sample_rate (int): The audio sample rate.
    """
    audio_data = np.asarray(audio_data, dtype=np.int16)
    write(filename, sample_rate, audio_data)
    print(f"Audio saved as {filename}")


def normalize_audio(audio_data):
    """
    Normalize audio data to fit within the range of int16.

    Args:
        audio_data (numpy array): The audio data to normalize.

    Returns:
        numpy array: The normalized audio data.
    """
    return (audio_data / np.max(np.abs(audio_data)) * 32767).astype(np.int16)


def generate_audio(
    texts,
    save_audio: bool = False,
    lang: str = "a",
    output_file: str = "output.wav",
):
    """
    Main function to initialize the Kokoro model, process text, generate audio,
    and save the output.

    Args:
        texts (str): The input text to convert to speech.
        save_audio (bool): Whether to save the generated audio to a file.
        lang (str): Language code for phonemization.
        output_file (str): The output .wav file name.
    """
    try:
        kokoro = KokoroVoiceModel()
        all_audio = []

        for text in texts.split("\n"):
            text = text.strip()
            if not text:
                continue

            chunks = process_text_chunks(text)
            for chunk in chunks:
                logger.info(
                    f"Processing chunk: {chunk[:50]}..."
                )  # Show the first 50 characters of the chunk
                audio, _ = generate(
                    kokoro.model, chunk, kokoro.voicepack, lang=lang
                )
                all_audio.append(audio)

        all_audio = np.concatenate(all_audio)
        logger.info("Audio generation complete.")

        if save_audio:
            normalized_audio = normalize_audio(all_audio)
            save_audio_output(normalized_audio, output_file)
            logger.info(f"Audio saved as {output_file}")

    except Exception as e:
        logger.error(f"An error occurred during audio generation: {e}")
        raise
