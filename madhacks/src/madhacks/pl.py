"""Bayesian Plackett–Luce ranking from a ranked-choice CSV.

Each row is one judge's ballot: Judge, R1, R2, ..., Rk (R1 best).
Empty cells and "NA" are treated as no preference and truncate the ballot.
"""
from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import pymc as pm


def _load(rank_csv: Path) -> list[list[str]]:
    df = pd.read_csv(rank_csv, keep_default_na=False, dtype=str)
    ballots: list[list[str]] = []
    for _, row in df.iterrows():
        prefs = [v.strip() for v in row.iloc[1:].tolist() if v.strip() and v.strip() != "NA"]
        if len(prefs) >= 2:
            ballots.append(prefs)
    return ballots


def fit(ballots: list[list[str]]) -> tuple[list[str], np.ndarray]:
    teams = sorted({t for b in ballots for t in b})
    idx = {t: i for i, t in enumerate(teams)}
    n = len(teams)

    by_len: dict[int, list[list[int]]] = defaultdict(list)
    for b in ballots:
        by_len[len(b)].append([idx[t] for t in b])

    with pm.Model():
        sigma = pm.HalfNormal("sigma", 1.0)
        s_raw = pm.Normal("s_raw", 0.0, 1.0, shape=n)
        s = pm.Deterministic("s", s_raw * sigma)

        ll = 0.0
        for L, group in by_len.items():
            R = np.array(group)  # (J, L)
            for pos in range(L - 1):
                chosen = s[R[:, pos]]
                remaining = s[R[:, pos:]]
                ll = ll + pm.math.sum(chosen - pm.math.logsumexp(remaining, axis=1))
        pm.Potential("pl_lik", ll)

        m = pm.find_MAP(progressbar=True)

    return teams, np.asarray(m["s"])


DEFAULT_RANK_CSV = Path(__file__).resolve().parents[2] / "data" / "rank.csv"


def main() -> None:
    p = argparse.ArgumentParser(description="Bayesian Plackett–Luce ranking from ranked ballots.")
    p.add_argument(
        "rank_csv",
        type=Path,
        nargs="?",
        default=DEFAULT_RANK_CSV,
        help=f"CSV: Judge, R1, R2, ... (default: {DEFAULT_RANK_CSV})",
    )
    p.add_argument("-k", "--top", type=int, default=20, help="rows to print (default: 20)")
    args = p.parse_args()

    names_path = args.rank_csv.parent / "project_numbers.csv"
    names: dict[str, str] = {}
    if names_path.exists():
        with names_path.open() as f:
            for row in csv.DictReader(f):
                names[row["Table"]] = row["Project"]

    ballots = _load(args.rank_csv)
    teams, scores = fit(ballots)

    order = np.argsort(scores)[::-1]
    print(f"{len(ballots)} ballots, {len(teams)} candidates\n")
    print(f"{'#':>3}  {'code':<8}  {'score':>7}  project")
    print("-" * 70)
    for rk, i in enumerate(order[: args.top], 1):
        print(f"{rk:>3}  {teams[i]:<8}  {scores[i]:+7.3f}  {names.get(teams[i], '')}")


if __name__ == "__main__":
    main()
