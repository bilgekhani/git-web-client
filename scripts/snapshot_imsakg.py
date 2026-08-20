#!/usr/bin/env python3
"""Snapshot the live public GitHub profile for imsakg into fixtures.

Read-only. Does not create, delete, or mutate repositories.
Uses the public GitHub API; an optional GITHUB_TOKEN / gh auth token
raises the rate limit.
"""

from __future__ import annotations

import json
import os
import subprocess
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "fixtures" / "github" / "imsakg"
LOGIN = "imsakg"
API = "https://api.github.com"


def token() -> str | None:
    env = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if env:
        return env
    try:
        proc = subprocess.run(
            ["gh", "auth", "token", "-h", "github.com"],
            check=False,
            capture_output=True,
            text=True,
        )
        tok = (proc.stdout or "").strip()
        return tok or None
    except OSError:
        return None


def get(path: str):
    req = urllib.request.Request(
        f"{API}{path}",
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "git-web-client-fixture-snapshot",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    tok = token()
    if tok:
        req.add_header("Authorization", f"Bearer {tok}")
    with urllib.request.urlopen(req, timeout=45) as resp:
        return json.loads(resp.read().decode())


def compact_repo(repo: dict) -> dict:
    license_info = repo.get("license") or {}
    return {
        "name": repo.get("name"),
        "full_name": repo.get("full_name"),
        "description": repo.get("description"),
        "html_url": repo.get("html_url"),
        "clone_url": repo.get("clone_url"),
        "homepage": repo.get("homepage"),
        "language": repo.get("language"),
        "stargazers_count": repo.get("stargazers_count", 0),
        "forks_count": repo.get("forks_count", 0),
        "watchers_count": repo.get("watchers_count", 0),
        "open_issues_count": repo.get("open_issues_count", 0),
        "fork": bool(repo.get("fork")),
        "archived": bool(repo.get("archived")),
        "disabled": bool(repo.get("disabled")),
        "is_template": bool(repo.get("is_template")),
        "visibility": repo.get("visibility") or ("private" if repo.get("private") else "public"),
        "default_branch": repo.get("default_branch"),
        "created_at": repo.get("created_at"),
        "updated_at": repo.get("updated_at"),
        "pushed_at": repo.get("pushed_at"),
        "license": license_info.get("spdx_id") if license_info.get("spdx_id") != "NOASSERTION" else None,
        "topics": repo.get("topics") or [],
        "size": repo.get("size", 0),
        "has_issues": bool(repo.get("has_issues")),
        "has_wiki": bool(repo.get("has_wiki")),
        "has_pages": bool(repo.get("has_pages")),
        "has_discussions": bool(repo.get("has_discussions")),
    }


def write(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(payload, (dict, list)):
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    else:
        path.write_text(str(payload))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    user = get(f"/users/{LOGIN}")
    write(OUT / "user.json", user)

    repos: list[dict] = []
    page = 1
    while True:
        chunk = get(f"/users/{LOGIN}/repos?per_page=100&page={page}&type=owner&sort=updated")
        if not chunk:
            break
        repos.extend(chunk)
        if len(chunk) < 100:
            break
        page += 1
    compact = [compact_repo(r) for r in repos]
    write(OUT / "repos.json", compact)

    try:
        gists = get(f"/users/{LOGIN}/gists?per_page=100")
    except urllib.error.HTTPError:
        gists = []
    write(OUT / "gists.json", gists)

    try:
        orgs = get(f"/users/{LOGIN}/orgs")
    except urllib.error.HTTPError:
        orgs = []
    write(OUT / "orgs.json", orgs)

    try:
        readme = get(f"/repos/{LOGIN}/{LOGIN}/readme")
        import base64

        body = base64.b64decode(readme.get("content") or "").decode("utf-8", "replace")
        write(OUT / "profile-readme.md", body)
    except Exception as exc:  # noqa: BLE001
        write(OUT / "profile-readme.md", f"# snapshot failed\n\n{exc}\n")

    pinned = []
    try:
        req = urllib.request.Request(
            "https://api.github.com/graphql",
            data=json.dumps(
                {
                    "query": """
                    query($login: String!) {
                      user(login: $login) {
                        pinnedItems(first: 6, types: REPOSITORY) {
                          nodes {
                            ... on Repository {
                              nameWithOwner
                              description
                              stargazerCount
                              isPrivate
                              primaryLanguage { name }
                            }
                          }
                        }
                      }
                    }
                    """,
                    "variables": {"login": LOGIN},
                }
            ).encode(),
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "git-web-client-fixture-snapshot",
            },
            method="POST",
        )
        tok = token()
        if tok:
            req.add_header("Authorization", f"Bearer {tok}")
        with urllib.request.urlopen(req, timeout=45) as resp:
            payload = json.loads(resp.read().decode())
        pinned = (
            (((payload.get("data") or {}).get("user") or {}).get("pinnedItems") or {}).get("nodes")
            or []
        )
        write(OUT / "pinned.json", pinned)
    except Exception as exc:  # noqa: BLE001
        write(OUT / "pinned.json", {"error": str(exc)})

    langs: dict[str, int] = {}
    for repo in compact:
        key = repo.get("language") or "None"
        langs[key] = langs.get(key, 0) + 1
    created = [r["created_at"] for r in compact if r.get("created_at")]
    summary = {
        "login": user.get("login"),
        "id": user.get("id"),
        "name": user.get("name"),
        "blog": user.get("blog"),
        "company": user.get("company"),
        "location": user.get("location"),
        "email": user.get("email"),
        "twitter": user.get("twitter_username"),
        "followers": user.get("followers"),
        "following": user.get("following"),
        "public_repos": user.get("public_repos"),
        "public_gists": user.get("public_gists"),
        "created_at": user.get("created_at"),
        "html_url": user.get("html_url"),
        "avatar_url": user.get("avatar_url"),
        "repo_count": len(compact),
        "original_count": sum(1 for r in compact if not r.get("fork")),
        "fork_count": sum(1 for r in compact if r.get("fork")),
        "language_histogram": dict(sorted(langs.items(), key=lambda kv: -kv[1])),
        "oldest_repo_created_at": min(created) if created else None,
        "newest_repo_created_at": max(created) if created else None,
        "pinned": [n.get("nameWithOwner") for n in pinned if isinstance(n, dict)],
        "snapshotted_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    write(OUT / "summary.json", summary)
    print(json.dumps({k: summary[k] for k in ("login", "repo_count", "original_count", "fork_count", "followers", "created_at")}, indent=2))


if __name__ == "__main__":
    main()
