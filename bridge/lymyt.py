#!/usr/bin/env python3
"""Local, read-only Codex/Claude Code quota bridge; Python standard library only."""
import argparse
import hmac
import json
import math
import mimetypes
import os
from pathlib import Path
import queue
import secrets
import shutil
import subprocess
import sys
import threading
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = Path(__file__).resolve().parent.parent


class SerialLink:
    """USB CDC on macOS/Linux; no Wi-Fi secret or third-party serial library."""
    def __init__(self, port):
        import fcntl
        import termios
        import tty
        if not port.startswith('/dev/'):
            raise ValueError('USB port must be a /dev/ serial device')
        self.fd = os.open(port, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
        self.original = None
        self.buffer = bytearray()
        self.dropping = False
        try:
            fcntl.flock(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.original = termios.tcgetattr(self.fd)
            tty.setraw(self.fd)
            attrs = termios.tcgetattr(self.fd)
            attrs[4] = attrs[5] = termios.B115200
            attrs[2] |= termios.CLOCAL | termios.CREAD
            termios.tcsetattr(self.fd, termios.TCSANOW, attrs)
            termios.tcflush(self.fd, termios.TCIOFLUSH)
        except Exception as error:
            self.close()
            raise RuntimeError('USB configuration failed: ' + str(error)) from error

    def close(self):
        import termios
        if self.fd is not None:
            try:
                if self.original is not None:
                    termios.tcsetattr(self.fd, termios.TCSANOW, self.original)
            except (OSError, termios.error):
                pass
            os.close(self.fd)
            self.fd = None

    def send(self, snapshot):
        import select
        payload = json.dumps(snapshot, allow_nan=False, separators=(',', ':')).encode() + b'\n'
        if len(payload) > 8192:
            raise ValueError('USB snapshot too large')
        pending = memoryview(payload)
        deadline = time.monotonic() + 3
        while pending:
            if time.monotonic() >= deadline:
                raise TimeoutError('USB write timed out')
            if select.select([], [self.fd], [], 0.2)[1]:
                try:
                    pending = pending[os.write(self.fd, pending):]
                except BlockingIOError:
                    pass

    def lines(self, timeout=0.5):
        import select
        if not select.select([self.fd], [], [], timeout)[0]:
            return []
        chunk = os.read(self.fd, 4096)
        if not chunk:
            raise OSError('USB device disconnected')
        lines = []
        for ch in chunk:
            if ch == 10:
                if not self.dropping and self.buffer:
                    lines.append(self.buffer.decode('utf-8', errors='replace').rstrip('\r'))
                self.buffer.clear()
                self.dropping = False
            elif not self.dropping:
                if len(self.buffer) >= 8192:
                    self.buffer.clear()
                    self.dropping = True
                else:
                    self.buffer.append(ch)
        return lines


def usb_snapshots(bridge, link):
    started = time.monotonic()
    last_send = 0
    expected_epoch = None
    last_ack = None
    try:
        while not bridge.stop.is_set():
            now = time.monotonic()
            if not last_send or now - last_send >= 15:
                snapshot = bridge.snapshot()
                # Let the first account read complete before the panel's first refresh.
                awaiting_codex = (not bridge.args.no_codex and not snapshot['providers']['openai']['windows']
                                  and now - started < 10)
                if not awaiting_codex:
                    link.send(snapshot)
                    expected_epoch = snapshot['generated_at']
                    last_send = now
            for line in link.lines():
                try:
                    message = json.loads(line)
                except ValueError:
                    print('USB panel: ' + line[:240], flush=True)
                    continue
                if not isinstance(message, dict):
                    continue
                if message.get('lymyt') == 'ready':
                    print('Lymyt USB firmware ready.', flush=True)
                if (expected_epoch is not None and message.get('lymyt') == 'ack'
                        and message.get('generated_at') == expected_epoch):
                    with bridge.lock:
                        bridge.device = {'last_seen': int(time.time()), 'motion': None,
                                         'acceleration': None, 'transport': 'usb',
                                         'view': 'week' if message.get('view') == 'week' else 'short'}
                    if last_ack != expected_epoch:
                        print('USB quota frame acknowledged: ' + str(expected_epoch), flush=True)
                        last_ack = expected_epoch
    except (OSError, ValueError, TimeoutError) as error:
        print('Lymyt USB stopped: ' + str(error), file=sys.stderr, flush=True)
    finally:
        link.close()


def maintain_usb(bridge, port, link):
    """Reconnect only the explicitly selected device path after unplug/reboot."""
    while not bridge.stop.is_set():
        if link is None:
            try:
                link = SerialLink(port)
                print('Lymyt USB reconnected: ' + port, flush=True)
            except (OSError, ValueError, RuntimeError):
                bridge.stop.wait(3)
                continue
        usb_snapshots(bridge, link)
        link = None
        bridge.stop.wait(3)
    if link is not None:
        link.close()


def number(value, low=0, high=None):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    if not math.isfinite(value) or value < low or (high is not None and value > high):
        return None
    return value


def window(key, data, percent_key, reset_key, duration=None):
    if not isinstance(data, dict):
        return None
    used = number(data.get(percent_key), high=100)
    reset = number(data.get(reset_key), low=1)
    if used is None and reset is None:
        return None
    return {"id": key, "used_percent": used,
            "resets_at": int(reset) if reset is not None else None,
            "window_minutes": duration}


def normalize_codex(result, now):
    buckets = result.get("rateLimitsByLimitId")
    if isinstance(buckets, dict):
        # Never silently use another product's bucket when Codex is absent.
        bucket = buckets.get("codex")
    else:
        bucket = result.get("rateLimits")
        if isinstance(bucket, dict) and bucket.get("limitId") not in (None, "codex"):
            bucket = None
    windows = []
    if isinstance(bucket, dict):
        for key in ("primary", "secondary"):
            data = bucket.get(key)
            duration = number(data.get("windowDurationMins"), low=1) if isinstance(data, dict) else None
            item = window(key, data, "usedPercent", "resetsAt", duration)
            if item:
                windows.append(item)
    return {"product": "codex", "observed_at": now if windows else None,
            "windows": windows}


def normalize_claude(data, now):
    rates = data.get("rate_limits") or {}
    windows = []
    if isinstance(rates, dict):
        for key, duration in (("five_hour", 300), ("seven_day", 10080)):
            item = window(key, rates.get(key), "used_percentage", "resets_at", duration)
            if item:
                windows.append(item)
    return {"product": "claude-code", "observed_at": now if windows else None,
            "windows": windows}


def presentation(provider, now, stale_after):
    result = dict(provider)
    age = now - result["observed_at"] if result.get("observed_at") is not None else None
    result["status"] = "unknown" if age is None else ("stale" if age > stale_after else "ok")
    result["age_seconds"] = max(0, age) if age is not None else None
    result["windows"] = []
    for source in provider.get("windows", []):
        item = dict(source)
        reset = source.get("resets_at")
        remaining = max(0, reset - now) if reset is not None else None
        item["remaining_seconds"] = remaining
        item["remaining_percent"] = (100 - source["used_percent"]
                                     if source.get("used_percent") is not None else None)
        # A countdown reaching zero is not proof that the service renewed quota.
        item["reset_needs_confirmation"] = reset is not None and now >= reset
        result["windows"].append(item)
    return result


def atomic_json(path, data):
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    temporary = path.with_name(path.name + "." + secrets.token_hex(6) + ".tmp")
    try:
        with temporary.open("x") as stream:
            os.chmod(temporary, 0o600)
            json.dump(data, stream, allow_nan=False)
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


class CodexRPC:
    def __init__(self, binary):
        self.messages = queue.Queue()
        self.sequence = 0
        self.process = subprocess.Popen([binary, "app-server"], stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                        text=True, bufsize=1)
        threading.Thread(target=self.read, daemon=True).start()
        try:
            self.request("initialize", {"clientInfo": {
                "name": "lymyt", "title": "Lymyt quota display", "version": "0.1.0"}})
            self.send({"method": "initialized", "params": {}})
        except Exception:
            self.close()
            raise

    def read(self):
        for line in self.process.stdout:
            try:
                message = json.loads(line)
                if isinstance(message, dict):
                    self.messages.put(message)
            except json.JSONDecodeError:
                continue
        self.messages.put(None)

    def send(self, message):
        self.process.stdin.write(json.dumps(message) + "\n")
        self.process.stdin.flush()

    def request(self, method, params=None):
        self.sequence += 1
        request_id = self.sequence
        self.send({"id": request_id, "method": method, "params": params or {}})
        deadline = time.monotonic() + 20
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError("Codex did not respond")
            message = self.messages.get(timeout=remaining)
            if message is None:
                raise RuntimeError("Codex app-server exited")
            if message.get("id") == request_id and "method" not in message:
                if "error" in message:
                    # Do not expose raw upstream responses in the device endpoint.
                    raise RuntimeError("Codex rejected the quota request")
                return message.get("result") or {}
            if "id" in message and "method" in message:
                self.send({"id": message["id"], "error": {
                    "code": -32601, "message": "Read-only Lymyt client"}})

    def close(self):
        if self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=3)
        self.process.stdin.close()
        self.process.stdout.close()


class Bridge:
    def __init__(self, args):
        self.args = args
        self.lock = threading.Lock()
        self.stop = threading.Event()
        self.codex = {"product": "codex", "observed_at": None, "windows": []}
        self.relay_providers = None
        self.device = None
        if args.relay:
            try:
                self.relay_providers = clean_providers(json.loads((args.data_dir / "cloud-quotas.json").read_text()))
            except (OSError, ValueError, TypeError):
                pass

    def poll_codex(self):
        rpc = None
        try:
            while not self.stop.is_set():
                try:
                    if rpc is None:
                        rpc = CodexRPC(self.args.codex)
                    provider = normalize_codex(rpc.request("account/rateLimits/read"), int(time.time()))
                    with self.lock:
                        self.codex = provider
                except Exception:
                    if rpc is not None:
                        rpc.close()
                        rpc = None
                    # Keep the last successful observation; freshness expires naturally.
                    print("Codex limits unavailable; check CLI login/version/network.", file=sys.stderr)
                self.stop.wait(self.args.poll_seconds)
        finally:
            if rpc is not None:
                rpc.close()

    def snapshot(self):
        now = int(time.time())
        with self.lock:
            codex = dict(self.codex)
            relay = self.relay_providers
            device = dict(self.device) if self.device else None
        claude = {"product": "claude-code", "observed_at": None, "windows": []}
        try:
            candidate = json.loads((self.args.data_dir / "claude.json").read_text())
            if (candidate.get("product") == "claude-code"
                    and isinstance(candidate.get("windows"), list)):
                claude = candidate
        except (OSError, ValueError, AttributeError):
            pass
        if relay is not None:
            codex, claude = relay["openai"], relay["claude"]
        if device:
            device["online"] = now - device["last_seen"] <= 60
        return {"schema_version": 1, "generated_at": now, "stale_after": self.args.stale_after,
                "device": device, "providers": {
            "openai": presentation(codex, now, self.args.stale_after),
            "claude": presentation(claude, now, self.args.stale_after)}}


def clean_providers(payload):
    if not isinstance(payload, dict):
        raise ValueError("Expected an object")
    sources = payload.get("providers")
    if payload.get("schema_version") != 1 or not isinstance(sources, dict):
        raise ValueError("Invalid snapshot")
    result = {}
    now = int(time.time())
    for key, product, accepted in (("openai", "codex", ("primary", "secondary")),
                                    ("claude", "claude-code", ("five_hour", "seven_day"))):
        source = sources.get(key)
        if not isinstance(source, dict) or source.get("product") != product:
            raise ValueError("Invalid provider")
        observed = number(source.get("observed_at"), high=now + 120)
        windows = source.get("windows")
        if not isinstance(windows, list) or len(windows) > 2:
            raise ValueError("Invalid windows")
        parsed = []
        for candidate in windows:
            if not isinstance(candidate, dict) or candidate.get("id") not in accepted:
                raise ValueError("Invalid window")
            item = window(candidate["id"], candidate, "used_percent", "resets_at",
                          number(candidate.get("window_minutes"), low=1))
            if item:
                parsed.append(item)
        result[key] = {"product": product, "observed_at": int(observed) if observed is not None else None,
                       "windows": parsed}
    return result


def read_token(data_dir, name="device-token"):
    data_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    token_file = data_dir / name
    if not token_file.exists():
        with token_file.open("x") as stream:
            os.chmod(token_file, 0o600)
            stream.write(secrets.token_urlsafe(32))
    token = token_file.read_text().strip()
    if len(token) < 24:
        raise ValueError("Device token is too short")
    return token


def serve(args):
    token = read_token(args.data_dir)
    sync_token = read_token(args.data_dir, "sync-token") if args.relay else None
    bridge = Bridge(args)

    class Handler(BaseHTTPRequestHandler):
        def authorized(self, expected):
            return bool(expected) and not self.headers.get("Origin") and hmac.compare_digest(
                self.headers.get("Authorization", "").encode(), ("Bearer " + expected).encode())

        def do_GET(self):
            assets = {"/": "index.html", "/app.js": "app.js", "/style.css": "style.css"}
            if self.path in assets:
                path = ROOT / "web" / assets[self.path]
                payload = path.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", mimetypes.guess_type(str(path))[0] or "application/octet-stream")
                self.send_header("Content-Length", str(len(payload)))
                self.send_header("X-Content-Type-Options", "nosniff")
                self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'self'; script-src 'self'; connect-src 'self'; object-src 'none'; frame-ancestors 'none'")
                self.end_headers()
                self.wfile.write(payload)
                return
            if not self.authorized(token):
                self.send_error(401)
                return
            if self.path != "/v1/status":
                self.send_error(404)
                return
            payload = json.dumps(bridge.snapshot(), allow_nan=False).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def do_POST(self):
            if self.path not in ("/v1/device", "/v1/ingest") or (self.path == "/v1/ingest" and not args.relay):
                self.send_error(404)
                return
            if not self.authorized(sync_token if self.path == "/v1/ingest" else token):
                self.send_error(401)
                return
            try:
                size = int(self.headers.get("Content-Length", "0"))
                if size <= 0 or size > 8192:
                    self.send_error(413)
                    return
                payload = json.loads(self.rfile.read(size))
                if self.path == "/v1/ingest":
                    providers = clean_providers(payload)
                    atomic_json(args.data_dir / "cloud-quotas.json", {"schema_version": 1, "providers": providers})
                    with bridge.lock:
                        bridge.relay_providers = providers
                else:
                    if not isinstance(payload, dict):
                        raise ValueError("Invalid telemetry")
                    acceleration = payload.get("acceleration")
                    parsed_acceleration = None
                    if isinstance(acceleration, dict):
                        parsed_acceleration = {axis: number(acceleration.get(axis), low=-160, high=160)
                                               for axis in ("x", "y", "z")}
                    telemetry = {"last_seen": int(time.time()),
                                 "motion": payload.get("motion") if isinstance(payload.get("motion"), bool) else None,
                                 "acceleration": parsed_acceleration,
                                 "view": "week" if payload.get("view") == "week" else "short"}
                    with bridge.lock:
                        bridge.device = telemetry
            except (ValueError, TypeError, OSError):
                self.send_error(400)
                return
            self.send_response(204)
            self.send_header("Content-Length", "0")
            self.end_headers()

        def log_message(self, *unused):
            pass

    server = ThreadingHTTPServer((args.host, args.port), Handler)
    serial_link = None
    try:
        if args.serial_port:
            serial_link = SerialLink(args.serial_port)
    except (OSError, ValueError, ImportError, RuntimeError) as error:
        server.server_close()
        raise RuntimeError('Cannot open USB serial port: ' + str(error)) from error
    worker = threading.Thread(target=bridge.poll_codex, daemon=True)
    if not args.no_codex and not args.relay:
        worker.start()
    serial_worker = None
    if serial_link:
        serial_worker = threading.Thread(target=maintain_usb, args=(bridge, args.serial_port, serial_link), daemon=True)
        serial_worker.start()
        print('Lymyt USB: ' + args.serial_port, flush=True)
    uploader = None
    if args.sync_url:
        uploader = threading.Thread(target=push_snapshots, args=(bridge,), daemon=True)
        uploader.start()
    print("Lymyt bridge: http://{}:{}/v1/status".format(args.host, args.port), flush=True)
    print("Device token file: {}".format(args.data_dir / "device-token"), flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        bridge.stop.set()
        server.server_close()
        if serial_worker:
            serial_worker.join(timeout=5)
        if worker.is_alive():
            worker.join(timeout=25)
        if uploader:
            uploader.join(timeout=12)


def push_snapshots(bridge):
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *unused):
            return None
    opener = urllib.request.build_opener(NoRedirect)
    while not bridge.stop.is_set():
        try:
            token = bridge.args.sync_token_file.read_text().strip()
            request = urllib.request.Request(bridge.args.sync_url,
                data=json.dumps(bridge.snapshot(), allow_nan=False).encode(),
                headers={"Authorization": "Bearer " + token, "Content-Type": "application/json"},
                method="POST")
            with opener.open(request, timeout=10) as response:
                if response.status != 204:
                    raise ValueError("Unexpected relay response")
        except Exception:
            print("Cloud sync unavailable; local quota display continues.", file=sys.stderr)
        bridge.stop.wait(30)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=ROOT / ".lymyt")
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser("serve", help="Serve normalized quota data")
    run.add_argument("--host", default="127.0.0.1")
    run.add_argument("--port", type=int, default=8787)
    run.add_argument("--codex", default=shutil.which("codex") or "codex")
    run.add_argument("--poll-seconds", type=int, default=60)
    run.add_argument("--stale-after", type=int, default=180)
    run.add_argument("--no-codex", action="store_true", help="Preview the UI without starting Codex")
    run.add_argument("--relay", action="store_true", help="VPS mode: receive sanitized quotas, no account login")
    run.add_argument("--sync-url", help="HTTPS VPS /v1/ingest endpoint")
    run.add_argument("--sync-token-file", type=Path, help="File containing the VPS sync token")
    run.add_argument("--serial-port", help="Send quotas to the Nano over USB CDC (macOS/Linux)")
    commands.add_parser("capture-claude", help="Read status line JSON from stdin")
    args = parser.parse_args()
    if args.command == "serve":
        if args.poll_seconds < 15 or args.stale_after < args.poll_seconds:
            parser.error("poll-seconds must be >=15 and stale-after >= poll-seconds")
        if args.sync_url and (not args.sync_url.startswith("https://") or not args.sync_token_file or args.relay):
            parser.error("sync-url requires HTTPS, sync-token-file and local mode")
        if args.serial_port and (args.relay or os.name != 'posix'):
            parser.error("serial-port requires local mode on macOS/Linux")
        serve(args)
    else:
        try:
            data = json.load(sys.stdin)
            if not isinstance(data, dict):
                raise ValueError("Expected a JSON object")
            provider = normalize_claude(data, int(time.time()))
            atomic_json(args.data_dir / "claude.json", provider)
            values = ["{}: {:.0f}%".format(w["id"], w["used_percent"])
                      for w in provider["windows"] if w["used_percent"] is not None]
            print("Lymyt | " + (" · ".join(values) if values else "limit bilgisi bekleniyor"))
        except (OSError, ValueError, TypeError):
            print("Lymyt | limit bilgisi alınamadı")
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
