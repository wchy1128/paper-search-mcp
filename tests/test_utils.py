# tests/test_utils.py
import re
import unittest

from paper_search_mcp.utils import extract_doi, stable_id, safe_filename


class TestExtractDoi(unittest.TestCase):
    def test_extracts_doi_from_url(self):
        self.assertEqual(
            extract_doi("see https://doi.org/10.1000/test-doi for details"),
            "10.1000/test-doi",
        )

    def test_empty_text_returns_empty(self):
        self.assertEqual(extract_doi(""), "")
        self.assertEqual(extract_doi(None), "")


class TestStableId(unittest.TestCase):
    def test_format_is_prefix_plus_eight_hex(self):
        result = stable_id("citeseerx", "A Test Paper")
        self.assertRegex(result, r"^citeseerx_[0-9a-f]{8}$")

    def test_deterministic_across_calls(self):
        # Same input must always yield the same id (the bug being fixed: the old
        # hash()-based id changed every process start due to PYTHONHASHSEED).
        self.assertEqual(
            stable_id("dblp", "machine learning"),
            stable_id("dblp", "machine learning"),
        )

    def test_different_inputs_diverge(self):
        self.assertNotEqual(
            stable_id("openaire", "paper one"),
            stable_id("openaire", "paper two"),
        )

    def test_empty_text_still_stable(self):
        # Should not raise; empty text just hashes to the md5 of "".
        self.assertRegex(stable_id("gs", ""), r"^gs_[0-9a-f]{8}$")

    def test_custom_length(self):
        result = stable_id("ssrn", "https://example.com/x", length=12)
        self.assertRegex(result, r"^ssrn_[0-9a-f]{12}$")

    def test_known_value(self):
        # md5("foo") = acbd18db4ccabf85..., so first 8 hex chars are acbd18db.
        self.assertEqual(stable_id("citeseerx", "foo"), "citeseerx_acbd18db")

    def test_custom_separator(self):
        # Sources whose historical id format used a colon (e.g. SSRN) can keep
        # it, so primary and fallback ids share the same prefix.
        self.assertEqual(
            stable_id("ssrn", "https://example.com/x", separator=":"),
            "ssrn:" + stable_id("ssrn", "https://example.com/x").split("_", 1)[1],
        )
        self.assertTrue(stable_id("ssrn", "u", separator=":").startswith("ssrn:"))


class TestSafeFilename(unittest.TestCase):
    def test_replaces_slash(self):
        # Matches the historical behaviour relied on by test_semantic.py.
        self.assertEqual(safe_filename("paper/123"), "paper_123")

    def test_strips_windows_illegal_colon(self):
        result = safe_filename("DOI:10.18653/v1/N18-3011")
        self.assertNotIn(":", result)
        self.assertNotIn("/", result)
        self.assertEqual(result, "DOI_10.18653_v1_N18-3011")

    def test_strips_other_windows_illegal_chars(self):
        for bad in ('?', '*', '\\', '<', '>', '|', '"'):
            result = safe_filename(f"foo{bad}bar")
            self.assertNotIn(bad, result, f"char {bad!r} should be stripped")

    def test_empty_input_returns_default(self):
        self.assertEqual(safe_filename("///"), "paper")
        self.assertEqual(safe_filename(""), "paper")

    def test_custom_default(self):
        self.assertEqual(safe_filename("", default="untitled"), "untitled")

    def test_truncates_long_input(self):
        result = safe_filename("a" * 500)
        self.assertLessEqual(len(result), 120)


if __name__ == "__main__":
    unittest.main()
