"""USB framing through an actual pseudo-terminal, without touching the Nano."""
import importlib.util
import json
import os
from pathlib import Path
import unittest
from types import SimpleNamespace

spec = importlib.util.spec_from_file_location('lymyt', Path(__file__).resolve().parent.parent / 'bridge' / 'lymyt.py')
lymyt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lymyt)


@unittest.skipUnless(os.name == 'posix', 'USB CDC transport requires macOS/Linux')
class USBFraming(unittest.TestCase):
    def setUp(self):
        import pty
        self.master, self.slave = pty.openpty()
        self.link = lymyt.SerialLink(os.ttyname(self.slave))

    def tearDown(self):
        self.link.close()
        os.close(self.master)
        os.close(self.slave)

    def test_fragmented_ack_and_debug_line(self):
        os.write(self.master, b'{"lymyt":"ack",')
        self.assertEqual(self.link.lines(.1), [])
        os.write(self.master, b'"generated_at":123}\r\nBusy Timeout!\n')
        result = self.link.lines(.1)
        self.assertEqual(json.loads(result[0])['generated_at'], 123)
        self.assertEqual(result[1], 'Busy Timeout!')

    def test_oversized_frame_recovers_on_newline(self):
        for _ in range(24):
            os.write(self.master, b'x' * 500)
            self.assertEqual(self.link.lines(.1), [])
        os.write(self.master, b'\n{"lymyt":"ready"}\n')
        self.assertEqual(self.link.lines(.1), ['{"lymyt":"ready"}'])

    def test_send_is_single_json_frame_and_bounded(self):
        self.link.send({'schema_version': 1, 'providers': {}})
        payload = os.read(self.master, 4096)
        self.assertTrue(payload.endswith(b'\n'))
        self.assertEqual(json.loads(payload)['schema_version'], 1)
        with self.assertRaises(ValueError):
            self.link.send({'payload': 'x' * 8192})

    def test_ack_without_a_sent_snapshot_does_not_mark_device_online(self):
        import tempfile
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as directory:
            bridge = lymyt.Bridge(SimpleNamespace(relay=False, data_dir=Path(directory),
                                                  stale_after=180, no_codex=False))
            class Link:
                def send(self, unused):
                    raise AssertionError('Initial empty Codex snapshot must wait')
                def lines(self):
                    bridge.stop.set()
                    return ['{"lymyt":"ack"}']
                def close(self):
                    pass
            with patch('builtins.print'):
                lymyt.usb_snapshots(bridge, Link())
            self.assertIsNone(bridge.device)

    def test_close_after_device_disappears_still_releases_descriptor(self):
        import termios
        from unittest.mock import patch
        fd = self.link.fd
        with patch('termios.tcsetattr', side_effect=termios.error(6, 'Device not configured')):
            self.link.close()
        self.assertIsNone(self.link.fd)
        with self.assertRaises(OSError):
            os.fstat(fd)

    def test_reconnect_uses_only_the_explicit_port(self):
        import tempfile
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as directory:
            bridge = lymyt.Bridge(SimpleNamespace(relay=False, data_dir=Path(directory),
                                                  stale_after=180, no_codex=True))
            class Link:
                def __init__(self, disconnect):
                    self.disconnect = disconnect
                    self.closed = False
                def send(self, unused):
                    pass
                def lines(self):
                    if self.disconnect:
                        raise OSError('unplugged')
                    bridge.stop.set()
                    return ['{"lymyt":"ready"}']
                def close(self):
                    self.closed = True
            first, second = Link(True), Link(False)
            with patch('builtins.print'), patch.object(bridge.stop, 'wait'), \
                    patch.object(lymyt, 'SerialLink', return_value=second) as reopen:
                lymyt.maintain_usb(bridge, '/dev/selected-nano', first)
            reopen.assert_called_once_with('/dev/selected-nano')
            self.assertTrue(first.closed and second.closed)


if __name__ == '__main__':
    unittest.main()
