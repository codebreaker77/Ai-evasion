"""Lightweight local web server for the Zero-Width Obfuscator frontend.

Runs with Python's standard library (no pip packages required).
Automatically launches your default web browser.
"""

from __future__ import annotations

import functools
import http.server
import os
import socketserver
import webbrowser

PORT = 5000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))


def main():
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=DIRECTORY)

    # Enable socket reuse
    socketserver.TCPServer.allow_reuse_address = True

    try:
        with socketserver.TCPServer(("", PORT), handler) as httpd:
            url = f"http://localhost:{PORT}"
            print(f"Local server running at: {url}")
            print("Press Ctrl+C to stop.")

            # Automatically launch the web browser
            webbrowser.open(url)

            httpd.serve_forever()
    except OSError:
        # Fallback to alternate port if 5000 is occupied
        alt_port = 8080
        with socketserver.TCPServer(("", alt_port), handler) as httpd:
            url = f"http://localhost:{alt_port}"
            print(f"Port {PORT} was busy. Started on {url}")
            webbrowser.open(url)
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[Server stopped]")


if __name__ == "__main__":
    main()
