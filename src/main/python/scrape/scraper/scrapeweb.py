from typing import List
import requests
from bs4 import BeautifulSoup
from typing import List
from itertools import chain
import langchain
from langchain.document_loaders import UnstructuredURLLoader
from langchain.schema.document import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import VertexAIEmbeddings



def get_sitemap_urls() -> List[str]:
    # TODO: Check https://neo4j.com/robots.txt to discover additional sitemaps or updates
    return [
        'https://neo4j.com/docs/graph-data-science/current/sitemap.xml',  # core GDS
        'https://neo4j.com/docs/graph-data-science-client/current/sitemap.xml',  # GDS client
        'https://neo4j.com/docs/python-manual/current/sitemap.xml',  # Neo4j python client
        'https://neo4j.com/docs/cypher-manual/current/sitemap.xml',  # Cypher manual
        'https://neo4j.com/docs/apoc/current/sitemap.xml',  # APOC manual
        'https://neo4j.com/docs/aura/sitemap.xml',  # Aura DB and DS
        'https://neo4j.com/docs/operations-manual/5/sitemap.xml'  # Neo4j5
    ]


def get_practitioner_guide_md() -> List[str]:
    # TODO: programmatically pull this from here -> https://github.com/danb-neo4j/gds-guide/tree/main
    return [
        'https://github.com/danb-neo4j/gds-guide/blob/main/README.md',
        'https://github.com/danb-neo4j/gds-guide/blob/main/gds-resources.md',
        'https://github.com/danb-neo4j/gds-guide/blob/main/graph-data-modeling.md',
        'https://github.com/danb-neo4j/gds-guide/blob/main/graph-eda.md',
        'https://github.com/danb-neo4j/gds-guide/blob/main/graphs-llms.md',
        'https://github.com/danb-neo4j/gds-guide/blob/main/neo4j-resources.md',
        'https://github.com/danb-neo4j/gds-guide/blob/main/usecase-specific.md',
        'https://github.com/danb-neo4j/gds-guide/blob/main/algorithms/README.md',
        'https://github.com/danb-neo4j/gds-guide/blob/main/algorithms/gds_centrality.md',
        'https://github.com/danb-neo4j/gds-guide/blob/main/algorithms/gds_community.md',
        'https://github.com/danb-neo4j/gds-guide/blob/main/algorithms/gds_pathfinding.md',
        'https://github.com/danb-neo4j/gds-guide/blob/main/algorithms/gds_similarity.md',
        'https://github.com/danb-neo4j/gds-guide/blob/main/embeddings/README.md',
        'https://github.com/danb-neo4j/gds-guide/blob/main/embeddings/fastrp.md',
        'https://github.com/danb-neo4j/gds-guide/blob/main/embeddings/graphSAGE.md',
        'https://github.com/danb-neo4j/gds-guide/blob/main/embeddings/hashGNN.md',
        'https://github.com/danb-neo4j/gds-guide/blob/main/embeddings/node2vec.md',
    ]


