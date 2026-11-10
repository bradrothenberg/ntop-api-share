"""Small offline checks for failure handling. Run with uv run python this_file.py."""
import copy
import unittest
from unittest.mock import Mock
from unlinked import Client, check_result


class Checks(unittest.TestCase):
    def setUp(self):
        self.result = {"run": {"id": "test", "status": "completed", "request": {
            "options": {"start": 0, "stop": 1, "output_signals": ["state"]}}},
            "trace": {"time": [0, 0.5, 1], "signals": {"state": [1, 0.5, 0.25]}}}

    def test_rejects_bad_traces(self):
        invalid = []
        for values in ([1, float("nan"), 0], [1, 0], [1, "0.5", 0]):
            result = copy.deepcopy(self.result)
            result["trace"]["signals"]["state"] = values
            invalid.append(result)
        result = copy.deepcopy(self.result)
        result["trace"]["time"] = [0, 0.5, 0.5]
        invalid.append(result)
        result = copy.deepcopy(self.result)
        result["run"]["status"] = "failed"
        invalid.append(result)
        result = copy.deepcopy(self.result)
        result["trace"]["signals"] = {"wrong_id": [1, 0.5, 0.25]}
        invalid.append(result)
        result = copy.deepcopy(self.result)
        result["trace"]["time"] = [0, 0.5, 0.9]
        invalid.append(result)
        for item in invalid:
            with self.subTest(item=item), self.assertRaises(ValueError):
                check_result(item)
        self.assertEqual(check_result(self.result)["samples"], 3)

    def test_loopback_scope(self):
        # Synthetic user-info case, assembled without a credential-shaped literal.
        userinfo_url = "http://" + ":".join(("test-user", "test-password")) + "@localhost"
        for url in ("https://example.com", "http://localhost.evil", userinfo_url, "http://localhost/path"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                Client(url)
        Client("http://localhost:3000")
        Client("http://127.0.0.1:3000")

    def test_uncertain_mutation_is_not_retried(self):
        client = Client()
        client.opener = Mock()
        client.opener.open.side_effect = TimeoutError("test timeout")
        with self.assertRaisesRegex(RuntimeError, "Inspect server state"):
            client.request("POST", "/api/files/test/simulations", {"version": 1})
        self.assertEqual(client.opener.open.call_count, 1)


if __name__ == "__main__":
    unittest.main()
