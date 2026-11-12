"""Fake Anthropic Messages endpoint on 127.0.0.1 (for testing only).

Answers POST /v1/messages with a keyword-rule label, logs every
request body to requests.jsonl, so we can check (1) what promptfoo
sends (model, max_tokens, effort, no temperature) and (2) whether a
rerun is served from cache (no new requests logged).

python fake_anthropic_server.py PORT LOGFILE
"""
import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT, LOG = int(sys.argv[1]), sys.argv[2]
RULES = [("refund", ["refund", "money back", "charged", "reimbursed"]),
         ("account", ["log in", "password", "account", "phone number"]),
         ("delivery", ["driver", "late", "delivered", "address"])]


def label(text):
    t = text.lower()
    for name, words in RULES:
        if any(w in t for w in words):
            return name
    return "other"


class H(BaseHTTPRequestHandler):
    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["content-length"])))
        with open(LOG, "a") as f:
            f.write(json.dumps({"path": self.path, "body": body}) + "\n")
        user = body["messages"][-1]["content"]
        if isinstance(user, list):
            user = " ".join(b.get("text", "") for b in user)
        resp = {
            "id": "msg_fake", "type": "message", "role": "assistant",
            "model": body.get("model"),
            "content": [{"type": "text", "text": label(user)}],
            "stop_reason": "end_turn", "stop_sequence": None,
            "usage": {"input_tokens": 50, "output_tokens": 2},
        }
        data = json.dumps(resp).encode()
        self.send_response(200)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *a):
        pass


HTTPServer(("127.0.0.1", PORT), H).serve_forever()
