from __future__ import annotations

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


HOST = "127.0.0.1"
PORT = 8765
SITE_ROOT = Path(__file__).resolve().parents[1]


class QuietStaticHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        return


class LocalStaticServer(ThreadingHTTPServer):
    allow_reuse_address = False
    daemon_threads = True


def main() -> None:
    handler = partial(QuietStaticHandler, directory=str(SITE_ROOT))
    with LocalStaticServer((HOST, PORT), handler) as server:
        server.serve_forever()


if __name__ == "__main__":
    main()
