"""Cross-hackathon, cross-judge eval with bootstrap CIs.

Globs every `data/<hackathon>/judgments*.jsonl`, groups by hackathon, and runs
the BT pipeline once per file. Each file's `model` field disambiguates the
judge (e.g. `Qwen/Qwen3.5-27B` vs `Qwen/Qwen3.5-4B`).

By default restricts judgments to the held-out test set used by
`twangodev/devpost-hacks-qwen3-4b-judge` (cs639's seed=42 80/20 pair-level split
of position-consistent Qwen3.5-27B verdicts) so the FT judge is evaluated on
pairs it never saw during training. Pass `full=True` to skip that filter.
"""

from __future__ import annotations

import json
import random
import re
import time
from pathlib import Path

import numpy as np
from rich.console import Console
from rich.table import Table

from devpost import rank as rank_mod

JUDGMENTS_SRC = Path("data")
HF_JUDGMENTS_REPO = "twangodev/devpost-hacks-judgments"
TEACHER_MODEL = "Qwen/Qwen3.5-27B"
SPLIT_SEED = 42
TEST_SIZE = 0.2
_VERDICT_RE = re.compile(r"VERDICT:\s*(A|B|tie|invalid)", re.IGNORECASE)


def _testset_pair_ids() -> set[str]:
    """Reproduce cs639's pair-level 80/20 split → return the held-out 20% pair_ids.

    Mirrors `hackathon_judge_ft.data.split` so the held-out pairs match those
    held out from the FT model's training run (seed=42, 27B-judged,
    position-consistent only).
    """
    from datasets import load_dataset

    ds = load_dataset(HF_JUDGMENTS_REPO, "all")["train"].filter(
        lambda r: r["model"] == TEACHER_MODEL
    )
    winners: dict[str, dict[str, str]] = {}
    for row in ds:
        if row["verdict"] not in ("A", "B"):
            continue
        if _VERDICT_RE.search(row["messages"][2]["content"]) is None:
            continue
        w = row["project_a_id"] if row["verdict"] == "A" else row["project_b_id"]
        winners.setdefault(row["pair_id"], {})[row["position"]] = w
    consistent = sorted(
        pid
        for pid, sides in winners.items()
        if sides.get("ab") and sides.get("ab") == sides.get("ba")
    )
    random.Random(SPLIT_SEED).shuffle(consistent)
    n_test = int(len(consistent) * TEST_SIZE)
    return set(consistent[:n_test])


def _judge_name(path: Path) -> str:
    with path.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            return json.loads(line).get("model") or path.name
    return path.name


def _fmt_ci(d: dict, fmt: str = ".3f") -> str:
    if d is None or np.isnan(d.get("mean", float("nan"))):
        return "—"
    return f"{d['mean']:{fmt}} [{d['lo']:{fmt}}–{d['hi']:{fmt}}]"


