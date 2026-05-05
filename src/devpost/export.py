"""Stage per-hackathon parquets into HuggingFace dataset layout.

Two flows:
- `stage_projects` — bundles `data/projects/<h>.parquet` (produced by `devpost
  enrich`) into HF layout under `data/hf/`.
- `stage_judgments` — converts `data/<h>/judgments.jsonl` (produced by
  `devpost judge`) into ChatML/messages format and bundles under
  `data/hf-judgments/`.

Both produce per-hackathon configs + a default `all` config (concat of all).
"""

from __future__ import annotations

import json
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from devpost.finalize import _build_row as _build_judgment_row

PROJECTS_SRC = Path("data/projects")
PROJECTS_OUT = Path("data/hf")
JUDGMENTS_SRC = Path("data")
JUDGMENTS_OUT = Path("data/hf-judgments")

PARQUET_KW = dict(compression="zstd", write_page_index=True, row_group_size=500)

JUDGMENT_SCHEMA = pa.schema(
    [
        (
            "messages",
            pa.list_(
                pa.struct(
                    [
                        ("role", pa.string()),
                        ("content", pa.string()),
                    ]
                )
            ),
        ),
        ("judgment_id", pa.string()),
        ("pair_id", pa.string()),
        ("hackathon", pa.string()),
        ("position", pa.string()),
        ("project_a_id", pa.string()),
        ("project_b_id", pa.string()),
        ("verdict", pa.string()),
        ("gt_a_result", pa.string()),
        ("gt_b_result", pa.string()),
        ("model", pa.string()),
        ("prompt_tokens", pa.int64()),
        ("completion_tokens", pa.int64()),
        ("finish_reason", pa.string()),
        ("latency_s", pa.float64()),
        ("sampling", pa.string()),
    ]
)


def _write(table: pa.Table, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(table, path, **PARQUET_KW)


def stage_projects(out_dir: Path | None = None) -> int:
    out_dir = out_dir or PROJECTS_OUT
    data_dir = out_dir / "data"
    sources = sorted(PROJECTS_SRC.glob("*.parquet"))
    if not sources:
        raise SystemExit(f"no parquets in {PROJECTS_SRC}; run `devpost enrich` first")

    tables: list[pa.Table] = []
    print(f"  {'hackathon':<28} {'rows':>6}")
    for src in sources:
        hackathon = src.stem
        t = pq.read_table(src)
        _write(t, data_dir / hackathon / "train.parquet")
        tables.append(t)
        print(f"  {hackathon:<28} {t.num_rows:>6}")

    combined = pa.concat_tables(tables)
    _write(combined, data_dir / "all" / "train.parquet")
    print(f"  {'all':<28} {combined.num_rows:>6}  (default)")
    return len(sources)


def _read_judgment_rows(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(_build_judgment_row(json.loads(line)))
    return rows


def stage_judgments(out_dir: Path | None = None) -> int:
    """Bundle all judgments*.jsonl files under data/<hackathon>/ into HF layout.

    Multiple judges' files (e.g. judgments.jsonl + judgments-small.jsonl) are
    concatenated per hackathon; each row's `model` field disambiguates them.
    """
    out_dir = out_dir or JUDGMENTS_OUT
    data_dir = out_dir / "data"

    by_hackathon: dict[str, list[Path]] = {}
    for src in sorted(JUDGMENTS_SRC.glob("*/judgments*.jsonl")):
        by_hackathon.setdefault(src.parent.name, []).append(src)
    if not by_hackathon:
        raise SystemExit(f"no judgments*.jsonl under {JUDGMENTS_SRC}/*/")

    tables: list[pa.Table] = []
    print(f"  {'hackathon':<28} {'rows':>6}  {'MB':>6}  files")
    for hackathon, sources in sorted(by_hackathon.items()):
        rows: list[dict] = []
        for src in sources:
            rows.extend(_read_judgment_rows(src))
        if not rows:
            continue
        t = pa.Table.from_pylist(rows, schema=JUDGMENT_SCHEMA)
        out = data_dir / hackathon / "train.parquet"
        _write(t, out)
        size_mb = out.stat().st_size / 1024 / 1024
        tables.append(t)
        files = ", ".join(s.name for s in sources)
        print(f"  {hackathon:<28} {t.num_rows:>6}  {size_mb:>6.1f}  {files}")

    combined = pa.concat_tables(tables)
    out = data_dir / "all" / "train.parquet"
    _write(combined, out)
    size_mb = out.stat().st_size / 1024 / 1024
    print(f"  {'all':<28} {combined.num_rows:>6}  {size_mb:>6.1f}  (default)")
    return len(tables)
