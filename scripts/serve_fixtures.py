#!/usr/bin/env python3
"""Tiny GitHub-shaped mock API over the local fixture corpus.

    python3 scripts/serve_fixtures.py --port 8787

Endpoints (GitHub-ish, not a full clone):

    GET /users/{login}
    GET /users/{login}/repos
    GET /users/{login}/events
    GET /users/{login}/gists
    GET /repos/{owner}/{name}
    GET /repos/{owner}/{name}/commits
    GET /users/{login}/contributions
    GET /meta
    GET /healthz
"""

from __future__ import annotations

import argparse
import json
from functools import lru_cache
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / "fixtures" / "github"


def load(path: Path):
    return json.loads(path.read_text())


@lru_cache(maxsize=8)
def generated():
    return {
        "profile": load(FIX / "generated" / "profile.json"),
        "repos": load(FIX / "generated" / "repos.json"),
        "commits": load(FIX / "generated" / "commits.json"),
        "events": load(FIX / "generated" / "events.json"),
        "contrib": load(FIX / "generated" / "contribution-calendar.json"),
        "summary": load(FIX / "generated" / "summary.json"),
        "months": load(FIX / "generated" / "months.json"),
        "languages": load(FIX / "generated" / "languages.json"),
    }


@lru_cache(maxsize=4)
def live_imsakg():
    base = FIX / "imsakg"
    if not (base / "summary.json").exists():
        return None
    return {
        "summary": load(base / "summary.json"),
        "user": load(base / "user.json") if (base / "user.json").exists() else None,
        "repos": load(base / "repos.json") if (base / "repos.json").exists() else [],
        "gists": load(base / "gists.json") if (base / "gists.json").exists() else [],
        "orgs": load(base / "orgs.json") if (base / "orgs.json").exists() else [],
        "pinned": load(base / "pinned.json") if (base / "pinned.json").exists() else [],
    }


def paginate(items, query):
    page = int((query.get("page") or ["1"])[0])
    per_page = int((query.get("per_page") or ["30"])[0])
    per_page = max(1, min(per_page, 100))
    start = (page - 1) * per_page
    return items[start : start + per_page]


class Handler(BaseHTTPRequestHandler):
    server_version = "git-web-client-fixtures/0.1"

    def log_message(self, format, *args):
        print(f"{self.command} {self.path} -> {format % args}")

    def send_json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        parts = [p for p in parsed.path.split("/") if p]
        query = parse_qs(parsed.query)
        try:
            self.dispatch(parts, query)
        except FileNotFoundError:
            self.send_json({"message": "fixtures not generated; run scripts/generate_fixtures.py"}, 503)
        except Exception as exc:  # noqa: BLE001
            self.send_json({"message": str(exc)}, 500)

    def send_file(self, path: Path, content_type: str):
        body = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def dispatch(self, parts, query):
        if not parts or parts == ["index.html"]:
            return self.send_file(ROOT / "web" / "index.html", "text/html; charset=utf-8")
        if parts == ["healthz"]:
            return self.send_json({"ok": True})
        if parts == ["meta"]:
            live = live_imsakg()
            gen = generated()
            return self.send_json(
                {
                    "name": "git-web-client fixture api",
                    "sources": {
                        "generated": gen["summary"],
                        "imsakg": None if live is None else live["summary"],
                    },
                }
            )
        if len(parts) >= 2 and parts[0] == "users":
            return self.handle_user(parts[1], parts[2:], query)
        if len(parts) >= 3 and parts[0] == "repos":
            return self.handle_repo(parts[1], parts[2], parts[3:], query)
        return self.send_json({"message": "Not Found"}, 404)

    def handle_user(self, login, rest, query):
        if login == "imsakg":
            live = live_imsakg()
            if live is None:
                return self.send_json({"message": "imsakg snapshot missing"}, 404)
            if not rest:
                return self.send_json(live["user"] or live["summary"])
            if rest == ["repos"]:
                return self.send_json(paginate(live["repos"], query))
            if rest == ["gists"]:
                return self.send_json(paginate(live["gists"], query))
            if rest == ["orgs"]:
                return self.send_json(live["orgs"])
            if rest == ["pinned"]:
                return self.send_json(live["pinned"])
            return self.send_json({"message": "Not Found"}, 404)

        gen = generated()
        if login != gen["profile"]["login"] and login != "bilgekhani":
            return self.send_json({"message": "Not Found"}, 404)
        if not rest:
            return self.send_json(gen["profile"])
        if rest == ["repos"]:
            vis = (query.get("visibility") or ["all"])[0]
            items = gen["repos"]
            if vis in {"public", "private"}:
                items = [r for r in items if r["visibility"] == vis]
            return self.send_json(paginate(items, query))
        if rest == ["events"]:
            return self.send_json(paginate(list(reversed(gen["events"])), query))
        if rest == ["contributions"]:
            return self.send_json(gen["contrib"])
        if rest == ["languages"]:
            return self.send_json(gen["languages"])
        if rest == ["months"]:
            return self.send_json(gen["months"])
        if rest == ["summary"]:
            return self.send_json(gen["summary"])
        return self.send_json({"message": "Not Found"}, 404)

    def handle_repo(self, owner, name, rest, query):
        gen = generated()
        full = f"{owner}/{name}"
        repo = next((r for r in gen["repos"] if r["full_name"] == full), None)
        if repo is None and owner == "imsakg":
            live = live_imsakg()
            if live:
                repo = next((r for r in live["repos"] if r.get("name") == name), None)
        if repo is None:
            return self.send_json({"message": "Not Found"}, 404)
        if not rest:
            return self.send_json(repo)
        if rest == ["commits"]:
            commits = [c for c in gen["commits"] if c["repo"] == full]
            return self.send_json(paginate(list(reversed(commits)), query))
        return self.send_json({"message": "Not Found"}, 404)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8787)
    args = parser.parse_args()
    httpd = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"fixture api on http://{args.host}:{args.port}")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
