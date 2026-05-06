"""Madhacks-fall-2025 secondary eval: paired bootstrap of judges' BT rankings
against the human Plackett-Luce ranking from `madhacks/data/rank.csv`.

The anonymized→real-title map is private; expected at
`data/madhacks-fall-2025/real_names.csv` (gitignored). If absent, this eval
is silently skipped.
"""
from __future__ import annotations

import csv
import os
import random
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from itertools import combinations
from pathlib import Path

import numpy as np

from devpost import rank as rank_mod
from devpost.pairs import iter_jsonl

HACKATHON = "madhacks-fall-2025"
BALLOTS_CSV = Path("madhacks/data/rank.csv")
REAL_NAMES_CSV = Path(
    os.environ.get("DEVPOST_PL_REAL_NAMES_CSV", "data/madhacks-fall-2025/real_names.csv")
)
TITLE_ALIAS = {"Recipe Manager - MadHacks 2025": "Recipe Manager"}


def available() -> bool:
    return BALLOTS_CSV.exists() and REAL_NAMES_CSV.exists()


def _resolve(t: str) -> str:
    return TITLE_ALIAS.get(t, t)


def _pl_by_title() -> dict[str, float]:
    from madhacks.pl import _load, fit  # local import: pymc is heavy

    real_to_code = {
        row["Project"].strip(): row["Table"].strip()
        for row in csv.DictReader(REAL_NAMES_CSV.open())
    }
    ballots = _load(BALLOTS_CSV)
    teams, scores = fit(ballots)
    code_to_score = dict(zip(teams, scores))
    return {
        _resolve(title): code_to_score[code]
        for title, code in real_to_code.items()
        if code in code_to_score
    }


_BOOT: dict = {}


def _one_iter(seed: int) -> dict[str, float]:
    from scipy.stats import spearmanr

    s = _BOOT
    rng = random.Random(seed)
    pair_ids = s["pair_ids"]
    sampled = [rng.choice(pair_ids) for _ in range(len(pair_ids))]

    rhos: dict[str, float] = {}
    for model, by_pair in s["by_judge"].items():
        judgments = []
        for pid in sampled:
            judgments.extend(by_pair.get(pid, ()))
        if not judgments:
            rhos[model] = float("nan")
            continue
        r = rank_mod._fit_and_rank(
            HACKATHON, s["projects"], s["project_ids"],
            s["winner_ids"], judgments, [1],
        )
        bt_score = {}
        for pid in r.appeared_ids:
            i = r.idx[pid]
            bt_score[r.projects[i]["title"]] = r.log_skill[i]
        common = sorted(set(s["pl"]) & set(bt_score))
        if len(common) < 5:
            rhos[model] = float("nan")
            continue
        x = np.array([s["pl"][t] for t in common])
        y = np.array([bt_score[t] for t in common])
        rhos[model], _ = spearmanr(x, y)
    return rhos


def run(B: int = 1000, workers: int = 24, base_seed: int = 42) -> dict | None:
    """Returns {marginals: {model: (mean, lo, hi)}, pairwise: [(ja, jb, mean, lo, hi, p_pos)],
    arc: {ft_minus_base: (...), ft_minus_teacher: (...)}, n_projects, n_pairs}, or None
    if inputs unavailable."""
    if not available() or B <= 0:
        return None

    pl = _pl_by_title()
    projects = [p for p in rank_mod._load_hf_projects(HACKATHON) if rank_mod._is_valid(p)]
    project_ids = [rank_mod._project_id(p) for p in projects]
    winner_ids = {pid for pid, p in zip(project_ids, projects) if p.get("is_winner")}

    judgment_files = sorted(Path(f"data/{HACKATHON}").glob("judgments*.jsonl"))
    by_judge: dict[str, dict[str, list]] = {}
    for jf in judgment_files:
        rows = list(iter_jsonl(jf))
        if not rows:
            continue
        model = rows[0].get("model") or jf.name
        bp: dict[str, list] = defaultdict(list)
        for j in rows:
            bp[j["pair_id"]].append(j)
        by_judge[model] = dict(bp)

    if len(by_judge) < 1:
        return None

    pair_ids = sorted(set().union(*[set(bp) for bp in by_judge.values()]))

    _BOOT.update(
        projects=projects, project_ids=project_ids, winner_ids=winner_ids,
        by_judge=by_judge, pair_ids=pair_ids, pl=pl,
    )
    seeds = list(range(base_seed, base_seed + B))
    chunksize = max(1, B // (workers * 4))
    if workers <= 1:
        results = [_one_iter(s) for s in seeds]
    else:
        with ProcessPoolExecutor(max_workers=workers) as ex:
            results = list(ex.map(_one_iter, seeds, chunksize=chunksize))

    models = sorted(by_judge.keys())
    per_model = {m: np.array([r[m] for r in results], dtype=float) for m in models}

    def _ci(arr: np.ndarray) -> tuple[float, float, float]:
        a = arr[~np.isnan(arr)]
        if len(a) == 0:
            return float("nan"), float("nan"), float("nan")
        return float(a.mean()), float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5))

    marginals = {m: _ci(per_model[m]) for m in models}

    pairwise: list[tuple] = []
    for ja, jb in combinations(models, 2):
        diff = per_model[ja] - per_model[jb]
        diff = diff[~np.isnan(diff)]
        if len(diff) == 0:
            continue
        m, lo, hi = diff.mean(), np.percentile(diff, 2.5), np.percentile(diff, 97.5)
        pairwise.append((ja, jb, float(m), float(lo), float(hi), float((diff > 0).mean())))

    # Distillation arc (FT vs base, FT vs teacher)
    arc: dict[str, tuple] = {}
    ft = "twangodev/devpost-hacks-qwen3-4b-judge"
    base = "Qwen/Qwen3-4B-Instruct-2507"
    teacher = "Qwen/Qwen3.5-27B"
    if all(m in per_model for m in (ft, base, teacher)):
        for label, key, ref in [
            ("ft_minus_base", ft, base),
            ("ft_minus_teacher", ft, teacher),
        ]:
            d = per_model[key] - per_model[ref]
            d = d[~np.isnan(d)]
            arc[label] = (float(d.mean()),
                          float(np.percentile(d, 2.5)),
                          float(np.percentile(d, 97.5)),
                          float((d > 0).mean()))

    return {
        "marginals": marginals,
        "pairwise": pairwise,
        "arc": arc,
        "n_projects": len(pl),
        "n_pairs": len(pair_ids),
        "B": B,
    }


def top_n_rankings(n: int = 15) -> dict | None:
    """Returns side-by-side ranking data: human PL top-N + each judge's BT top-N."""
    if not available():
        return None
    pl = _pl_by_title()
    pl_sorted = sorted(pl, key=lambda t: -pl[t])
    pl_top10 = set(pl_sorted[:10])

    judgment_files = sorted(Path(f"data/{HACKATHON}").glob("judgments*.jsonl"))
    rankings: list[tuple[str, list[tuple[str, float, bool]]]] = []
    for jf in judgment_files:
        rows = list(iter_jsonl(jf))
        if not rows:
            continue
        model = rows[0].get("model") or jf.name
        r = rank_mod.compute(HACKATHON, jf, ks=[1])
        ranking: list[tuple[str, float, bool]] = []
        for pid in r.appeared_ids[:n]:
            i = r.idx[pid]
            p = r.projects[i]
            ranking.append((p["title"], r.log_skill[i], bool(p.get("is_winner"))))
        rankings.append((model, ranking))

    return {
        "n": n,
        "pl_top": pl_sorted[:n],
        "pl_top10": pl_top10,
        "rankings": rankings,
    }
