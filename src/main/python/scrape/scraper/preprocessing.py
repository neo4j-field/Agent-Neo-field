import requests
from bs4 import BeautifulSoup
from typing import List
from itertools import chain

#TODO: Pull these into a seperate module or encapsulate them in the ScrapeLangChain
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


def concatenate_unique_ordered(*lists:List) -> List:
    seen = set()
    result = []
    for item in chain(*lists):
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result