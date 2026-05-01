"""Cross-hackathon eval — the headline 'how often did we pick the winner' number.

Loops over every `data/<hackathon>/judgments.jsonl` it finds, fits BT, and
prints one row per hackathon plus the aggregate top-1 hit rate.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from rich.console import Console
from rich.table import Table

from devpost import rank as rank_mod

JUDGMENTS_SRC = Path("data")


def run(ks: list[int]) -> None:
    console = Console()
    sources = sorted(JUDGMENTS_SRC.glob("*/judgments.jsonl"))
    if not sources:
        raise SystemExit(f"no judgments.jsonl under {JUDGMENTS_SRC}/*/")

    results: list[rank_mod.RankResult] = []
    for src in sources:
        h = src.parent.name
        results.append(rank_mod.compute(h, src, ks))

    # ── per-hackathon table ──
    table = Table(
        title=f"Cross-hackathon eval ({len(results)} hackathons)",
        title_justify="left",
        show_header=True,
    )
    table.add_column("hackathon")
    table.add_column("N", justify="right")
    table.add_column("W", justify="right")
    table.add_column("top-1 BT pick", overflow="ellipsis", max_width=36)
    table.add_column("hit", justify="center")
    table.add_column("recall@1", justify="right")
    table.add_column("recall@10", justify="right")
    table.add_column("median pct", justify="right")

    for r in results:
        hit_str = "[green]✓[/]" if r.top1_hit else "[red]✗[/]"
        title = r.top1_project.get("title") if r.top1_project else "—"
        pct = np.median(r.winner_pcts) if r.winner_pcts else float("nan")
        table.add_row(
            r.config,
            str(r.n_projects),
            str(r.n_winners),
            title or "",
            hit_str,
            f"{r.recall_at_k.get(1, 0):.3f}",
            f"{r.recall_at_k.get(10, 0):.3f}",
            f"{pct:.3f}" if not np.isnan(pct) else "—",
        )
    console.print(table)

    # ── aggregate ──
    n_hackathons = len(results)
    n_hit = sum(1 for r in results if r.top1_hit)
    hit_rate = n_hit / n_hackathons if n_hackathons else 0.0
    mean_recall = {k: float(np.mean([r.recall_at_k.get(k, 0) for r in results])) for k in ks}

    console.print()
    console.print(
        f"[bold]Top-1 hit rate:[/] [green]{n_hit}/{n_hackathons}[/] hackathons "
        f"= [bold green]{hit_rate:.1%}[/]"
    )
    console.print("  Mean recall across hackathons:")
    for k in ks:
        console.print(f"    @{k}: [cyan]{mean_recall[k]:.3f}[/]")