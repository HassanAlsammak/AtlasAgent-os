import io
import json
import unittest
from atlasagent.github_pr import DraftPR, create_draft_pr


class Response:
    def __enter__(self):
        return io.BytesIO(b'{"html_url":"https://github.com/test/repo/pull/1"}')

    def __exit__(self, *args):
        return False


class TestDraftPR(unittest.TestCase):
    def setUp(self):
        self.pr = DraftPR("test/repo", "feature/demo", "main", "Test feature", "Test body")

    def test_payload_is_always_draft(self):
        self.assertTrue(self.pr.payload()["draft"])

    def test_reject_invalid_repo(self):
        with self.assertRaises(ValueError):
            DraftPR("test/repo/extra", "head", "main", "x", "y").payload()

    def test_reject_same_branch(self):
        with self.assertRaises(ValueError):
            DraftPR("test/repo", "main", "main", "x", "y").payload()

    def test_requires_confirmation(self):
        with self.assertRaises(PermissionError):
            create_draft_pr(self.pr, token="fake", opener=lambda *a, **kw: self.fail("Network called"))

    def test_confirmed_creation(self):
        def opener(req, timeout):
            self.assertEqual(req.get_method(), "POST")
            self.assertTrue(json.loads(req.data)["draft"])
            self.assertIn("/pulls", req.full_url)
            return Response()
        self.assertEqual(create_draft_pr(self.pr, token="fake", confirm=True, opener=opener),
                         "https://github.com/test/repo/pull/1")
