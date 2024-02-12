import requests
from bs4 import BeautifulSoup
from typing import List
from itertools import chain
import regex as re





def remove_newlines(text: str) -> str:
    return text.replace('\n\n', ' ').replace('\n', ' ')

def remove_unwanted_phrase(text: str) -> str:
    return text.replace('Was this page helpful?', '')


def concatenate_unique_ordered(*lists:List) -> List:
    seen = set()
    result = []
    for item in chain(*lists):
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def extract_list_from_json(json_data: dict, key: str = None) -> list:
    if key:
        return json_data.get(key, [])
    elif len(json_data) == 1:
        single_key = next(iter(json_data.keys()))
        if isinstance(json_data[single_key], list):
            return json_data[single_key]
    return []

def remove_filler_words(text: str) -> str:
    """
    This method removes filler words such as "um" or "ah" from a given text.
    """

    filler_words = ["um", "ah", "uh"]

    for word in filler_words:
        text = text.replace(word, "")

    # remove extra whitespace
    return text.strip()

def fix_neo4j_spelling(text: str) -> str:
    """
    This method corrects the spelling of neo4j in transcripts which is *always* wrong.
    """

    # safe_words = ['freon', 'fern', 'roof']
    return re.sub(r"\b([neoforja ]{4,8})\b", "Neo4j", text, flags=re.IGNORECASE)