def run(ks: list[int], B: int = 1000, workers: int = 24, full: bool = False) -> None:
    console = Console()
    sources = sorted(JUDGMENTS_SRC.glob("*/judgments*.jsonl"))
    if not sources:
        raise SystemExit(f"no judgments*.jsonl under {JUDGMENTS_SRC}/*/")

    if full:
        pair_filter: set[str] | None = None
        scope_label = "[yellow]all pairs (train + test)[/]"
    else:
        console.print("[dim]Loading held-out test pair_ids (cs639 split, seed=42)...[/]")
        pair_filter = _testset_pair_ids()
        scope_label = f"held-out test set ({len(pair_filter)} pair_ids)"

    by_hack: dict[str, list[tuple[str, Path]]] = {}
    for p in sources:
        by_hack.setdefault(p.parent.name, []).append((_judge_name(p), p))

    console.print(
        f"[dim]Eval scope: {scope_label}  ·  "
        f"{sum(len(v) for v in by_hack.values())} (hackathon × judge) combos  ·  "
        f"B={B}  ·  workers={workers}[/]"
    )
    console.print()

    t0 = time.time()
    rows: list[dict] = []
    for hackathon, runs in sorted(by_hack.items()):
        for model, path in sorted(runs):
            point = rank_mod.compute(hackathon, path, ks, pair_id_filter=pair_filter)
            boot = (
                rank_mod.bootstrap(
                    hackathon, path, ks, B=B, workers=workers, pair_id_filter=pair_filter
                )
                if B > 0
                else None
            )
            rows.append({"hackathon": hackathon, "model": model, "point": point, "boot": boot})

    elapsed = time.time() - t0
    console.print(f"[dim]({elapsed:.1f}s)[/]")
    console.print()

    # ── per-hackathon table ──
    table = Table(title=f"Per (hackathon × judge) — point estimate + 95% bootstrap CI",
                  title_justify="left", show_header=True)
    table.add_column("hackathon")
    table.add_column("model", overflow="ellipsis", max_width=22)
    table.add_column("top-1", justify="center")
    table.add_column("recall@1 [95% CI]", justify="right")
    table.add_column("recall@10 [95% CI]", justify="right")
    table.add_column("median pct [95% CI]", justify="right")

    for r in rows:
        p = r["point"]
        b = r["boot"]
        hit = "[green]✓[/]" if p.top1_hit else "[red]✗[/]"
        if b is not None:
            hit_str = f"{hit} ({b['top1_hit_rate']:.0%})"
            r1 = _fmt_ci(b["recall"].get(1))
            r10 = _fmt_ci(b["recall"].get(10))
            mp = _fmt_ci(b["median_pct"])
        else:
            hit_str = hit
            r1 = f"{p.recall_at_k.get(1, 0):.3f}"
            r10 = f"{p.recall_at_k.get(10, 0):.3f}"
            pct = float(np.median(p.winner_pcts)) if p.winner_pcts else float("nan")
            mp = "—" if np.isnan(pct) else f"{pct:.3f}"
        table.add_row(r["hackathon"], r["model"] or "—", hit_str, r1, r10, mp)
    console.print(table)
    console.print()

    # ── per-judge aggregate ──
    by_model: dict[str, list[dict]] = {}
    for r in rows:
        by_model.setdefault(r["model"], []).append(r)

    agg = Table(
        title=f"Aggregate across {len(by_hack)} hackathons (paired by hackathon)",
        title_justify="left",
        show_header=True,
    )
    agg.add_column("model", overflow="ellipsis", max_width=24)
    agg.add_column("top-1 hit rate", justify="right")
    agg.add_column("mean recall@1", justify="right")
    agg.add_column("mean recall@10", justify="right")
    agg.add_column("mean recall@50", justify="right")

    for model, model_rows in sorted(by_model.items()):
        n = len(model_rows)
        n_hit = sum(int(r["point"].top1_hit) for r in model_rows)
        mean_r1 = np.mean([r["point"].recall_at_k.get(1, 0) for r in model_rows])
        mean_r10 = np.mean([r["point"].recall_at_k.get(10, 0) for r in model_rows])
        mean_r50 = np.mean([r["point"].recall_at_k.get(50, 0) for r in model_rows])
        agg.add_row(
            model or "—",
            f"{n_hit}/{n} = [bold]{n_hit / n:.1%}[/]",
            f"{mean_r1:.3f}",
            f"{mean_r10:.3f}",
            f"{mean_r50:.3f}",
        )
    console.print(agg)

    # ── inter-judge pairwise comparisons (Spearman ρ, Kendall τ, McNemar) ──
    models = sorted(by_model.keys())
    if len(models) >= 2:
        from itertools import combinations
        from math import comb
        from scipy.stats import kendalltau, spearmanr

        by_hm = {(r["hackathon"], r["model"]): r["point"] for r in rows}
        common_hacks = lambda a, b: sorted(  # noqa: E731
            {r["hackathon"] for r in by_model[a]} & {r["hackathon"] for r in by_model[b]}
        )

        pair_table = Table(
            title="Pairwise judge comparisons (median across shared hackathons)",
            title_justify="left",
            show_header=True,
        )
        pair_table.add_column("judge A", overflow="ellipsis", max_width=28)
        pair_table.add_column("judge B", overflow="ellipsis", max_width=28)
        pair_table.add_column("N hacks", justify="right")
        pair_table.add_column("median ρ", justify="right")
        pair_table.add_column("median τ", justify="right")
        pair_table.add_column("McNemar p", justify="right")
        pair_table.add_column("A-only / B-only", justify="right")

        for ja, jb in combinations(models, 2):
            shared = common_hacks(ja, jb)
            if not shared:
                continue
            rhos: list[float] = []
            taus: list[float] = []
            for hackathon in shared:
                ra = by_hm[(hackathon, ja)]
                rb = by_hm[(hackathon, jb)]
                common = sorted(set(ra.rank_of) & set(rb.rank_of))
                if len(common) < 3:
                    continue
                ranks_a = [ra.rank_of[pid] for pid in common]
                ranks_b = [rb.rank_of[pid] for pid in common]
                rhos.append(float(spearmanr(ranks_a, ranks_b)[0]))
                taus.append(float(kendalltau(ranks_a, ranks_b)[0]))

            a_hits = {r["hackathon"]: r["point"].top1_hit for r in by_model[ja]}
            b_hits = {r["hackathon"]: r["point"].top1_hit for r in by_model[jb]}
            a_only = sum(1 for h in shared if a_hits.get(h) and not b_hits.get(h))
            b_only = sum(1 for h in shared if not a_hits.get(h) and b_hits.get(h))
            n_disc = a_only + b_only
            if n_disc == 0:
                p_value = 1.0
            else:
                k = max(a_only, b_only)
                tail = sum(comb(n_disc, i) for i in range(k, n_disc + 1))
                p_value = min(1.0, 2 * tail / (2 ** n_disc))

            pair_table.add_row(
                ja,
                jb,
                str(len(shared)),
                f"{np.median(rhos):+.3f}" if rhos else "—",
                f"{np.median(taus):+.3f}" if taus else "—",
                "<0.001" if p_value < 0.001 else f"{p_value:.3f}",
                f"{a_only} / {b_only}",
            )

        console.print(pair_table)

    # ── madhacks PL secondary eval (if private real_names.csv present) ──
    from devpost import madhacks_eval

    if not madhacks_eval.available():
        console.print(
            f"\n[dim]Skipping madhacks PL eval — set "
            f"{madhacks_eval.REAL_NAMES_CSV} to enable.[/]"
        )
    else:
        console.print()
        console.print(
            f"[dim]Madhacks PL eval (paired bootstrap, B={B}, workers={workers})...[/]"
        )
        result = madhacks_eval.run(B=B, workers=workers)
        if result is None:
            console.print("[dim](skipped)[/]")
        else:
            pl_table = Table(
                title=(
                    f"Madhacks-fall-2025: judge BT vs human PL  "
                    f"(N={result['n_projects']} projects, {result['n_pairs']} pairs)"
                ),
                title_justify="left",
                show_header=True,
            )
            pl_table.add_column("model", overflow="ellipsis", max_width=42)
            pl_table.add_column("Spearman ρ [95% CI]", justify="right")
            for model, (m, lo, hi) in sorted(
                result["marginals"].items(), key=lambda kv: -kv[1][0]
            ):
                pl_table.add_row(model, f"{m:+.3f} [{lo:+.3f}, {hi:+.3f}]")
            console.print(pl_table)

            if result["arc"]:
                arc_table = Table(
                    title="Distillation arc (paired Δρ)",
                    title_justify="left", show_header=True,
                )
                arc_table.add_column("comparison")
                arc_table.add_column("Δρ [95% CI]", justify="right")
                arc_table.add_column("P(Δ>0)", justify="right")
                for label, (m, lo, hi, p) in result["arc"].items():
                    arc_table.add_row(
                        label.replace("_", " "),
                        f"{m:+.4f} [{lo:+.3f}, {hi:+.3f}]",
                        f"{p:.1%}",
                    )
                console.print(arc_table)