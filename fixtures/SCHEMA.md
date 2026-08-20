# Fixture schema

Two corpora live under `fixtures/github/`.

## `imsakg/` — live snapshot

Read-only clone of the public GitHub user [imsakg](https://github.com/imsakg).
Regenerate with `python3 scripts/snapshot_imsakg.py`.

This is the real profile the CV publishes. Do not invent extra public repos
on this account.

## `generated/` — 13-year synthetic corpus

Deterministic local mock for the git web client. Seeded from CV v4.4.0 and
the live `imsakg` language/topic mix. **Not published to GitHub.**

Career phases baked into the generator:

- 2013-2016 early tinkerer (C/Python/Arduino/homework)
- 2017-2019 independent infra operator
- 2020-2022 uni / GSoC / Teknofest
- 2022-2024 Fora embedded / OSDP / UWB
- 2024 Q1-Q2 Baykar eBPF/XDP/TSN
- 2024-2026 VYVO realtime agents + personal range

Cadence is ~5-6 new repos/month with human zeros and bursts.

Regenerate with `python3 scripts/generate_fixtures.py`.

## Mock API

```bash
python3 scripts/serve_fixtures.py --port 8787
```

Then:

- `GET /users/bilgekhani`
- `GET /users/bilgekhani/repos?per_page=30&page=1`
- `GET /users/bilgekhani/contributions`
- `GET /users/imsakg` (live snapshot, if present)
