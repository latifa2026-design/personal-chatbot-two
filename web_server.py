"""
Local web server for the Groq-powered chatbot.

Serves the HTML/CSS/JS frontend from ./static and exposes a small JSON API so
the browser can talk to the Groq model (same system prompt / persona as the
Tkinter desktop app in main.py).

How to run:
    python web_server.py

Then open http://127.0.0.1:8000 in your browser.
"""

import json
import os
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from dotenv import load_dotenv

# Load the .env that lives next to this file no matter where the server is
# started from. (main.py also loads it, but only relative to the CWD.)
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# Reuse the chatbot's Groq client, model, persona and conversation history.
# Importing main.py does NOT open the Tkinter GUI — that only happens when
# main.py is run directly.
from main import (
    MODEL_NAME,
    PROFILE_NAME,
    PUBLICATIONS,
    MEU_ROLE,
    client,
    conversation_history,
)  # noqa: E402

STATIC_DIR = BASE_DIR / "static"
# Bind to 0.0.0.0 when running on Render (set as an env var there) so the
# service is reachable. Locally the default stays 127.0.0.1.
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))

# The shared conversation history is guarded by a lock because requests are
# handled by several threads.
history_lock = threading.Lock()


class ChatRequestHandler(SimpleHTTPRequestHandler):
    """Serves the static frontend and the JSON API from one server."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    # -- GET: static files + conversation history -------------------------
    def do_GET(self):
        if self.path == "/api/history":
            with history_lock:
                history = [
                    {"role": m["role"], "content": m["content"]}
                    for m in conversation_history
                    if m["role"] != "system"
                ]
            self._send_json({"history": history})
            return
        if self.path == "/api/publications":
            # Research publications - journal name with volume number etc.
            self._send_json({"publications": PUBLICATIONS})
            return
        if self.path == "/api/meu":
            # MEU role & activities (Member Secretary & Coordinator, UMC)
            self._send_json(MEU_ROLE)
            return
        super().do_GET()

    # -- POST: send a chat message to Groq --------------------------------
    def do_POST(self):
        if self.path != "/api/chat":
            self._send_json({"error": f"Not found: {self.path}"}, status=404)
            return

        # 1. Read and validate the request body.
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length) if length else b"{}")
            message = str(body.get("message", "")).strip()
        except (json.JSONDecodeError, ValueError) as exc:
            self._send_json(
                {"error": f"Invalid request body: {exc}"}, status=400
            )
            return

        if not message:
            self._send_json(
                {"error": "Message must not be empty."}, status=400
            )
            return

        # 2. Ask Groq (same call and same conversation history as main.py).
        try:
            with history_lock:
                conversation_history.append(
                    {"role": "user", "content": message}
                )
                messages = list(conversation_history)

            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
            )
            reply = response.choices[0].message.content

            with history_lock:
                conversation_history.append(
                    {"role": "assistant", "content": reply}
                )

            self._send_json({"reply": reply})
        except Exception as exc:  # noqa: BLE001
            self._send_json({"error": f"Groq error: {exc}"}, status=500)

    # -- helpers -----------------------------------------------------------
    def _send_json(self, payload, status=200):
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)


def main():
    server = ThreadingHTTPServer((HOST, PORT), ChatRequestHandler)
    print("=" * 64)
    print(f"  {PROFILE_NAME} — Web Chatbot")
    print(f"  Model: {MODEL_NAME}")
    print(f"  Open in your browser:  http://{HOST}:{PORT}")
    print("  API: /api/chat  /api/history  /api/publications  /api/meu")
    print("  Press Ctrl+C to stop the server.")
    print("=" * 64)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()