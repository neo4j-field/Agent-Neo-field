import requests
from bs4 import BeautifulSoup
from typing import List
from itertools import chain


def parse_sitemap(sitemap: str) -> List[str]:
    response = requests.get(sitemap)
    soup = BeautifulSoup(response.content, "xml")
    urls = [element.text for element in soup.find_all("loc")]
    return urls


def parse_sitemaps_tolist(sitemaps: List[str]) -> List[str]:
    neo4j_doc_sites = []

    for sitemap in sitemaps:
        try:
            neo4j_doc_sites.extend(parse_sitemap(sitemap))
        except Exception as e:
            print(f"Error parsing sitemap {sitemap}: {e}")

    return neo4j_doc_sites


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
