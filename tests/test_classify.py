"""Offline check of classify.py with the Clef API faked. Run from the repo root: python -m unittest"""
import io
import json
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest import mock

import classify


def fake_response(choice, conf):
    probs = {k: (0.8 if k == choice else 0.1) for k in ("acceptable", "toxic", "spam")}
    body = {"success": True, "result": {"answers": {"label": {"choice": choice, "probabilities": probs, "confidence": conf}}}}
    return io.BytesIO(json.dumps(body).encode())


class ClassifyTest(unittest.TestCase):
    def test_retries_429_then_succeeds(self):
        err = urllib.error.HTTPError("u", 429, "Too Many", {}, io.BytesIO(b""))
        with mock.patch("urllib.request.urlopen", side_effect=[err, fake_response("spam", 0.9)]), mock.patch("time.sleep"):
            a = classify.ask_clef({"author": "x", "thread": "t", "comment": "buy now"}, "acc", "tok", "clef")
        self.assertEqual(a["choice"], "spam")

    def test_cache_and_html(self):
        comments = [
            {"id": 1, "author": "A", "thread": "Doubts", "posted_at": "now", "comment": "</script><script>alert(1)</script>"},
            {"id": 2, "author": "B", "thread": "General", "posted_at": "now", "comment": "WhatsApp 90000"},
        ]
        with tempfile.TemporaryDirectory() as d:
            cache = Path(d) / "c.json"
            with mock.patch.object(classify, "load_creds", return_value=("a", "t")), \
                 mock.patch("urllib.request.urlopen", side_effect=[fake_response("acceptable", 0.2), fake_response("spam", 0.9)]):
                answers = classify.classify_all(comments, cache, "clef", fresh=False)
            # second run must be served from the cache, with no API call
            with mock.patch("urllib.request.urlopen", side_effect=AssertionError("called API")):
                self.assertEqual(classify.classify_all(comments, cache, "clef", fresh=False), answers)

        page = classify.render_html({"forum": "F"}, comments, answers, "clef")
        self.assertEqual(page.count("</script>"), 2)  # the comment can't break out of the data block
        blob = page.split('id="data">')[1].split("</script>")[0]
        data = json.loads(blob)
        self.assertEqual(data["comments"][0]["comment"], comments[0]["comment"])
        self.assertEqual([c["choice"] for c in data["comments"]], ["acceptable", "spam"])


if __name__ == "__main__":
    unittest.main()
