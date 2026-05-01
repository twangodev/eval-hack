from __future__ import annotations

from pathlib import Path

import typer

from devpost import pairs as pairs_mod

app = typer.Typer(
    no_args_is_help=True,
    add_completion=False,
    help="Pairwise LLM-judge dataset builder over hackathon projects.",
)


@app.command()
def enrich(
    source: Path = typer.Option(
        ..., "--source", "-s", help="Input projects JSON to enrich"
    ),
    out: Path = typer.Option(
        None,
        "--out",
        "-o",
        help="Output projects parquet (default: data/projects/<source.stem>.parquet)",
    ),
    workers: int = typer.Option(
        4, "--workers", "-w", help="Concurrent fetch threads"
    ),
) -> None:
    """Fetch GitHub READMEs for each project, write per-hackathon projects parquet."""
    from devpost import enrich as enrich_mod

    n_total, n_with_readme, n_readmes = enrich_mod.run(source, out, workers=workers)
    target = out or Path(f"data/projects/{source.stem}.parquet")
    typer.echo(
        f"enriched {n_total} projects → {target} "
        f"(readmes: {n_readmes} across {n_with_readme} projects)"
    )


@app.command()
def pairs(
    config: str = typer.Option(
        "all",
        "--config",
        "-c",
        help=(
            f"HuggingFace dataset config from {pairs_mod.HF_REPO} "
            "(`all` = global pool across hackathons, or a single-hackathon config like `treehacks-2026`)"
        ),
    ),
    out: Path = typer.Option(
        None,
        "--out",
        "-o",
        help="Output pairs manifest (default: data/{config}/pairs.jsonl)",
    ),
    n: int = typer.Option(500, "--n", help="Number of unordered pairs to sample"),
    seed: int = typer.Option(0, "--seed"),
) -> None:
    """Sample random pairs of projects and emit a manifest (both A/B orderings)."""
    out = out or Path(f"data/{config}/pairs.jsonl")
    written = pairs_mod.generate_pairs(out, n, seed, config)
    typer.echo(
        f"[{config}] wrote {written} rows to {out} (pairs sampled: {written // 2})"
    )


@app.command()
def judge(
    pairs_path: Path = typer.Option(
        ..., "--pairs", help="Pairs manifest from `devpost pairs`"
    ),
    out: Path = typer.Option(
        None,
        "--out",
        "-o",
        help="Output judgments JSONL (default: <pairs dir>/judgments.jsonl)",
    ),
    model: str = typer.Option("Qwen/Qwen3.5-27B", "--model"),
    base_url: str = typer.Option(
        "http://localhost:30000", "--base-url", help="SGLang OpenAI-compatible server"
    ),
    max_tokens: int = typer.Option(8192, "--max-tokens"),
    temperature: float = typer.Option(0.7, "--temperature"),
    top_p: float = typer.Option(0.9, "--top-p"),
    seed: int = typer.Option(0, "--seed"),
    limit: int = typer.Option(None, "--limit"),
    resume: bool = typer.Option(True, "--resume/--no-resume"),
    concurrency: int = typer.Option(32, "--concurrency"),
    wait_ready_s: float = typer.Option(
        600.0, "--wait-ready-s", help="Seconds to wait for server health"
    ),
) -> None:
    """Run the SGLang HTTP judge over the pairs manifest, append to judgments JSONL."""
    from devpost import judge as judge_mod

    out = out or pairs_path.parent / "judgments.jsonl"
    written = judge_mod.run(
        pairs_path=pairs_path,
        out=out,
        model=model,
        base_url=base_url,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
        seed=seed,
        limit=limit,
        resume=resume,
        concurrency=concurrency,
        wait_ready_s=wait_ready_s,
    )
    typer.echo(f"wrote {written} new judgments to {out}")


@app.command()
def rank(
    config: str = typer.Option(
        "all",
        "--config",
        "-c",
        help=f"HuggingFace dataset config from {pairs_mod.HF_REPO} (matches the one passed to `pairs`)",
    ),
    judgments: Path = typer.Option(
        None, "--judgments", help="Judgments JSONL (default: data/{config}/judgments.jsonl)"
    ),
    out_dir: Path = typer.Option(
        None, "--out-dir", "-o", help="Output dir (default: data/{config}/)"
    ),
    ks: list[int] = typer.Option(
        [10, 20, 50], "--k", help="K values for recall@K (repeatable)"
    ),
) -> None:
    """Fit Bradley-Terry on judgments → ranking.parquet + eval.json."""
    from devpost import rank as rank_mod

    judgments = judgments or Path(f"data/{config}/judgments.jsonl")
    out_dir = out_dir or Path(f"data/{config}/")
    summary = rank_mod.run(config, judgments, out_dir, ks)
    typer.echo(
        f"[{config}] {summary['n_projects_appeared']}/{summary['n_projects']} projects ranked, "
        f"{summary['n_judgments']} judgments ({summary['n_invalid']} invalid)"
    )
    typer.echo(
        f"  winners ranked: {summary['n_winners_appeared']}/{summary['n_winners']}"
    )
    if summary["mean_winner_rank_pct"] is not None:
        typer.echo(
            f"  winner rank percentile: median={summary['median_winner_rank_pct']:.3f} "
            f"mean={summary['mean_winner_rank_pct']:.3f}"
        )
    for k, recall in summary["recall_at_k"].items():
        typer.echo(f"  recall@{k}: {recall:.3f}")
    typer.echo(f"wrote {out_dir/'ranking.parquet'} + {out_dir/'eval.json'}")


@app.command()
def finalize(
    judgments: Path = typer.Option(..., "--judgments", help="Judgments JSONL"),
    out_dir: Path = typer.Option(
        None,
        "--out-dir",
        "-o",
        help="Output directory (default: <judgments dir>)",
    ),
) -> None:
    """Convert judgments JSONL to a single train.parquet (TRL/Unsloth-ready)."""
    from devpost import finalize as finalize_mod

    out_dir = out_dir or judgments.parent
    n = finalize_mod.run(judgments, out_dir)
    typer.echo(f"wrote {n} rows → {out_dir/'train.parquet'}")


export_app = typer.Typer(
    no_args_is_help=True,
    add_completion=False,
    help="Stage per-hackathon parquets into HuggingFace dataset layout.",
)
app.add_typer(export_app, name="export")


@export_app.command("projects")
def export_projects(
    out_dir: Path = typer.Option(
        None, "--out-dir", "-o", help="Output dir (default: data/hf/)"
    ),
) -> None:
    """Bundle data/projects/*.parquet into HF layout under data/hf/."""
    from devpost import export as export_mod

    n = export_mod.stage_projects(out_dir)
    typer.echo(f"staged {n} hackathons + 'all' → {out_dir or export_mod.PROJECTS_OUT}")


@export_app.command("judgments")
def export_judgments(
    out_dir: Path = typer.Option(
        None, "--out-dir", "-o", help="Output dir (default: data/hf-judgments/)"
    ),
) -> None:
    """Bundle data/<h>/judgments.jsonl into HF chat-format layout under data/hf-judgments/."""
    from devpost import export as export_mod

    n = export_mod.stage_judgments(out_dir)
    typer.echo(f"staged {n} hackathons + 'all' → {out_dir or export_mod.JUDGMENTS_OUT}")


if __name__ == "__main__":
    app()
