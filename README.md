# git-web-client

Personal git forge web client. The first slice is a private GitHub repo plus
local mock data so the UI can be built against a realistic nerd/hacker profile
without inventing live GitHub history.

## Why fixtures, not a fake GitHub graph

`bilgekhani` was created on 2026-08-19 and started empty. GitHub does not let
you backdate `created_at` on an account or a repository. Pushing ~800 synthetic
repos with rewritten commit dates would:

- violate GitHub's acceptable-use rules around fake/misleading content
- be immediately visible as fake (every repo created today)
- misrepresent a career that already has a real public graph on [`imsakg`](https://github.com/imsakg)

This repo therefore keeps the 13-year corpus **inside** `fixtures/`. The client
can render it as if it were a forge API. Later we can add a live adapter for
real accounts (`imsakg`, this repo, or a local Forgejo).

## Fixture corpus

Generated, deterministic, CV-shaped:

- owner: `bilgekhani`
- span: 2013-08 through 2026-08
- ~5-6 new repos / month with human gaps and bursts
- public/private mix
- language weight: Rust, C++, Python, plus C / Lua / TS / Shell
- topic arc: student systems → sysadmin → embedded/RTOS → eBPF/TSN → realtime agents

Regenerate:

```bash
python3 scripts/generate_fixtures.py
```

Outputs land in `fixtures/github/`.

## Preview

```bash
python3 scripts/snapshot_imsakg.py   # live public profile
python3 scripts/generate_fixtures.py # 13-year synthetic corpus
python3 scripts/serve_fixtures.py --port 8787
```

Open http://127.0.0.1:8787

Rust loader:

```bash
cargo test
cargo run
```

## Live GitHub

This repository: https://github.com/bilgekhani/git-web-client (private)

The published identity on the CV is still [imsakg](https://github.com/imsakg).
`bilgekhani` is the fresh private-work account. Do not backdate or
bulk-create public GitHub repos to fake a contribution graph.

```bash
gh repo view bilgekhani/git-web-client
```

## Status

Private repo + fixture store + mock API + preview page. Real client UI next.
