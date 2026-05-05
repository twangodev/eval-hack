from __future__ import annotations

import os

# Set before numpy is imported by workers (fork inherits, but spawn re-reads env)
for _var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_var, "1")

import random
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
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


@dataclass
class RankResult:
    config: str
    n_projects: int
    n_appeared: int
    n_winners: int
    n_winners_appeared: int
    n_judgments: int
    n_invalid: int
    log_skill: np.ndarray
    pairs_per: np.ndarray
    projects: list[dict]
    idx: dict[str, int]
    appeared_ids: list[str]
    rank_of: dict[str, int]
    winner_ids: set[str]
    winner_pcts: list[float]
    recall_at_k: dict[int, float]
    top1_id: str | None
    top1_project: dict | None
    top1_hit: bool


def _fit_and_rank(
    config: str,
    projects: list[dict],
    project_ids: list[str],
    winner_ids: set[str],
    judgments: list[dict],
    ks: list[int],
) -> RankResult:
    """Pure: build outcomes, fit BT, compute metrics. Used by both `compute` and bootstrap."""
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
    winner_pcts = [rank_of[w] / max(n_appeared, 1) for w in appeared_winners]

    recall_at_k: dict[int, float] = {}
    for k in ks:
        top_k = set(appeared_ids[:k])
        hits = sum(1 for w in appeared_winners if w in top_k)
        recall_at_k[k] = hits / max(n_winners, 1)

    top1_id = appeared_ids[0] if appeared_ids else None
    return RankResult(
        config=config,
        n_projects=n,
        n_appeared=n_appeared,
        n_winners=n_winners,
        n_winners_appeared=len(appeared_winners),
        n_judgments=len(judgments),
        n_invalid=n_invalid,
        log_skill=log_skill,
        pairs_per=pairs_per,
        projects=projects,
        idx=idx,
        appeared_ids=appeared_ids,
        rank_of=rank_of,
        winner_ids=winner_ids,
        winner_pcts=winner_pcts,
        recall_at_k=recall_at_k,
        top1_id=top1_id,
        top1_project=projects[idx[top1_id]] if top1_id else None,
        top1_hit=top1_id in winner_ids if top1_id else False,
    )


def compute(
    config: str,
    judgments_path: Path,
    ks: list[int],
    pair_id_filter: set[str] | None = None,
) -> RankResult:
    """Load + fit BT + compute metrics for one (hackathon, judgments-file) pair.

    `pair_id_filter`, if provided, restricts judgments to those pair_ids.
    """
    projects = [p for p in _load_hf_projects(config) if _is_valid(p)]
    project_ids = [_project_id(p) for p in projects]
    winner_ids = {pid for pid, p in zip(project_ids, projects) if p.get("is_winner")}

    judgments = list(iter_jsonl(judgments_path))
    if pair_id_filter is not None:
        judgments = [j for j in judgments if j["pair_id"] in pair_id_filter]
    if not judgments:
        raise SystemExit(f"no judgments in {judgments_path}")

    return _fit_and_rank(config, projects, project_ids, winner_ids, judgments, ks)


# ── bootstrap ──────────────────────────────────────────────────────────────

_BOOT: dict = {}  # state shared with worker processes via fork


def _bootstrap_iter(seed: int) -> dict | None:
    s = _BOOT
    rng = random.Random(seed)
    sampled = [rng.choice(s["pair_ids"]) for _ in range(len(s["pair_ids"]))]
    judgments = [j for pid in sampled for j in s["judgments_by_pair"][pid]]

    r = _fit_and_rank(
        s["config"], s["projects"], s["project_ids"], s["winner_ids"], judgments, s["ks"]
    )
    return {
        "top1_hit": r.top1_hit,
        "median_pct": (
            float(np.median(r.winner_pcts)) if r.winner_pcts else float("nan")
        ),
        **{f"r{k}": v for k, v in r.recall_at_k.items()},
    }


def _ci(values: list[float]) -> dict:
    arr = np.asarray(values, dtype=float)
    arr = arr[~np.isnan(arr)]
    if len(arr) == 0:
        return {"mean": float("nan"), "lo": float("nan"), "hi": float("nan")}
    return {
        "mean": float(arr.mean()),
        "lo": float(np.percentile(arr, 2.5)),
        "hi": float(np.percentile(arr, 97.5)),
    }


