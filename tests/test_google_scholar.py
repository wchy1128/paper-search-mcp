import unittest
import os
import requests
from bs4 import BeautifulSoup
from paper_search_mcp.academic_platforms.google_scholar import GoogleScholarSearcher

# Minimal, offline HTML fixture mirroring real Google Scholar markup.
# The <b> tags wrap query terms (how Scholar renders matches); this is the
# structure that previously caused adjacent words to be concatenated
# (e.g. "on<b>graph</b>" -> "ongraph") when parsed with get_text(strip=True).
GS_FIXTURE_HTML = """
<div class="gs_ri">
  <h3 class="gs_rt"><a id="x" href="https://example.com/paper1">A comprehensive survey on <b>graph</b> neural networks</a></h3>
  <div class="gs_a">J Zhou, G Cui, S Hu - ACM Computing Surveys, 2020</div>
  <div class="gs_rs">In this survey, we provide a comprehensive overview of <b>graph</b> neural networks...</div>
</div>
"""

def check_scholar_accessible():
    """检查 Google Scholar 是否可访问"""
    try:
        response = requests.get("https://scholar.google.com", timeout=5)
        return response.status_code == 200
    except:
        return False

class TestGoogleScholarSearcher(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scholar_accessible = check_scholar_accessible()
        if not cls.scholar_accessible:
            print("\nWarning: Google Scholar is not accessible, some tests will be skipped")

    def setUp(self):
        self.searcher = GoogleScholarSearcher()

    def test_search(self):
        if not self.scholar_accessible:
            self.skipTest("Google Scholar is not accessible")
            
        papers = self.searcher.search("machine learning", max_results=5)
        print(f"\nFound {len(papers)} papers for query 'machine learning':")
        if len(papers) == 0:
            self.skipTest("Google Scholar returned 0 results (likely bot-detection/rate-limit)")

        for i, paper in enumerate(papers, 1):
            print(f"\n{i}. {paper.title}")
            print(f"   Authors: {', '.join(paper.authors)}")
            print(f"   Citations: {paper.citations}")
        self.assertTrue(len(papers) > 0)
        self.assertTrue(papers[0].title)

    def test_download_pdf_not_supported(self):
        with self.assertRaises(NotImplementedError):
            self.searcher.download_pdf("some_id", "./downloads")

    def test_read_paper_not_supported(self):
        message = self.searcher.read_paper("some_id")
        self.assertIn("Google Scholar doesn't support direct paper reading", message)

    def test_proxy_configuration(self):
        proxy_searcher = GoogleScholarSearcher(proxy_url="http://127.0.0.1:7890")
        self.assertEqual(proxy_searcher.session.proxies.get("http"), "http://127.0.0.1:7890")
        self.assertEqual(proxy_searcher.session.proxies.get("https"), "http://127.0.0.1:7890")

    def test_retry_configuration(self):
        retry_searcher = GoogleScholarSearcher(max_retries=5, retry_delay=3.0)
        self.assertEqual(retry_searcher.max_retries, 5)
        self.assertEqual(retry_searcher.retry_delay, 3.0)

    def test_parse_paper_preserves_spaces_around_bold_terms(self):
        """Words adjacent to <b> tags must not be concatenated.

        Scholar wraps query terms in <b>; get_text(strip=True) silently
        drops the space at the tag boundary, yielding 'ongraph' etc.
        """
        item = BeautifulSoup(GS_FIXTURE_HTML, 'html.parser')
        paper = self.searcher._parse_paper(item)
        self.assertIsNotNone(paper)
        self.assertEqual(paper.title, "A comprehensive survey on graph neural networks")
        self.assertIn("graph", paper.abstract)
        # abstract boundary too: '...of <b>graph</b> neural...' must keep spaces
        self.assertIn("of graph neural", paper.abstract)

    def test_parse_paper_extracts_authors_and_year(self):
        """Regression guard for the fixture parsing path."""
        item = BeautifulSoup(GS_FIXTURE_HTML, 'html.parser')
        paper = self.searcher._parse_paper(item)
        self.assertIsNotNone(paper)
        self.assertEqual(paper.authors, ["J Zhou", "G Cui", "S Hu"])
        self.assertEqual(paper.url, "https://example.com/paper1")
        self.assertEqual(paper.source, "google_scholar")

if __name__ == '__main__':
    unittest.main()