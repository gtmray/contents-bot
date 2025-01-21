import os
import requests
from typing import List, Dict
from dotenv import load_dotenv, find_dotenv
import json


load_dotenv(find_dotenv())


def bing_search(query: str, k: int) -> List[Dict]:
    """Get top k results of the query from the bing search

    Args:
        query (str): Query text
        k (int): Number of results to get

    Returns:
        List[Dict]: List of results with title and description
    """
    headers = {"Ocp-Apim-Subscription-Key": os.getenv("BING_SUBSCRIPTION_KEY")}
    params = {
        "q": query,
        "count": k,
    }

    try:
        response = requests.get(
            os.getenv("BING_SEARCH_URL"), headers=headers, params=params
        )
        response.raise_for_status()
        search_results = response.json()
        top_results = []
        for result in search_results["webPages"]["value"]:
            top_results.append(
                {
                    "Title": result["name"],
                    "URL": result["url"],
                    "Description": result["snippet"],
                }
            )

        return top_results

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return []


def extract_json(raw_result: str) -> dict:
    """Extracts a JSON string from a raw result .

    Args:
        raw_result (str): The raw result from the GPT API.

    Returns:
        str: The JSON string.
    """
    return json.loads(raw_result.strip("```json"))
