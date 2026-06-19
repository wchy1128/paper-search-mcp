# tests/test_openalex.py
import unittest
from unittest.mock import patch, Mock

from paper_search_mcp.academic_platforms.openalex import OpenAlexSearcher


def _ok_response(payload):
    resp = Mock()
    resp.status_code = 200
    resp.json.return_value = payload
    return resp


class TestOpenAlexSearcher(unittest.TestCase):
    def setUp(self):
        self.searcher = OpenAlexSearcher()

    def test_search_without_language_sends_no_filter(self):
        """By default no language filter is sent to OpenAlex."""
        resp = _ok_response({"results": []})
        with patch.object(self.searcher.session, "get", return_value=resp) as mock_get:
            self.searcher.search("transformer", max_results=5)

        mock_get.assert_called_once()
        _args, kwargs = mock_get.call_args
        params = kwargs.get("params", {})
        self.assertNotIn("filter", params)
        self.assertEqual(params.get("search"), "transformer")

    def test_search_with_language_sends_language_filter(self):
        """A language code maps to OpenAlex top-level filter=language:<code>.

        OpenAlex exposes language as a top-level Work field, so the filter is
        ``language:zh`` (not a nested primary_location.source path, which the
        API rejects with HTTP 400).
        """
        resp = _ok_response({"results": []})
        with patch.object(self.searcher.session, "get", return_value=resp) as mock_get:
            self.searcher.search("深度学习", max_results=5, language="zh")

        mock_get.assert_called_once()
        _args, kwargs = mock_get.call_args
        params = kwargs.get("params", {})
        self.assertEqual(params.get("filter"), "language:zh")
        # search and filter coexist as independent query params.
        self.assertEqual(params.get("search"), "深度学习")

    def test_search_returns_empty_on_non_200(self):
        resp = Mock()
        resp.status_code = 500
        with patch.object(self.searcher.session, "get", return_value=resp):
            result = self.searcher.search("anything", max_results=5)
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
