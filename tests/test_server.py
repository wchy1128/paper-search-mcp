# tests/test_server.py
import unittest
import asyncio
import os
import threading
from unittest.mock import patch
from paper_search_mcp import server

class TestPaperSearchServer(unittest.TestCase):
    def test_all_sources_include_new_platforms(self):
        self.assertIn("dblp", server.ALL_SOURCES)
        self.assertIn("openaire", server.ALL_SOURCES)
        self.assertIn("citeseerx", server.ALL_SOURCES)
        self.assertIn("doaj", server.ALL_SOURCES)
        self.assertIn("base", server.ALL_SOURCES)
        self.assertIn("zenodo", server.ALL_SOURCES)
        self.assertIn("hal", server.ALL_SOURCES)
        self.assertIn("ssrn", server.ALL_SOURCES)
        self.assertIn("unpaywall", server.ALL_SOURCES)

    def test_parse_sources_with_new_platforms(self):
        parsed = server._parse_sources("dblp,doaj,base,zenodo,hal,ssrn,unpaywall,invalid")
        self.assertEqual(parsed, ["dblp", "doaj", "base", "zenodo", "hal", "ssrn", "unpaywall"])

    def test_search_arxiv(self):
        """Test the search_arxiv tool returns 10 results."""
        result = asyncio.run(server.search_arxiv("machine learning", max_results=10))
        self.assertIsInstance(result, list, "Result should be a list")
        self.assertEqual(len(result), 10, "Should return exactly 10 results")
        for paper in result:
            self.assertIn('title', paper, "Each result should contain a title")
            self.assertIn('paper_id', paper, "Each result should contain a paper_id")

    def test_download_arxiv_from_search(self):
        """Test downloading 10 arXiv papers based on search results."""
        # 先搜索 10 个结果
        search_results = asyncio.run(server.search_arxiv("machine learning", max_results=10))
        self.assertEqual(len(search_results), 10, "Search should return 10 results")

        # 下载目录
        save_path = "./downloads"
        os.makedirs(save_path, exist_ok=True)  # 确保目录存在

        # 下载每个搜索结果的 PDF
        for paper in search_results:
            paper_id = paper['paper_id']
            result = asyncio.run(server.download_arxiv(paper_id, save_path))
            self.assertIsInstance(result, str, f"Result for {paper_id} should be a file path")
            self.assertTrue(result.endswith(".pdf"), f"Result for {paper_id} should be a PDF file path")
            self.assertTrue(os.path.exists(result), f"PDF file for {paper_id} should exist on disk")

    def test_download_tool_runs_off_the_event_loop_thread(self):
        """download_* tools must run the blocking searcher call in a worker
        thread (asyncio.to_thread), not on the event loop's main thread.
        Otherwise a single slow download stalls the whole MCP server.
        """
        captured = {}

        def fake_download(self, paper_id, save_path):
            captured["thread"] = threading.current_thread().name
            return f"{save_path}/fake_{paper_id}.pdf"

        with patch.object(server.BioRxivSearcher, "download_pdf", fake_download):
            asyncio.run(server.download_biorxiv("10.001/abc", "./downloads"))

        # The event loop runs on the main thread ("MainThread"). If the
        # download executed there, blocking IO would stall it.
        self.assertIn("thread", captured)
        self.assertNotEqual(captured["thread"], threading.main_thread().name)

    def test_read_tool_runs_off_the_event_loop_thread(self):
        """read_* tools must likewise run the blocking call off the loop thread."""
        captured = {}

        def fake_read(self, paper_id, save_path="./downloads"):
            captured["thread"] = threading.current_thread().name
            return "extracted text"

        with patch.object(server.SemanticSearcher, "read_paper", fake_read):
            asyncio.run(server.read_semantic_paper("some-paper-id", "./downloads"))

        self.assertIn("thread", captured)
        self.assertNotEqual(captured["thread"], threading.main_thread().name)

if __name__ == "__main__":
    unittest.main()