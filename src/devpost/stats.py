"""Dataset-description tables for the LLM-judge corpus.

Reads raw judgments from `data/<h>/judgments*.jsonl` and prints:
- rows per (model × hackathon)
- verdict distribution per judge (A/B/tie/invalid)
- position consistency (A/B vs B/A picks the same project)
- latency + completion-token stats per judge
"""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path

import numpy as np
from rich.console import Console
from rich.table import Table

from devpost.pairs import iter_jsonl

JUDGMENTS_SRC = Path("data")


def run() -> None:
    console = Console()
    sources = sorted(JUDGMENTS_SRC.glob("*/judgments*.jsonl"))
    if not sources:
        raise SystemExit(f"no judgments*.jsonl under {JUDGMENTS_SRC}/*/")

    by_model: dict[str, dict] = defaultdict(
        lambda: {
            "rows": defaultdict(int),
            "verdicts": defaultdict(int),
            "pairs": defaultdict(dict),
            "latencies": [],
            "completion_tokens": [],
            "finish_reasons": defaultdict(int),
        }
    )

    for path in sources:
        hackathon = path.parent.name
        for r in iter_jsonl(path):
            model = r.get("model") or "—"
            d = by_model[model]
            d["rows"][hackathon] += 1
            d["verdicts"][r["verdict"]] += 1
            v = r["verdict"]
            w = (
                r["project_a_id"] if v == "A"
                else r["project_b_id"] if v == "B"
                else v
            )
            d["pairs"][r["pair_id"]][r["position"]] = w
            if r.get("latency_s") is not None:
                d["latencies"].append(r["latency_s"])
            if r.get("completion_tokens") is not None:
                d["completion_tokens"].append(r["completion_tokens"])
            d["finish_reasons"][r.get("finish_reason") or "—"] += 1

    all_hacks = sorted({h for d in by_model.values() for h in d["rows"]})

    # ── rows per (model × hackathon) ──
    t1 = Table(title="Rows per (model × hackathon)", title_justify="left", show_header=True)
    t1.add_column("model", overflow="ellipsis", max_width=42)
    for h in all_hacks:
        t1.add_column(h, justify="right")
    t1.add_column("TOTAL", justify="right")
    for model, d in sorted(by_model.items()):
        cells = [f"{d['rows'][h]:,}" if d["rows"][h] else "—" for h in all_hacks]
        total = sum(d["rows"].values())
        t1.add_row(model, *cells, f"[bold]{total:,}[/]")
    console.print(t1)
    console.print()

    # ── verdict distribution ──
    t2 = Table(title="Verdict distribution per judge", title_justify="left", show_header=True)
    t2.add_column("model", overflow="ellipsis", max_width=42)
    for col in ("A", "B", "tie", "invalid", "A%", "B%", "tie%", "inv%"):
        t2.add_column(col, justify="right")
    for model, d in sorted(by_model.items()):
        v = d["verdicts"]
        n = sum(v.values())
        a, b, tie, inv = v.get("A", 0), v.get("B", 0), v.get("tie", 0), v.get("invalid", 0)
        t2.add_row(
            model, f"{a:,}", f"{b:,}", f"{tie:,}", f"{inv:,}",
            f"{a/n:.1%}" if n else "—",
            f"{b/n:.1%}" if n else "—",
            f"{tie/n:.1%}" if n else "—",
            f"{inv/n:.1%}" if n else "—",
        )
    console.print(t2)
    console.print()

    # ── position consistency ──
    t3 = Table(
        title="Position consistency (A/B vs B/A picks same project)",
        title_justify="left", show_header=True,
    )
    t3.add_column("model", overflow="ellipsis", max_width=42)
    for col in ("pairs", "agree", "flip", "inv-1", "inv-2", "consistency", "flip rate"):
        t3.add_column(col, justify="right")
    pc_rows = []
    for model, d in sorted(by_model.items()):
        agree = flip = inv1 = inv2 = 0
        for sides in d["pairs"].values():
            a, b = sides.get("ab"), sides.get("ba")
            if a is None or b is None:
                continue
            if a in ("invalid", "tie") or b in ("invalid", "tie"):
                inv2 += int(a == "invalid" and b == "invalid")
                inv1 += int(not (a == "invalid" and b == "invalid"))
            elif a == b:
                agree += 1
            else:
                flip += 1
        denom = agree + flip
        pc_rows.append((
            model, agree + flip + inv1 + inv2,
            agree, flip, inv1, inv2,
            agree / max(denom, 1), flip / max(denom, 1),
        ))
    pc_rows.sort(key=lambda r: -r[6])
    for model, n, agree, flip, i1, i2, c, fr in pc_rows:
        t3.add_row(
            model, f"{n:,}", f"{agree:,}", f"{flip:,}", f"{i1:,}", f"{i2:,}",
            f"{c:.1%}", f"{fr:.1%}",
        )
    console.print(t3)
    console.print()

    # ── latency + tokens ──
    t4 = Table(
        title="Latency + token stats per judge", title_justify="left", show_header=True,
    )
    t4.add_column("model", overflow="ellipsis", max_width=42)
    for col in ("n", "median compl tok", "p95 compl tok", "median lat s", "p95 lat s", "truncated %"):
        t4.add_column(col, justify="right")
    for model, d in sorted(by_model.items()):
        n = sum(d["rows"].values())
        toks = d["completion_tokens"]
        lats = d["latencies"]
        trunc = d["finish_reasons"].get("length", 0) / max(n, 1)
        t4.add_row(
            model, f"{n:,}",
            f"{int(np.median(toks)):,}" if toks else "—",
            f"{int(np.quantile(toks, 0.95)):,}" if toks else "—",
            f"{np.median(lats):.1f}" if lats else "—",
            f"{np.quantile(lats, 0.95):.1f}" if lats else "—",
            f"{trunc:.2%}",
        )
    console.print(t4)
