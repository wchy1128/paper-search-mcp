# tests/test_arxiv.py
import unittest
from unittest.mock import patch, Mock

import requests

from paper_search_mcp.academic_platforms.arxiv import ArxivSearcher

class TestArxivSearcher(unittest.TestCase):
    def test_search(self):
        searcher = ArxivSearcher()
        papers = searcher.search("machine learning", max_results=10)
        print(f"Found {len(papers)} papers for query 'machine learning':")
        for i, paper in enumerate(papers, 1):
            print(f"{i}. {paper.title} (ID: {paper.paper_id})")
        if not papers:
            self.skipTest("arXiv API is unavailable or rate-limited")
        self.assertEqual(len(papers), 10)
        self.assertTrue(papers[0].title)

    def test_download_pdf_passes_timeout(self):
        """download_pdf must pass a timeout so a hung host can't stall forever."""
        searcher = ArxivSearcher()
        fake_response = Mock()
        fake_response.content = b"%PDF-1.4 bytes"
        fake_response.raise_for_status.return_value = None

        with patch("paper_search_mcp.academic_platforms.arxiv.requests.get", return_value=fake_response) as mock_get:
            import tempfile
            with tempfile.TemporaryDirectory() as tmp:
                searcher.download_pdf("2106.12345", tmp)

        mock_get.assert_called_once()
        _args, kwargs = mock_get.call_args
        self.assertEqual(kwargs.get("timeout"), 30)

    def test_download_pdf_raises_on_http_error(self):
        """A non-2xx response should surface, not silently write an error body."""
        searcher = ArxivSearcher()
        fake_response = Mock()
        fake_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")

        with patch("paper_search_mcp.academic_platforms.arxiv.requests.get", return_value=fake_response):
            import tempfile
            with tempfile.TemporaryDirectory() as tmp:
                with self.assertRaises(requests.HTTPError):
                    searcher.download_pdf("0000.00000", tmp)

if __name__ == '__main__':
    unittest.main()