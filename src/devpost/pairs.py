from __future__ import annotations

import hashlib
import json
import random
from collections.abc import Iterable
from pathlib import Path

HF_REPO = "twangodev/devpost-hacks"


def _project_id(project: dict) -> str:
    if pid := project.get("project_id"):
        return pid
    url = project.get("url") or ""
    return hashlib.sha1(url.encode()).hexdigest()[:12]


def _pair_id(a: dict, b: dict) -> str:
    a_id, b_id = sorted([_project_id(a), _project_id(b)])
    return hashlib.sha1(f"{a_id}|{b_id}".encode()).hexdigest()[:16]


def _is_valid(project: dict) -> bool:
    return project.get("results") != "Error" and bool(project.get("description"))


def _slim(project: dict) -> dict:
    """Project the HF row down to the fields the judge prompt reads.

    HF parquet uses underscores (`built_with`); the prompt template still
    references `built-with`, so normalize on the way out.
    """
    return {
        "url": project.get("url"),
        "title": project.get("title"),
        "tagline": project.get("tagline"),
        "description": project.get("description"),
        "built-with": project.get("built_with") or project.get("built-with"),
        "results": project.get("results"),
        "readmes": project.get("readmes") or [],
    }


def _sample_random(
    projects: list[dict], n: int, rng: random.Random
) -> list[tuple[dict, dict]]:
    pairs: list[tuple[dict, dict]] = []
    seen: set[tuple[str, str]] = set()
    idxs = list(range(len(projects)))
    max_pairs = len(projects) * (len(projects) - 1) // 2
    while len(pairs) < n and len(seen) < max_pairs:
        i, j = rng.sample(idxs, 2)
        a, b = projects[i], projects[j]
        key = tuple(sorted([_project_id(a), _project_id(b)]))
        if key in seen:
            continue
        seen.add(key)
        pairs.append((a, b))
    return pairs


def _load_hf_projects(config: str) -> list[dict]:
    from datasets import load_dataset

    ds = load_dataset(HF_REPO, config, split="train")
    return [dict(row) for row in ds]


def generate_pairs(
    out: Path,
    n: int,
    seed: int,
    config: str,
) -> int:
    projects = [p for p in _load_hf_projects(config) if _is_valid(p)]

    rng = random.Random(seed)
    sampled = _sample_random(projects, n, rng)

    out.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    with out.open("w") as f:
        for a, b in sampled:
            pid = _pair_id(a, b)
            for position in ("ab", "ba"):
                left, right = (a, b) if position == "ab" else (b, a)
                row = {
                    "judgment_id": f"{pid}-{position}",
                    "pair_id": pid,
                    "hackathon": config,
                    "project_a_hackathon": left.get("hackathon"),
                    "project_b_hackathon": right.get("hackathon"),
                    "position": position,
                    "project_a_id": _project_id(left),
                    "project_b_id": _project_id(right),
                    "project_a": _slim(left),
                    "project_b": _slim(right),
                }
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
                written += 1
    return written


def iter_jsonl(path: Path) -> Iterable[dict]:
    with path.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)