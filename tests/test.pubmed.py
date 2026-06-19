import unittest
from unittest.mock import patch, Mock

import requests

from paper_search_mcp.academic_platforms.pubmed import PubMedSearcher

class TestPubMedSearcher(unittest.TestCase):
    def test_search(self):
        searcher = PubMedSearcher()
        papers = searcher.search("machine learning", max_results=10)
        print(f"Found {len(papers)} papers for query 'machine learning':")
        for i, paper in enumerate(papers, 1):
            print(f"{i}. {paper.title} (ID: {paper.paper_id})")
        self.assertEqual(len(papers), 10)
        self.assertTrue(papers[0].title)
    
    def test_pdf_unsupported(self):
        searcher = PubMedSearcher()
        with self.assertRaises(NotImplementedError):
            searcher.download_pdf("12345678", "./downloads")
    
    def test_read_paper_message(self):
        searcher = PubMedSearcher()
        message = searcher.read_paper("12345678")
        self.assertIn("PubMed papers cannot be read directly", message)

    def test_search_returns_empty_on_html_error_page(self):
        """NCBI sometimes returns an HTML error page; search must not crash."""
        searcher = PubMedSearcher()
        html_response = Mock()
        # Non-XML body that ET.fromstring cannot parse.
        html_response.content = b"<html><body>Service Unavailable</body></html>"

        with patch("paper_search_mcp.academic_platforms.pubmed.requests.get", return_value=html_response) as mock_get:
            result = searcher.search("anything", max_results=5)

        self.assertEqual(result, [])
        # esearch call must carry a timeout.
        for _args, kwargs in mock_get.call_args_list:
            self.assertEqual(kwargs.get("timeout"), 30)

    def test_search_returns_empty_on_request_exception(self):
        """Network failures should yield an empty list, not propagate."""
        searcher = PubMedSearcher()
        with patch("paper_search_mcp.academic_platforms.pubmed.requests.get", side_effect=requests.ConnectionError("boom")):
            result = searcher.search("anything", max_results=5)
        self.assertEqual(result, [])

if __name__ == '__main__':
    unittest.main()