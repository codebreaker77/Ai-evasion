"""Lightweight local web server for the Zero-Width Obfuscator frontend.

Runs with Python's standard library (no pip packages required).
Automatically launches your default web browser and provides a local /api/count endpoint.
"""

from __future__ import annotations

import http.server
import json
import os
import socketserver
import urllib.parse
import webbrowser

PORT = 5000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))


class CustomRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Serves static files and provides a local fallback /api/count endpoint."""

    unique_visitors: set[str] = set()
    current_count: int = 291

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)

        if parsed.path == "/api/count":
            query = urllib.parse.parse_qs(parsed.query)
            visitor_id = query.get("visitorId", ["local"])[0]
            client_ip = self.client_address[0]
            unique_key = f"{client_ip}_{visitor_id}"

            if unique_key not in self.unique_visitors:
                self.unique_visitors.add(unique_key)
                if len(self.unique_visitors) > 1:
                    CustomRequestHandler.current_count += 1

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            response_data = json.dumps({"count": CustomRequestHandler.current_count})
            self.wfile.write(response_data.encode("utf-8"))
            return

        super().do_GET()

    def log_message(self, format, *args):
        # Keep terminal output clean
        pass


def main():
    socketserver.TCPServer.allow_reuse_address = True

    try:
        with socketserver.TCPServer(("", PORT), CustomRequestHandler) as httpd:
            url = f"http://localhost:{PORT}"
            print(f"Local server running at: {url}")
            print("Press Ctrl+C to stop.")
            webbrowser.open(url)
            httpd.serve_forever()
    except OSError:
        alt_port = 8080
        with socketserver.TCPServer(("", alt_port), CustomRequestHandler) as httpd:
            url = f"http://localhost:{alt_port}"
            print(f"Port {PORT} was busy. Started on {url}")
            webbrowser.open(url)
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[Server stopped]")


if __name__ == "__main__":
    main()