def bootstrap(
    config: str,
    judgments_path: Path,
    ks: list[int],
    B: int = 1000,
    workers: int = 24,
    base_seed: int = 42,
    pair_id_filter: set[str] | None = None,
) -> dict | None:
    """B iterations of pair-resampling → BT refit → metrics. Returns 95% CIs."""
    projects = [p for p in _load_hf_projects(config) if _is_valid(p)]
    project_ids = [_project_id(p) for p in projects]
    winner_ids = {pid for pid, p in zip(project_ids, projects) if p.get("is_winner")}

    judgments = list(iter_jsonl(judgments_path))
    if pair_id_filter is not None:
        judgments = [j for j in judgments if j["pair_id"] in pair_id_filter]
    if not judgments:
        return None

    by_pair: dict[str, list[dict]] = defaultdict(list)
    for j in judgments:
        by_pair[j["pair_id"]].append(j)

    _BOOT.update(
        config=config,
        projects=projects,
        project_ids=project_ids,
        winner_ids=winner_ids,
        judgments_by_pair=dict(by_pair),
        pair_ids=list(by_pair.keys()),
        ks=ks,
    )

    seeds = list(range(base_seed, base_seed + B))
    if workers <= 1:
        results = [_bootstrap_iter(s) for s in seeds]
    else:
        chunksize = max(1, B // (workers * 4))
        with ProcessPoolExecutor(max_workers=workers) as ex:
            results = list(ex.map(_bootstrap_iter, seeds, chunksize=chunksize))
    results = [r for r in results if r is not None]

    return {
        "B": B,
        "n_judgments": len(judgments),
        "n_projects": len(projects),
        "n_winners": len(winner_ids),
        "model": judgments[0].get("model") if judgments else None,
        "top1_hit_rate": float(np.mean([r["top1_hit"] for r in results])),
        "recall": {k: _ci([r[f"r{k}"] for r in results]) for k in ks},
        "median_pct": _ci([r["median_pct"] for r in results]),
    }


# ── single-hackathon CLI render ────────────────────────────────────────────


def run(
    config: str,
    judgments_path: Path,
    ks: list[int],
    top: int | None = None,
) -> None:
    console = Console()
    r = compute(config, judgments_path, ks)

    # header
    console.print(
        f"[bold]{r.config}[/]  "
        f"{r.n_appeared}/{r.n_projects} projects ranked  ·  "
        f"{r.n_judgments} judgments  ·  "
        f"[yellow]{r.n_invalid}[/] invalid"
    )
    if r.n_winners:
        console.print(
            f"  winners: {r.n_winners_appeared}/{r.n_winners}  ·  "
            f"percentile: median=[cyan]{np.median(r.winner_pcts):.3f}[/] "
            f"mean=[cyan]{np.mean(r.winner_pcts):.3f}[/]"
        )

    # recall@K
    if r.n_winners and r.n_projects > 0:
        rec_table = Table(title="Recall@K", title_justify="left", show_header=True)
        rec_table.add_column("K", justify="right")
        rec_table.add_column("recall", justify="right")
        rec_table.add_column("random", justify="right")
        rec_table.add_column("lift", justify="right")
        for k in ks:
            rec = r.recall_at_k[k]
            rand = k / r.n_projects
            lift = rec / rand if rand > 0 else float("inf")
            color = "green" if lift > 1 else "red"
            rec_table.add_row(
                str(k),
                f"[{color}]{rec:.3f}[/]",
                f"{rand:.3f}",
                f"[{color}]{lift:.2f}×[/]",
            )
        console.print(rec_table)

    # ranking
    n_show = top if top is not None else len(r.appeared_ids)
    title = (
        f"Top {n_show} (by BT score)"
        if top is not None
        else f"All {n_show} ranked projects (by BT score)"
    )
    top_table = Table(title=title, title_justify="left", show_header=True)
    top_table.add_column("rank", justify="right")
    top_table.add_column("title", overflow="ellipsis", max_width=40)
    top_table.add_column("score", justify="right")
    top_table.add_column("appearances", justify="right")
    top_table.add_column("W", justify="center")
    top_table.add_column("result", overflow="ellipsis", max_width=40)
    for rk, pid in enumerate(r.appeared_ids[:n_show]):
        i = r.idx[pid]
        p = r.projects[i]
        winner_mark = "[bold green]✓[/]" if p.get("is_winner") else ""
        top_table.add_row(
            str(rk),
            p.get("title") or "",
            f"{float(np.exp(r.log_skill[i])):.2f}",
            str(int(r.pairs_per[i])),
            winner_mark,
            p.get("results") or "",
        )
    console.print(top_table)
