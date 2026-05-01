from __future__ import annotations

import base64
import json
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from devpost.pairs import _is_valid, _project_id

CACHE_ROOT = Path(".cache/enrich")

GITHUB_RE = re.compile(r"github\.com[:/]([\w.-]+)/([\w.-]+?)(?:\.git)?(?:/|$)")

PROJECT_SCHEMA = pa.schema(
    [
        ("project_id", pa.string()),
        ("hackathon", pa.string()),
        ("url", pa.string()),
        ("title", pa.string()),
        ("tagline", pa.string()),
        ("description", pa.string()),
        ("built_with", pa.list_(pa.string())),
        ("video_link", pa.string()),
        ("other_links", pa.list_(pa.string())),
        ("results", pa.string()),
        ("is_winner", pa.bool_()),
        (
            "readmes",
            pa.list_(
                pa.struct(
                    [
                        ("repo", pa.string()),
                        ("content", pa.string()),
                        ("truncated", pa.bool_()),
                    ]
                )
            ),
        ),
    ]
)


def _winner_label(results) -> str | None:
    if isinstance(results, list):
        for item in results:
            if isinstance(item, dict) and item.get("winner"):
                return item.get("text") or "Winner"
        return "Winner"
    if isinstance(results, str):
        return results
    return None


def _is_winner_devpost(results) -> bool:
    return isinstance(results, list) and any(
        isinstance(x, dict) and x.get("winner") for x in results
    )


def _build_project_rows(enriched: dict, hackathon: str) -> list[dict]:
    rows: list[dict] = []
    for v in enriched.values():
        if not v.get("description"):
            continue
        url = v.get("url") or ""
        rows.append(
            {
                "project_id": _project_id({"url": url}),
                "hackathon": hackathon,
                "url": url,
                "title": v.get("title"),
                "tagline": v.get("tagline"),
                "description": v.get("description"),
                "built_with": v.get("built-with") or [],
                "video_link": v.get("video-link"),
                "other_links": v.get("other-links") or [],
                "results": _winner_label(v.get("results")),
                "is_winner": _is_winner_devpost(v.get("results")),
                "readmes": v.get("readmes") or [],
            }
        )
    return rows


def _extract_github_repos(other_links: list[str] | None) -> list[tuple[str, str]]:
    if not other_links:
        return []
    repos: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for url in other_links:
        m = GITHUB_RE.search(url or "")
        if not m:
            continue
        owner, repo = m.group(1), m.group(2)
        key = (owner.lower(), repo.lower())
        if key in seen:
            continue
        seen.add(key)
        repos.append((owner, repo))
    return repos


def _fetch_github_readme(owner: str, repo: str, timeout: float = 30.0) -> str | None:
    try:
        result = subprocess.run(
            ["gh", "api", f"repos/{owner}/{repo}/readme", "--jq", ".content"],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except (subprocess.TimeoutExpired, OSError):
        return None
    if result.returncode != 0:
        return None
    encoded = result.stdout.strip()
    if not encoded:
        return None
    try:
        return base64.b64decode(encoded).decode("utf-8", errors="replace")
    except Exception:
        return None


def _truncate(text: str, max_chars: int) -> tuple[str, bool]:
    if len(text) <= max_chars:
        return text, False
    return text[:max_chars] + "\n[... truncated]", True


def enrich_project(
    project: dict,
    cache_dir: Path,
    max_readmes: int = 2,
    readme_chars: int = 6000,
) -> dict:
    pid = _project_id(project)
    cache_file = cache_dir / f"{pid}.json"
    if cache_file.exists():
        try:
            cached = json.loads(cache_file.read_text())
            return cached
        except json.JSONDecodeError:
            pass  # fall through and refetch

    enriched = dict(project)

    readmes: list[dict] = []
    for owner, repo in _extract_github_repos(project.get("other-links"))[:max_readmes]:
        content = _fetch_github_readme(owner, repo)
        if content is None:
            continue
        truncated, was_truncated = _truncate(content, readme_chars)
        readmes.append(
            {"repo": f"{owner}/{repo}", "content": truncated, "truncated": was_truncated}
        )
    enriched["readmes"] = readmes

    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(json.dumps(enriched, ensure_ascii=False, indent=2))
    return enriched


def run(source: Path, out: Path | None, workers: int = 4) -> tuple[int, int, int]:
    raw = json.loads(source.read_text())
    cache_dir = CACHE_ROOT / source.stem
    cache_dir.mkdir(parents=True, exist_ok=True)

    keys = list(raw.keys())
    enriched: dict = {k: raw[k] for k in keys}
    valid_keys = [k for k in keys if _is_valid(raw[k])]

    n_total = len(valid_keys)
    n_with_readme = 0
    n_readmes = 0
    completed = 0

    def _job(k: str) -> tuple[str, dict]:
        return k, enrich_project(raw[k], cache_dir)

    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(_job, k): k for k in valid_keys}
        for fut in as_completed(futures):
            k, e = fut.result()
            enriched[k] = e
            readmes = e.get("readmes") or []
            if readmes:
                n_with_readme += 1
                n_readmes += len(readmes)
            completed += 1
            if completed % 10 == 0 or completed == n_total:
                print(
                    f"  enriched {completed}/{n_total} (readmes={n_readmes})",
                    file=sys.stderr,
                )

    if out is None:
        out = Path(f"data/projects/{source.stem}.parquet")
    out.parent.mkdir(parents=True, exist_ok=True)
    rows = _build_project_rows(enriched, source.stem)
    table = pa.Table.from_pylist(rows, schema=PROJECT_SCHEMA)
    pq.write_table(table, out, compression="zstd")
    return n_total, n_with_readme, n_readmes
