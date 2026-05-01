from __future__ import annotations

import json
from pathlib import Path

import choix
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

from devpost.pairs import _is_valid, _load_hf_projects, _project_id, iter_jsonl


def _build_outcomes(
    project_ids: list[str], judgments: list[dict]
) -> tuple[list[tuple[int, int]], dict[str, int], int]:
    """Convert judgments to choix's pairwise format: list of (winner, loser) idx tuples.

    Ties are split as one win each direction (a half-vote isn't supported by
    `ilsr_pairwise`, so we encode each tie as one outcome each way).
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
    out_dir: Path,
    ks: list[int],
) -> dict:
    projects = [p for p in _load_hf_projects(config) if _is_valid(p)]
    project_ids = [_project_id(p) for p in projects]
    winner_ids = [pid for pid, p in zip(project_ids, projects) if p.get("is_winner")]

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
    scores = np.exp(log_skill)

    appeared_ids = [pid for pid, i in idx.items() if appeared[i]]
    appeared_ids.sort(key=lambda pid: -log_skill[idx[pid]])
    rank_of = {pid: r for r, pid in enumerate(appeared_ids)}

    rows: list[dict] = []
    for pid, p in zip(project_ids, projects):
        i = idx[pid]
        rows.append(
            {
                "project_id": pid,
                "title": p.get("title"),
                "url": p.get("url"),
                "bt_score": float(scores[i]),
                "log_skill": float(log_skill[i]),
                "rank": rank_of.get(pid),
                "rank_percentile": (
                    None if pid not in rank_of else rank_of[pid] / max(n_appeared, 1)
                ),
                "n_appearances": int(pairs_per[i]),
                "n_wins": float(n_wins[i]),
                "n_losses": float(n_losses[i]),
                "is_winner": bool(p.get("is_winner")),
                "gt_result": p.get("results") or "Unknown",
            }
        )
    rows.sort(key=lambda r: (r["rank"] is None, r["rank"] if r["rank"] is not None else 0))

    out_dir.mkdir(parents=True, exist_ok=True)
    schema = pa.schema(
        [
            ("project_id", pa.string()),
            ("title", pa.string()),
            ("url", pa.string()),
            ("bt_score", pa.float64()),
            ("log_skill", pa.float64()),
            ("rank", pa.int64()),
            ("rank_percentile", pa.float64()),
            ("n_appearances", pa.int64()),
            ("n_wins", pa.float64()),
            ("n_losses", pa.float64()),
            ("is_winner", pa.bool_()),
            ("gt_result", pa.string()),
        ]
    )
    pq.write_table(
        pa.Table.from_pylist(rows, schema=schema),
        out_dir / "ranking.parquet",
        compression="zstd",
    )

    appeared_winners = [w for w in winner_ids if w in rank_of]
    n_winners = len(winner_ids)
    n_winners_appeared = len(appeared_winners)
    winner_ranks = [rank_of[w] for w in appeared_winners]
    winner_pcts = [r / max(n_appeared, 1) for r in winner_ranks]

    recall_at_k = {}
    for k in ks:
        if k <= 0:
            continue
        top_k = set(appeared_ids[:k])
        hits = sum(1 for w in appeared_winners if w in top_k)
        recall_at_k[str(k)] = hits / max(n_winners, 1)

    eval_summary = {
        "hackathon": config,
        "n_projects": len(projects),
        "n_projects_appeared": n_appeared,
        "n_winners": n_winners,
        "n_winners_appeared": n_winners_appeared,
        "n_judgments": len(judgments),
        "n_invalid": n_invalid,
        "recall_at_k": recall_at_k,
        "median_winner_rank_pct": (
            float(np.median(winner_pcts)) if winner_pcts else None
        ),
        "mean_winner_rank_pct": (
            float(np.mean(winner_pcts)) if winner_pcts else None
        ),
        "ks": ks,
    }
    (out_dir / "eval.json").write_text(json.dumps(eval_summary, indent=2) + "\n")

    return eval_summary