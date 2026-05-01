from __future__ import annotations

from pathlib import Path

import choix
import numpy as np
from rich.console import Console
from rich.table import Table

from devpost.pairs import _is_valid, _load_hf_projects, _project_id, iter_jsonl


def _build_outcomes(
    project_ids: list[str], judgments: list[dict]
) -> tuple[list[tuple[int, int]], dict[str, int], int]:
    """Convert judgments to choix's pairwise format: list of (winner, loser) idx tuples.

    Ties become one win each direction (no half-vote in `ilsr_pairwise`).
    """
    idx = {p: i for i, p in enumerate(project_ids)}
    outcomes: list[tuple[int, int]] = []
    invalid = 0
    for j in judgments:
        v = j["verdict"]
        if v == "invalid":
            invalid += 1
            continue
        a, b = j["project_a_id"], j["project_b_id"]
        if a not in idx or b not in idx:
            continue
        i, k = idx[a], idx[b]
        if v == "A":
            outcomes.append((i, k))
        elif v == "B":
            outcomes.append((k, i))
        elif v == "tie":
            outcomes.append((i, k))
            outcomes.append((k, i))
    return outcomes, idx, invalid


def run(
    config: str,
    judgments_path: Path,
    ks: list[int],
    top: int = 20,
) -> None:
    console = Console()

    projects = [p for p in _load_hf_projects(config) if _is_valid(p)]
    project_ids = [_project_id(p) for p in projects]
    winner_ids = {pid for pid, p in zip(project_ids, projects) if p.get("is_winner")}

    judgments = list(iter_jsonl(judgments_path))
    if not judgments:
        raise SystemExit(f"no judgments in {judgments_path}")

    outcomes, idx, n_invalid = _build_outcomes(project_ids, judgments)
    n = len(project_ids)

    n_wins = np.zeros(n)
    n_losses = np.zeros(n)
    for w, l in outcomes:
        n_wins[w] += 1
        n_losses[l] += 1
    pairs_per = n_wins + n_losses
    appeared = pairs_per > 0
    n_appeared = int(appeared.sum())

    # alpha regularizes sparse/disconnected pair graphs; returns log-scale skill
    log_skill = choix.ilsr_pairwise(n, outcomes, alpha=0.01)

    appeared_ids = [pid for pid, i in idx.items() if appeared[i]]
    appeared_ids.sort(key=lambda pid: -log_skill[idx[pid]])
    rank_of = {pid: r for r, pid in enumerate(appeared_ids)}

    appeared_winners = [w for w in winner_ids if w in rank_of]
    n_winners = len(winner_ids)
    n_winners_appeared = len(appeared_winners)
    winner_pcts = [rank_of[w] / max(n_appeared, 1) for w in appeared_winners]

    # ── header ──
    console.print(
        f"[bold]{config}[/]  "
        f"{n_appeared}/{n} projects ranked  ·  "
        f"{len(judgments)} judgments  ·  "
        f"[yellow]{n_invalid}[/] invalid"
    )
    if n_winners:
        console.print(
            f"  winners: {n_winners_appeared}/{n_winners}  ·  "
            f"percentile: median=[cyan]{np.median(winner_pcts):.3f}[/] "
            f"mean=[cyan]{np.mean(winner_pcts):.3f}[/]"
        )

    # ── recall@K ──
    if n_winners and n > 0:
        rec_table = Table(title="Recall@K", title_justify="left", show_header=True)
        rec_table.add_column("K", justify="right")
        rec_table.add_column("recall", justify="right")
        rec_table.add_column("random", justify="right")
        rec_table.add_column("lift", justify="right")
        for k in ks:
            top_k = set(appeared_ids[:k])
            hits = sum(1 for w in appeared_winners if w in top_k)
            rec = hits / n_winners
            rand = k / n
            lift = rec / rand if rand > 0 else float("inf")
            color = "green" if lift > 1 else "red"
            rec_table.add_row(
                str(k),
                f"[{color}]{rec:.3f}[/]",
                f"{rand:.3f}",
                f"[{color}]{lift:.2f}×[/]",
            )
        console.print(rec_table)

    # ── top N ──
    top_table = Table(
        title=f"Top {top} (by BT score)", title_justify="left", show_header=True
    )
    top_table.add_column("rank", justify="right")
    top_table.add_column("title", overflow="ellipsis", max_width=40)
    top_table.add_column("score", justify="right")
    top_table.add_column("appearances", justify="right")
    top_table.add_column("W", justify="center")
    top_table.add_column("result", overflow="ellipsis", max_width=40)
    for r, pid in enumerate(appeared_ids[:top]):
        i = idx[pid]
        p = projects[i]
        winner_mark = "[bold green]✓[/]" if p.get("is_winner") else ""
        top_table.add_row(
            str(r),
            p.get("title") or "",
            f"{float(np.exp(log_skill[i])):.2f}",
            str(int(pairs_per[i])),
            winner_mark,
            p.get("results") or "",
        )
    console.print(top_table)