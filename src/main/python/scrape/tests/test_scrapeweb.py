from unittest import TestCase, mock
from scrape.scraper.scrapeweb import ScrapeLangChain


class TestScrapeLangChain(TestCase):

    @mock.patch('scrape.scraper.scrapeweb.get_sitemap_urls')
    @mock.patch('scrape.scraper.scrapeweb.get_practitioner_guide_md')
    @mock.patch('scrape.scraper.scrapeweb.get_other_articles')
    def test_scrape_sites_into_lanchaindocs(self, mock_get_other_articles,
                                            mock_get_practitioner_guide_md, mock_get_sitemap_urls):

        # Mock return values for the functions using the provided lists
        mock_get_sitemap_urls.return_value = [
            'https://neo4j.com/docs/graph-data-science/current/sitemap.xml',
            'https://neo4j.com/docs/graph-data-science-client/current/sitemap.xml'
        ]

        mock_get_practitioner_guide_md.return_value = [
            'https://github.com/danb-neo4j/gds-guide/blob/main/README.md',
            'https://github.com/danb-neo4j/gds-guide/blob/main/gds-resources.md'
        ]

        mock_get_other_articles.return_value = [
            'https://neo4j.com/developer-blog/get-started-with-neo4j-gds-python-client/',
            'https://medium.com/neo4j/graph-data-modeling-categorical-variables-dd8a2845d5e0'
        ]


        # Instantiate the object
        scraper = ScrapeLangChain()
        scraper.scrape_sites_into_langchain_docs()