def get_other_articles() -> List[str]:
    return [
        'https://neo4j.com/developer-blog/get-started-with-neo4j-gds-python-client/',
        'https://medium.com/neo4j/graph-data-modeling-categorical-variables-dd8a2845d5e0',
        'https://medium.com/neo4j/graph-modeling-labels-71775ff7d121',
        'https://medium.com/neo4j/graph-data-modeling-all-about-relationships-5060e46820ce',
        'https://medium.com/neo4j/graph-data-modeling-keys-a5a5334a1297'
        'https://medium.com/neo4j/modeling-patient-journeys-with-neo4j-d0785fbbf5a2'
        'https://neo4j.com/docs/graph-data-science/current/installation/System-requirements/',
        'https://neo4j.com/developer/kb/understanding-memory-consumption/',
        'https://neo4j.com/developer-blog/exploring-fraud-detection-neo4j-graph-data-science-summary/',
        'https://neo4j.com/developer-blog/exploring-fraud-detection-neo4j-graph-data-science-part-1/',
        'https://neo4j.com/developer-blog/exploring-fraud-detection-neo4j-graph-data-science-part-2/',
        'https://neo4j.com/developer-blog/exploring-fraud-detection-neo4j-graph-data-science-part-3/',
        'https://neo4j.com/developer-blog/exploring-fraud-detection-neo4j-graph-data-science-part-4/',
        'https://medium.com/neo4j/using-neo4j-graph-data-science-in-python-to-improve-machine-learning-models-c55a4e15f530',
        'https://medium.com/neo4j/user-segmentation-based-on-node-roles-in-the-peer-to-peer-payment-network-1a766c60a4ee',
        'https://medium.com/data-science-at-microsoft/using-graphs-to-model-and-analyze-the-customer-journey-4b1f1e9f3696',
        'https://towardsdatascience.com/exploring-practical-recommendation-engines-in-neo4j-ff09fe767782',
        'https://neo4j.com/developer-blog/supply-chain-neo4j-gds-bloom/',
        'https://neo4j.com/developer-blog/gds-supply-chains-metrics-performance-python/',
        'https://neo4j.com/developer-blog/gds-supply-chain-pathfinding-optimization/',
        'https://medium.com/neo4j/knowledge-graphs-llms-real-time-graph-analytics-89b392eaaa95',
        'https://medium.com/neo4j/knowledge-graphs-llms-multi-hop-question-answering-322113f53f51',
        'https://towardsdatascience.com/integrate-llm-workflows-with-knowledge-graph-using-neo4j-and-apoc-27ef7e9900a2',
        'https://medium.com/neo4j/knowledge-graphs-llms-fine-tuning-vs-retrieval-augmented-generation-30e875d63a35',
        'https://medium.com/neo4j/langchain-cypher-search-tips-tricks-f7c9e9abca4d',
        'https://towardsdatascience.com/langchain-has-added-cypher-search-cb9d821120d5',
        'https://medium.com/neo4j/generating-cypher-queries-with-chatgpt-4-on-any-graph-schema-a57d7082a7e7',
        'https://towardsdatascience.com/fine-tuning-an-llm-model-with-h2o-llm-studio-to-generate-cypher-statements-3f34822ad5',
        'https://towardsdatascience.com/implementing-a-sales-support-agent-with-langchain-63c4761193e7',
        'https://towardsdatascience.com/integrating-neo4j-into-the-langchain-ecosystem-df0e988344d2',
        'https://medium.com/neo4j/context-aware-knowledge-graph-chatbot-with-gpt-4-and-neo4j-d3a99e8ae21e',
        'https://towardsdatascience.com/what-happened-with-apoc-in-neo4j-v5-core-and-extended-edition-23994cdf0a2c',
        'https://medium.com/neo4j/creating-a-knowledge-graph-from-video-transcripts-with-gpt-4-52d7c7b9f32c',
        'https://towardsdatascience.com/how-to-use-cypher-aggregations-in-neo4j-graph-data-science-library-5d8c40c2670c',
        'https://medium.com/neo4j/enhancing-word-embedding-with-graph-neural-networks-c26d8e54fe4a',
        'https://medium.com/neo4j/knowledge-graph-based-chatbot-with-gpt-3-and-neo4j-c4ebbd325ed',
        'https://towardsdatascience.com/use-chatgpt-to-query-your-neo4j-database-78680a05ec2',
        'https://towardsdatascience.com/how-cypher-changed-in-neo4j-v5-d0f10cbb60bf',
        'https://towardsdatascience.com/analyze-your-website-with-nlp-and-knowledge-graphs-88e291f6cbf4',
        'https://towardsdatascience.com/investigate-family-connections-between-house-of-dragon-and-game-of-thrones-characters-ff2afd5bdb82',
        'https://medium.com/neo4j/user-segmentation-based-on-node-roles-in-the-peer-to-peer-payment-network-1a766c60a4ee',
        'https://towardsdatascience.com/analyzing-the-evolution-of-life-on-earth-with-neo4j-7daeeb1e032d',
        'https://medium.com/neo4j/how-to-get-started-with-the-neo4j-graph-data-science-python-client-56209d9b0d0d',
        'https://towardsdatascience.com/extract-knowledge-from-text-end-to-end-information-extraction-pipeline-with-spacy-and-neo4j-502b2b1e0754',
        'https://towardsdatascience.com/batching-transactions-in-neo4j-1001d12c9a4a',

    ]




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


class ScrapeLangChain:
    def __init__(self):
        self._site_maps = get_sitemap_urls()
        self._practitioner_guides = get_practitioner_guide_md()
        self._other_articles = get_other_articles()
        self._docs = concatenate_unique_ordered(self._site_maps,self._practitioner_guides,self._other_articles)



    def scrape_sites_into_langchain_docs(self) -> List[Document]:
        documents = None
        try:
            loader = UnstructuredURLLoader(self._docs)
            documents = loader.load()
            print([(type(x)) for x in documents])
        except Exception as e:
            print(f"Error loading documents from URLs: {e}")
        return type(documents)


    def __str__(self):
        doc_strings = [str(doc) for doc in self._docs]
        return "\n".join(["ScrapeLangChain Documents:"] + doc_strings)





