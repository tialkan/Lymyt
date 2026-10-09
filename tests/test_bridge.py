import importlib.util
import json
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
import unittest
import urllib.error
import urllib.request
from unittest.mock import patch
import io

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("lymyt", ROOT / "bridge" / "lymyt.py")
lymyt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lymyt)


class QuotaSemantics(unittest.TestCase):
    def test_cached_statusline_does_not_renew_observation_and_empty_does_not_erase(self):
        with tempfile.TemporaryDirectory() as directory:
            sample = {"session_id": "not-saved", "cost": {"total_api_duration_ms": 10},
                      "rate_limits": {"five_hour": {"used_percentage": 40, "resets_at": 9000}}}
            def capture(payload, now):
                with patch.object(sys, "argv", ["lymyt", "--data-dir", directory, "capture-claude"]), \
                     patch.object(sys, "stdin", io.StringIO(json.dumps(payload))), \
                     patch.object(sys, "stdout", io.StringIO()), patch.object(lymyt.time, "time", return_value=now):
                    self.assertEqual(lymyt.main(), 0)
                return json.loads((Path(directory)/"claude.json").read_text())
            first = capture(sample, 1000)
            cached = capture(sample, 1600)
            self.assertEqual(cached["observed_at"], 1000)
            self.assertEqual(capture({}, 1700), first)
            self.assertNotIn("not-saved", json.dumps(first))
            sample["cost"]["total_api_duration_ms"] = 20
            self.assertEqual(capture(sample, 1800)["observed_at"], 1800)

    def test_multi_bucket_does_not_use_another_product(self):
        result = lymyt.normalize_codex({"rateLimitsByLimitId": {"other": {"primary": {
            "usedPercent": 40, "resetsAt": 1000}}}, "rateLimits": {"primary": {
                "usedPercent": 20, "resetsAt": 1000}}}, 500)
        self.assertEqual(result["windows"], [])

    def test_missing_percent_is_unknown_not_zero(self):
        result = lymyt.normalize_claude({"rate_limits": {"five_hour": {"resets_at": 1000}}}, 500)
        display = lymyt.presentation(result, 600, 180)
        self.assertIsNone(display["windows"][0]["remaining_percent"])
        self.assertEqual(display["windows"][0]["remaining_seconds"], 400)

    def test_zero_percent_is_present(self):
        result = lymyt.normalize_claude({"rate_limits": {"five_hour": {
            "used_percentage": 0, "resets_at": 1000}}}, 500)
        self.assertEqual(lymyt.presentation(result, 600, 180)["windows"][0]["remaining_percent"], 100)

    def test_expired_countdown_does_not_replenish_quota(self):
        result = lymyt.normalize_codex({"rateLimits": {"limitId": "codex", "primary": {
            "usedPercent": 100, "resetsAt": 1000}}}, 900)
        display = lymyt.presentation(result, 1100, 180)
        self.assertEqual(display["status"], "stale")
        self.assertEqual(display["windows"][0]["remaining_percent"], 0)
        self.assertTrue(display["windows"][0]["reset_needs_confirmation"])

    def test_non_finite_and_boolean_values_rejected(self):
        for invalid in (True, False, float("nan"), float("inf"), "90", -1, 101):
            self.assertIsNone(lymyt.number(invalid, high=100))

    def test_absent_claude_data_is_unknown(self):
        result = lymyt.normalize_claude({}, 500)
        self.assertEqual(lymyt.presentation(result, 600, 180)["status"], "unknown")


class HTTPContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory()
        cls.data = Path(cls.directory.name)
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
        cls.url = "http://127.0.0.1:{}".format(port)
        cls.process = subprocess.Popen([sys.executable, str(ROOT / "bridge" / "lymyt.py"),
            "--data-dir", str(cls.data), "serve", "--relay", "--port", str(port)],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(100):
            try:
                with urllib.request.urlopen(cls.url, timeout=.2):
                    break
            except OSError:
                if cls.process.poll() is not None:
                    raise RuntimeError("Test server failed to start")
                time.sleep(.02)
        else:
            cls.process.terminate()
            raise RuntimeError("Test server did not start")
        cls.device_token = (cls.data / "device-token").read_text().strip()
        cls.sync_token = (cls.data / "sync-token").read_text().strip()

    @classmethod
    def tearDownClass(cls):
        cls.process.terminate()
        cls.process.wait(timeout=5)
        cls.directory.cleanup()

    def request(self, path, token=None, payload=None, origin=None):
        headers = {}
        if token:
            headers["Authorization"] = "Bearer " + token
        if origin:
            headers["Origin"] = origin
        data = None if payload is None else json.dumps(payload).encode()
        request = urllib.request.Request(self.url + path, data=data, headers=headers)
        return urllib.request.urlopen(request, timeout=3)

    def test_public_preview_contains_no_quota_or_token(self):
        with self.request("/") as response:
            page = response.read().decode()
            self.assertIn("Lymyt Studio", page)
            self.assertNotIn(self.device_token, page)
            self.assertIn("default-src 'self'", response.headers["Content-Security-Policy"])

    def test_device_endpoint_requires_token(self):
        with self.assertRaises(urllib.error.HTTPError) as context:
            self.request("/v1/status")
        self.assertEqual(context.exception.code, 401)

    def test_foreign_origin_is_rejected(self):
        with self.assertRaises(urllib.error.HTTPError) as context:
            self.request("/v1/status", self.device_token, origin="https://foreign.invalid")
        self.assertEqual(context.exception.code, 401)

    def test_device_token_cannot_write_quotas(self):
        with self.assertRaises(urllib.error.HTTPError) as context:
            self.request("/v1/ingest", self.device_token, {})
        self.assertEqual(context.exception.code, 401)

    def test_cloud_ingest_keeps_source_timestamp_and_strips_extras(self):
        now = int(time.time())
        payload = {"schema_version": 1, "providers": {
            "openai": {"product": "codex", "observed_at": now - 600, "secret": "discard", "windows": [
                {"id": "primary", "used_percent": 100, "resets_at": now-60, "window_minutes": 300}]},
            "claude": {"product": "claude-code", "observed_at": None, "windows": []}}}
        with self.request("/v1/ingest", self.sync_token, payload) as response:
            self.assertEqual(response.status, 204)
        with self.request("/v1/status", self.device_token) as response:
            raw = response.read().decode()
            result = json.loads(raw)
        self.assertNotIn("discard", raw)
        codex = result["providers"]["openai"]
        self.assertEqual(codex["observed_at"], now-600)
        self.assertEqual(codex["status"], "stale")
        self.assertTrue(codex["windows"][0]["reset_needs_confirmation"])

    def test_device_telemetry_is_whitelisted(self):
        payload = {"motion": True, "view": "week", "password": "discard", "acceleration": {"x": 1, "y": 2, "z": 9.8}}
        with self.request("/v1/device", self.device_token, payload) as response:
            self.assertEqual(response.status, 204)
        with self.request("/v1/status", self.device_token) as response:
            result = json.loads(response.read())
        self.assertTrue(result["device"]["online"])
        self.assertTrue(result["device"]["motion"])
        self.assertNotIn("password", result["device"])


if __name__ == "__main__":
    unittest.main()
