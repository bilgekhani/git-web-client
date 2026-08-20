#!/usr/bin/env python3
"""Generate a deterministic 13-year GitHub-shaped fixture corpus.

This is LOCAL mock data for git-web-client. It does not create GitHub repos
and does not rewrite public contribution graphs. Dates, names, and activity
are synthetic but career-shaped around CV v4.4.0 + the live imsakg profile.
"""

from __future__ import annotations

import hashlib
import json
import math
import random
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "fixtures" / "github"
LIVE_DIR = OUT / "imsakg"
GEN_DIR = OUT / "generated"
SEED = "bilgekhani-git-web-client-cv-4.4.0"
OWNER_LOGIN = "bilgekhani"
OWNER_ID = 318754444
START = date(2013, 8, 1)
END = date(2026, 8, 20)
AUTHOR_NAME = "Mert Sefa AKGUN"
AUTHOR_EMAIL = "git@msakg.com"


def rng(seed: str) -> random.Random:
    digest = hashlib.sha256(seed.encode()).hexdigest()
    return random.Random(int(digest[:16], 16))


def iso(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def day_dt(d: date, hour: int, minute: int, second: int = 0) -> datetime:
    return datetime(d.year, d.month, d.day, hour, minute, second, tzinfo=timezone.utc)


def slugify(text: str) -> str:
    keep = []
    for ch in text.lower():
        if ch.isalnum():
            keep.append(ch)
        elif ch in "-_ " and (not keep or keep[-1] != "-"):
            keep.append("-")
    return "".join(keep).strip("-")[:48] or "untitled"


PHASES = [
    {
        "name": "early-tinkerer",
        "start": date(2013, 8, 1),
        "end": date(2016, 12, 31),
        "langs": [("C", 28), ("Python", 22), ("C++", 16), ("Shell", 14), ("PHP", 8), ("Java", 6), ("Arduino", 6)],
        "visibility": 0.78,
        "topics": ["linux", "cli", "homework", "arduino", "sysadmin", "dotfiles", "c", "python"],
        "kinds": [
            ("dotfiles", "rice and configs", "public"),
            ("homework", "coursework / lab notes", "private"),
            ("toy-cli", "tiny CLI experiment", "public"),
            ("arduino", "sensor / LED / radio sketch", "public"),
            ("sysadmin", "server notes and scripts", "private"),
            ("web-php", "tiny PHP/LAMP page", "public"),
        ],
    },
    {
        "name": "infra-operator",
        "start": date(2017, 1, 1),
        "end": date(2019, 12, 31),
        "langs": [("Python", 24), ("Shell", 22), ("C", 14), ("C++", 12), ("Go", 8), ("Nginx", 6), ("Lua", 6), ("PHP", 8)],
        "visibility": 0.62,
        "topics": ["linux", "nginx", "docker", "vpn", "monitoring", "backup", "proxmox", "sysadmin"],
        "kinds": [
            ("ansible-role", "repeatable host setup", "private"),
            ("nginx-edge", "reverse proxy snippets", "private"),
            ("backup", "restic / borg wrapper", "private"),
            ("monitor", "prometheus / node exporter glue", "public"),
            ("vpn", "wireguard / openvpn notes", "private"),
            ("python-ops", "small ops tool", "public"),
            ("kernel-notes", "tuning and sysctl labs", "public"),
        ],
    },
    {
        "name": "uni-gsoc-teknofest",
        "start": date(2020, 1, 1),
        "end": date(2022, 2, 28),
        "langs": [("Python", 30), ("C++", 22), ("C", 16), ("Rust", 10), ("JavaScript", 8), ("Shell", 8), ("MATLAB", 6)],
        "visibility": 0.72,
        "topics": ["gsoc", "fury", "teknofest", "uav", "uuv", "vision", "ros", "embedded", "algorithms"],
        "kinds": [
            ("vision", "underwater / aerial image pipeline", "public"),
            ("gcs", "ground control / telemetry UI", "public"),
            ("autopilot", "ardupilot / mavlink glue", "public"),
            ("algo", "data-structures homework turned library", "public"),
            ("gsoc", "python scientific viz notes", "public"),
            ("firmware-lab", "NuttX / Zephyr experiment", "private"),
            ("site", "personal pages / wiki", "public"),
        ],
    },
    {
        "name": "fora-embedded",
        "start": date(2022, 3, 1),
        "end": date(2024, 2, 29),
        "langs": [("C++", 28), ("C", 22), ("Rust", 18), ("Python", 12), ("TypeScript", 8), ("Lua", 6), ("Shell", 6)],
        "visibility": 0.48,
        "topics": ["rtos", "zephyr", "nuttx", "osdp", "uwb", "ble", "firmware", "security", "tauri"],
        "kinds": [
            ("osdp", "supervised access-control protocol slice", "private"),
            ("rtos-driver", "UART/I2C/SPI peripheral driver", "private"),
            ("uwb-rtls", "TDoA / TWR localization notes", "private"),
            ("crypto-c", "constrained symmetric crypto", "private"),
            ("tauri-tool", "field config / viz app", "public"),
            ("rust-lib", "data structure or protocol helper", "public"),
            ("rice", "hyprland / neovim / rust tooling", "public"),
        ],
    },
    {
        "name": "baykar-tsn",
        "start": date(2024, 3, 1),
        "end": date(2024, 6, 30),
        "langs": [("Rust", 46), ("C", 18), ("Python", 12), ("C++", 10), ("BitBake", 8), ("Shell", 6)],
        "visibility": 0.28,
        "topics": ["ebpf", "xdp", "tsn", "ieee8021", "aya", "yocto", "buildroot", "realtime"],
        "kinds": [
            ("xdp-lab", "XDP drop / redirect bench", "private"),
            ("frer", "802.1CB replication notes", "private"),
            ("ptp", "802.1AS / phc notes", "private"),
            ("yocto-layer", "custom kernel / image bits", "private"),
            ("aya-probe", "Rust Aya experiment", "public"),
            ("net-sim", "userspace TSN simulator", "public"),
        ],
    },
    {
        "name": "vyvo-agents",
        "start": date(2024, 7, 1),
        "end": date(2026, 8, 20),
        "langs": [("Python", 32), ("Rust", 26), ("TypeScript", 14), ("C++", 8), ("Lua", 6), ("Dart", 6), ("Shell", 8)],
        "visibility": 0.55,
        "topics": ["livekit", "pipecat", "webrtc", "rag", "qdrant", "surrealdb", "otel", "agents"],
        "kinds": [
            ("agent-runtime", "session / tool / interrupt notes", "private"),
            ("rag", "multimodal retrieval experiment", "private"),
            ("webrtc", "transport / jitter lab", "public"),
            ("search", "local search / crawler", "public"),
            ("editor", "terminal / worktree tool", "public"),
            ("os-lang", "from-scratch OS or language slice", "public"),
            ("frontend", "svelte / flutter surface", "public"),
            ("infra", "homelab / WAF / proxy", "private"),
        ],
    },
]


KIND_PREFIX = {
    "dotfiles": ["dotfiles", "rice", "cfg", "dots"],
    "homework": ["cs", "lab", "hw", "cmpe"],
    "toy-cli": ["mini", "tiny", "cmd", "cli"],
    "arduino": ["nano", "uno", "avr", "sketch"],
    "sysadmin": ["box", "host", "ops", "srv"],
    "web-php": ["site", "php", "lair"],
    "ansible-role": ["role", "play", "inv"],
    "nginx-edge": ["edge", "vhost", "proxy"],
    "backup": ["snap", "borg", "restic"],
    "monitor": ["prom", "node", "health"],
    "vpn": ["wg", "tun", "jump"],
    "python-ops": ["pyops", "fleet", "ctl"],
    "kernel-notes": ["sysctl", "knotes", "sched"],
    "vision": ["vis", "enhance", "uuvcam"],
    "gcs": ["gcs", "tlm", "ground"],
    "autopilot": ["mav", "apm", "fc"],
    "algo": ["ds", "algo", "struct"],
    "gsoc": ["fury", "viz", "gsoc"],
    "firmware-lab": ["nuttx", "zephyr", "rtos"],
    "site": ["wiki", "pages", "notes"],
    "osdp": ["osdp", "pd", "acp"],
    "rtos-driver": ["drv", "hal", "bus"],
    "uwb-rtls": ["uwb", "tdoa", "rtls"],
    "crypto-c": ["sbox", "aead", "authc"],
    "tauri-tool": ["tauri", "desk", "field"],
    "rust-lib": ["rs", "crate", "lib"],
    "rice": ["hypr", "nvim", "way"],
    "xdp-lab": ["xdp", "bpf", "drop"],
    "frer": ["frer", "cb", "seq"],
    "ptp": ["ptp", "phc", "as"],
    "yocto-layer": ["meta", "yocto", "br"],
    "aya-probe": ["aya", "probe", "kprobe"],
    "net-sim": ["tsnsim", "qbv", "schedsim"],
    "agent-runtime": ["sess", "agent", "toolcall"],
    "rag": ["rag", "emb", "retr"],
    "webrtc": ["rtc", "jitter", "sfu"],
    "search": ["search", "crawl", "idx"],
    "editor": ["ed", "wt", "tui"],
    "os-lang": ["os", "lang", "vm"],
    "frontend": ["kit", "ui", "app"],
    "infra": ["lab", "waf", "edge"],
}

KIND_NOUNS = {
    "dotfiles": ["arch", "void", "i3", "awesome", "x11", "term"],
    "homework": ["os", "net", "ds", "embed", "signals", "automata"],
    "toy-cli": ["todo", "fetch", "weather", "grep", "wc", "cat"],
    "arduino": ["sonar", "imu", "rf", "pwm", "led", "gps"],
    "sysadmin": ["mail", "dns", "jail", "lxc", "backup", "cron"],
    "web-php": ["board", "wiki", "paste", "blog", "gallery"],
    "ansible-role": ["sshd", "nft", "docker", "postgres", "caddy"],
    "nginx-edge": ["tls", "auth", "limit", "static", "ws"],
    "backup": ["offsite", "rotate", "verify", "cold"],
    "monitor": ["disk", "smart", "ping", "cert", "load"],
    "vpn": ["home", "lab", "travel", "site2site"],
    "python-ops": ["inventory", "rotate", "watch", "report"],
    "kernel-notes": ["cfs", "irq", "numa", "tcp", "bbr"],
    "vision": ["clahe", "dehaze", "stereo", "yolo", "track"],
    "gcs": ["map", "hud", "log", "plot", "rc"],
    "autopilot": ["mix", "failsafe", "nav", "ekf"],
    "algo": ["trie", "heap", "graph", "bloom", "skiplist"],
    "gsoc": ["actor", "scene", "ui", "shader"],
    "firmware-lab": ["i2c", "shell", "net", "fs"],
    "site": ["cv", "lab", "log", "garden"],
    "osdp": ["crc", "scbk", "pdcap", "secure"],
    "rtos-driver": ["uart", "spi", "i2c", "can", "adc"],
    "uwb-rtls": ["anchor", "tag", "cal", "ekf"],
    "crypto-c": ["cmac", "gcm", "hkdf", "nonce"],
    "tauri-tool": ["map", "cal", "flash", "log"],
    "rust-lib": ["bytes", "codec", "queue", "slab"],
    "rice": ["bar", "lock", "notif", "term"],
    "xdp-lab": ["redirect", "parse", "map", "bench"],
    "frer": ["seq", "latent", "match", "recover"],
    "ptp": ["sync", "delay", "servo", "phc"],
    "yocto-layer": ["kernel", "initramfs", "machine", "distro"],
    "aya-probe": ["sock", "xdp", "trace", "tc"],
    "net-sim": ["gate", "credit", "preempt", "clock"],
    "agent-runtime": ["turn", "barge", "flush", "supervisor"],
    "rag": ["hybrid", "rerank", "chunk", "cache"],
    "webrtc": ["nack", "jitter", "ice", "srtp"],
    "search": ["tantivy", "surreal", "crawl", "rank"],
    "editor": ["helix", "worktree", "diff", "picker"],
    "os-lang": ["boot", "sched", "lexer", "gc"],
    "frontend": ["pulse", "cockpit", "gcs", "reader"],
    "infra": ["caddy", "auth", "dns", "backup"],
}

COMMIT_VERBS = [
    "wip",
    "fix",
    "refactor",
    "docs",
    "test",
    "chore",
    "perf",
    "build",
    "ci",
    "revert",
]
COMMIT_OBJECTS = [
    "parser",
    "driver",
    "readme",
    "makefile",
    "timeouts",
    "error path",
    "types",
    "tests",
    "logging",
    "config",
    "build",
    "ci",
    "bench",
    "docs",
    "api",
    "state machine",
    "memory",
    "backpressure",
    "shutdown",
    "handshake",
]


def pick_weighted(r: random.Random, pairs):
    names, weights = zip(*pairs)
    return r.choices(names, weights=weights, k=1)[0]


def phase_for(d: date) -> dict:
    for phase in PHASES:
        if phase["start"] <= d <= phase["end"]:
            return phase
    return PHASES[-1]


def month_repo_count(year: int, month: int) -> int:
    r = rng(f"{SEED}:month:{year:04d}-{month:02d}")
    # Human cadence: usually 4-7, occasional 0, occasional burst 9-11.
    roll = r.random()
    if (year, month) in {(2014, 8), (2015, 7), (2018, 8), (2019, 7), (2021, 8), (2023, 8)}:
        return 0
    if roll < 0.07:
        return 0
    if roll < 0.16:
        return r.randint(1, 3)
    if roll > 0.93:
        return r.randint(8, 11)
    return r.randint(4, 7)


def repo_name(r: random.Random, kind: str, used: set[str], created: date) -> str:
    prefixes = KIND_PREFIX[kind]
    nouns = KIND_NOUNS[kind]
    for _ in range(40):
        form = r.choice(["dash", "plain", "year", "rs", "lab"])
        left = r.choice(prefixes)
        right = r.choice(nouns)
        if form == "dash":
            name = f"{left}-{right}"
        elif form == "plain":
            name = f"{left}{right}"
        elif form == "year":
            name = f"{left}-{right}-{created.year}"
        elif form == "rs":
            name = f"{right}-rs" if kind.startswith("rust") or "rust" in kind else f"{left}_{right}"
        else:
            name = f"{left}-{right}-lab"
        name = slugify(name)
        if name not in used:
            return name
    suffix = r.randint(2, 99)
    return slugify(f"{kind}-{created.year}-{suffix}")


def description_for(kind: str, name: str, lang: str, phase: str) -> str:
    templates = {
        "dotfiles": f"Personal {lang} configs and desktop rice ({name}).",
        "homework": f"Course lab / notes. Kept private-ish; {lang} scratch for {name}.",
        "toy-cli": f"Small {lang} CLI to learn the toolchain. Not a product.",
        "arduino": f"Arduino / AVR sketch: sensors, timing, and serial glue.",
        "sysadmin": f"Host notes and scripts from early independent infra work.",
        "web-php": f"Tiny LAMP/PHP page from the early web years.",
        "ansible-role": f"Repeatable {name} role for Linux hosts.",
        "nginx-edge": f"NGINX edge snippets: TLS, limits, and reverse proxy paths.",
        "backup": f"Backup wrapper and restore drill notes.",
        "monitor": f"Tiny health / metrics collector.",
        "vpn": f"Tunnel / jump-host notes. Private by default.",
        "python-ops": f"Python ops helper used on personal boxes.",
        "kernel-notes": f"Kernel / sysctl lab notes.",
        "vision": f"Image pipeline experiment for UAV/UUV work.",
        "gcs": f"Ground-control / telemetry visualization slice.",
        "autopilot": f"Autopilot / MAVLink integration notes.",
        "algo": f"From-scratch {lang} data-structure or algorithm.",
        "gsoc": f"GSoC-era Python scientific visualization notes.",
        "firmware-lab": f"RTOS lab: NuttX/Zephyr board bring-up crumbs.",
        "site": f"Personal pages, wiki, or lab notebook.",
        "osdp": f"Internal OSDP / access-control protocol slice.",
        "rtos-driver": f"Constrained-device driver work ({lang}).",
        "uwb-rtls": f"UWB TDoA/TWR localization notes and tooling.",
        "crypto-c": f"Constrained symmetric crypto / auth in C.",
        "tauri-tool": f"Field configuration / visualization desktop tool.",
        "rust-lib": f"Small Rust library. Learning by implementing internals.",
        "rice": f"Linux desktop / editor rice.",
        "xdp-lab": f"eBPF/XDP bench and parser lab.",
        "frer": f"IEEE 802.1CB FRER notes. Internal.",
        "ptp": f"Time-sync / 802.1AS lab.",
        "yocto-layer": f"Yocto/Buildroot layer crumbs for custom kernels.",
        "aya-probe": f"Rust Aya probe / XDP experiment.",
        "net-sim": f"Userspace TSN scheduler simulator.",
        "agent-runtime": f"Realtime agent session / tool-call notes.",
        "rag": f"Retrieval / memory experiment around Postgres + vectors.",
        "webrtc": f"WebRTC transport / jitter / interruption lab.",
        "search": f"Local search, crawl, or index experiment.",
        "editor": f"Terminal editor / worktree / TUI tool.",
        "os-lang": f"From-scratch OS or language internals.",
        "frontend": f"Svelte/Flutter/TS surface for a personal tool.",
        "infra": f"Homelab / WAF / proxy internals.",
    }
    return templates.get(kind, f"{phase} {lang} project: {name}")


def license_for(r: random.Random, visibility: str, kind: str) -> dict | None:
    if visibility == "private":
        return None
    if kind in {"homework", "sysadmin", "vpn", "osdp", "frer", "agent-runtime"}:
        return None
    roll = r.random()
    if roll < 0.55:
        return {"key": "mit", "name": "MIT License", "spdx_id": "MIT"}
    if roll < 0.75:
        return {"key": "gpl-3.0", "name": "GNU General Public License v3.0", "spdx_id": "GPL-3.0"}
    if roll < 0.88:
        return {"key": "apache-2.0", "name": "Apache License 2.0", "spdx_id": "Apache-2.0"}
    return None


def commit_message(r: random.Random, idx: int) -> str:
    if idx == 0:
        return r.choice(["initial commit", "bootstrap", "first cut", "scaffold"])
    verb = r.choice(COMMIT_VERBS)
    obj = r.choice(COMMIT_OBJECTS)
    extra = r.choice(
        [
            "",
            "",
            "",
            ": handle edge case",
            ": drop dead code",
            ": less allocation",
            ": make it compile",
            ": add failing test",
            ": unbreak CI",
            " after field bug",
        ]
    )
    if r.random() < 0.08:
        return r.choice(["oops", "tmp", "why", "aaaa", "fixup", "wip wip"])
    return f"{verb}: {obj}{extra}"


def sha_for(*parts: str) -> str:
    return hashlib.sha1("|".join(parts).encode()).hexdigest()


def activity_days(created: date, last: date, r: random.Random) -> list[date]:
    days = []
    span = max(1, (last - created).days)
    commits = r.randint(3, 28 if span > 40 else 14)
    if r.random() < 0.12:
        commits = r.randint(1, 3)  # abandoned after bootstrap
    used = set()
    for _ in range(commits * 3):
        if len(used) >= commits:
            break
        offset = int(abs(r.gauss(0.25, 0.28)) * span)
        offset = min(span, max(0, offset))
        day = created + timedelta(days=offset)
        # weekday bias
        if day.weekday() >= 5 and r.random() < 0.55:
            continue
        used.add(day)
    if created not in used:
        used.add(created)
    return sorted(used)


def contribution_from_commits(commits: list[dict]) -> dict:
    by_day: dict[str, int] = defaultdict(int)
    for c in commits:
        by_day[c["committed_at"][:10]] += 1
    weeks = []
    cursor = START
    # align to Sunday like GitHub
    cursor -= timedelta(days=(cursor.weekday() + 1) % 7)
    while cursor <= END:
        week = []
        for i in range(7):
            d = cursor + timedelta(days=i)
            key = d.isoformat()
            count = by_day.get(key, 0)
            if count == 0:
                level = 0
            elif count == 1:
                level = 1
            elif count <= 3:
                level = 2
            elif count <= 6:
                level = 3
            else:
                level = 4
            week.append({"date": key, "count": count, "level": level})
        weeks.append(week)
        cursor += timedelta(days=7)
    return {
        "from": START.isoformat(),
        "to": END.isoformat(),
        "total": len(commits),
        "weeks": weeks,
    }


def generate_repos() -> tuple[list[dict], list[dict], list[dict]]:
    used_names: set[str] = set()
    repos: list[dict] = []
    commits: list[dict] = []
    events: list[dict] = []
    repo_id = 10_000
    year = START.year
    month = START.month
    while date(year, month, 1) <= END:
        count = month_repo_count(year, month)
        month_rng = rng(f"{SEED}:plan:{year:04d}-{month:02d}")
        days_in_month = (date(year + (month == 12), 1 if month == 12 else month + 1, 1) - timedelta(days=1)).day
        chosen_days = sorted(month_rng.sample(range(1, days_in_month + 1), k=min(count, days_in_month)))
        # if we need more than unique days, reuse later days
        while len(chosen_days) < count:
            chosen_days.append(month_rng.randint(1, days_in_month))
        for day_n in chosen_days[:count]:
            created = date(year, month, min(day_n, days_in_month))
            if created < START or created > END:
                continue
            phase = phase_for(created)
            r = rng(f"{SEED}:repo:{year:04d}-{month:02d}-{day_n}:{len(repos)}")
            kind, _blurb, default_vis = r.choice(phase["kinds"])
            lang = pick_weighted(r, phase["langs"])
            visibility = "public" if r.random() < phase["visibility"] else "private"
            if default_vis == "private" and r.random() < 0.7:
                visibility = "private"
            name = repo_name(r, kind, used_names, created)
            used_names.add(name)
            created_at = day_dt(created, r.randint(7, 23), r.randint(0, 59), r.randint(0, 59))
            life_days = r.choice([2, 5, 9, 14, 21, 40, 70, 120, 200, 400])
            if visibility == "private":
                life_days = min(life_days, 180)
            last = min(END, created + timedelta(days=life_days))
            if r.random() < 0.08:
                last = created  # one-and-done
            days = activity_days(created, last, r)
            pushed_at = day_dt(days[-1], r.randint(8, 23), r.randint(0, 59), r.randint(0, 59))
            updated_at = pushed_at
            archived = last < date(2024, 1, 1) and r.random() < 0.11
            fork = r.random() < 0.07
            stars = 0 if visibility == "private" else max(0, int(r.expovariate(0.85)) - 1)
            if not fork and visibility == "public" and r.random() < 0.04:
                stars += r.randint(3, 18)
            forks = 0 if visibility == "private" else (1 if stars > 8 and r.random() < 0.4 else 0)
            topics = r.sample(phase["topics"], k=min(len(phase["topics"]), r.randint(2, 5)))
            repo_id += 1
            full_name = f"{OWNER_LOGIN}/{name}"
            repo = {
                "id": repo_id,
                "node_id": f"R_FIX_{repo_id}",
                "name": name,
                "full_name": full_name,
                "private": visibility == "private",
                "visibility": visibility,
                "owner": {"login": OWNER_LOGIN, "id": OWNER_ID, "type": "User"},
                "html_url": f"https://github.com/{full_name}",
                "description": description_for(kind, name, lang, phase["name"]),
                "fork": fork,
                "created_at": iso(created_at),
                "updated_at": iso(updated_at),
                "pushed_at": iso(pushed_at),
                "homepage": "https://msakg.com" if r.random() < 0.04 else None,
                "size": r.randint(12, 4800),
                "stargazers_count": stars,
                "watchers_count": stars,
                "forks_count": forks,
                "open_issues_count": 0 if visibility == "private" else r.randint(0, 4),
                "language": None if lang in {"Arduino", "Nginx", "BitBake", "MATLAB"} and r.random() < 0.3 else lang,
                "archived": archived,
                "disabled": False,
                "license": license_for(r, visibility, kind),
                "topics": topics,
                "default_branch": "master" if created.year < 2021 and r.random() < 0.7 else "main",
                "has_issues": visibility == "public",
                "has_wiki": False,
                "has_pages": name.endswith("github-io") or r.random() < 0.02,
                "is_template": kind in {"ansible-role", "rust-lib"} and r.random() < 0.08,
                "fixture": {
                    "phase": phase["name"],
                    "kind": kind,
                    "synthetic": True,
                },
            }
            repos.append(repo)
            events.append(
                {
                    "id": f"evt-create-{repo_id}",
                    "type": "CreateEvent",
                    "created_at": iso(created_at),
                    "repo": {"id": repo_id, "name": full_name},
                    "payload": {"ref_type": "repository", "ref": None},
                }
            )
            for i, day in enumerate(days):
                cr = rng(f"{SEED}:commit:{full_name}:{day.isoformat()}:{i}")
                committed = day_dt(day, cr.randint(8, 23), cr.randint(0, 59), cr.randint(0, 59))
                sha = sha_for(full_name, day.isoformat(), str(i), commit_message(cr, i))
                commit = {
                    "sha": sha,
                    "repo": full_name,
                    "message": commit_message(cr, i),
                    "author": {"name": AUTHOR_NAME, "email": AUTHOR_EMAIL, "date": iso(committed)},
                    "committer": {"name": AUTHOR_NAME, "email": AUTHOR_EMAIL, "date": iso(committed)},
                    "committed_at": iso(committed),
                    "html_url": f"https://github.com/{full_name}/commit/{sha}",
                    "stats": {
                        "additions": cr.randint(1, 240),
                        "deletions": cr.randint(0, 80),
                        "total": 0,
                    },
                }
                commit["stats"]["total"] = commit["stats"]["additions"] + commit["stats"]["deletions"]
                commits.append(commit)
                if i == 0 or cr.random() < 0.35:
                    events.append(
                        {
                            "id": f"evt-push-{sha[:12]}",
                            "type": "PushEvent",
                            "created_at": iso(committed),
                            "repo": {"id": repo_id, "name": full_name},
                            "payload": {"size": 1, "distinct_size": 1, "ref": f"refs/heads/{repo['default_branch']}"},
                        }
                    )
        if month == 12:
            year += 1
            month = 1
        else:
            month += 1
    repos.sort(key=lambda x: x["created_at"])
    commits.sort(key=lambda x: x["committed_at"])
    events.sort(key=lambda x: x["created_at"])
    return repos, commits, events


def language_bytes(repos: list[dict]) -> dict[str, int]:
    out: dict[str, int] = defaultdict(int)
    for repo in repos:
        lang = repo.get("language") or "Other"
        out[lang] += max(1200, repo["size"] * 18)
    return dict(sorted(out.items(), key=lambda kv: -kv[1]))


def load_live_imsakg() -> dict | None:
    path = LIVE_DIR / "summary.json"
    if not path.exists():
        return None
    return json.loads(path.read_text())


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


def main() -> None:
    GEN_DIR.mkdir(parents=True, exist_ok=True)
    repos, commits, events = generate_repos()
    langs = language_bytes(repos)
    public = [r for r in repos if r["visibility"] == "public"]
    private = [r for r in repos if r["visibility"] == "private"]
    by_year = Counter(r["created_at"][:4] for r in repos)
    by_month = Counter(r["created_at"][:7] for r in repos)
    by_phase = Counter(r["fixture"]["phase"] for r in repos)
    by_lang = Counter(r.get("language") or "None" for r in repos)
    contribution = contribution_from_commits(commits)

    profile = {
        "login": OWNER_LOGIN,
        "id": OWNER_ID,
        "name": AUTHOR_NAME,
        "bio": "Lead Software Engineer — Full-Spectrum Systems & AI",
        "blog": "https://msakg.com",
        "company": "@Vyvo-Labs",
        "location": "Istanbul, Turkiye",
        "email": "contact@msakg.com",
        "twitter_username": "imsakg",
        "html_url": f"https://github.com/{OWNER_LOGIN}",
        "avatar_url": "https://avatars.githubusercontent.com/u/318754444?v=4",
        "created_at": "2026-08-19T19:03:34Z",
        "public_repos": len(public),
        "total_private_repos": len(private),
        "followers": 0,
        "following": 0,
        "type": "User",
        "source": {
            "kind": "synthetic-fixture",
            "seed": SEED,
            "based_on": ["cv-v4.4.0", "github.com/imsakg", "linkedin.com/in/msakg"],
            "note": "Local mock only. The live GitHub account is one day old; this corpus is not published.",
        },
        "cv": {
            "version": "4.4.0",
            "title": "Lead Software Engineer — Full-Spectrum Systems & AI",
            "github": "https://github.com/imsakg",
            "linkedin": "https://www.linkedin.com/in/msakg",
            "site": "https://www.msakg.com",
        },
    }

    summary = {
        "owner": OWNER_LOGIN,
        "generated_at": iso(datetime.now(timezone.utc)),
        "span": {"from": START.isoformat(), "to": END.isoformat()},
        "repos": len(repos),
        "public_repos": len(public),
        "private_repos": len(private),
        "forks": sum(1 for r in repos if r["fork"]),
        "commits": len(commits),
        "events": len(events),
        "avg_repos_per_month": round(len(repos) / max(1, len(by_month)), 2),
        "months_with_zero_repos": sum(1 for c in by_month.values() if c == 0),
        "by_year": dict(sorted(by_year.items())),
        "by_phase": dict(by_phase),
        "by_language": dict(by_lang.most_common()),
        "language_bytes": langs,
        "live_imsakg": load_live_imsakg(),
    }

    write_json(GEN_DIR / "profile.json", profile)
    write_json(GEN_DIR / "repos.json", repos)
    write_json(GEN_DIR / "commits.json", commits)
    write_json(GEN_DIR / "events.json", events)
    write_json(GEN_DIR / "languages.json", langs)
    write_json(GEN_DIR / "contribution-calendar.json", contribution)
    write_json(GEN_DIR / "summary.json", summary)

    # Compact month index for UI lists.
    month_index = []
    grouped: dict[str, list[dict]] = defaultdict(list)
    for repo in repos:
        grouped[repo["created_at"][:7]].append(
            {
                "name": repo["name"],
                "visibility": repo["visibility"],
                "language": repo["language"],
                "kind": repo["fixture"]["kind"],
            }
        )
    cursor = date(START.year, START.month, 1)
    while cursor <= END:
        key = cursor.strftime("%Y-%m")
        month_index.append({"month": key, "count": len(grouped.get(key, [])), "repos": grouped.get(key, [])})
        if cursor.month == 12:
            cursor = date(cursor.year + 1, 1, 1)
        else:
            cursor = date(cursor.year, cursor.month + 1, 1)
    write_json(GEN_DIR / "months.json", month_index)

    print(json.dumps({k: summary[k] for k in ("repos", "public_repos", "private_repos", "commits", "avg_repos_per_month", "by_phase", "by_language")}, indent=2))


if __name__ == "__main__":
    main()
