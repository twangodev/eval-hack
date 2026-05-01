from __future__ import annotations

JUDGE_SYSTEM = (
    "You are an expert hackathon judge. You evaluate two student-built projects "
    "and decide which one is stronger overall. Weigh originality, technical depth, "
    "execution quality, and practical usefulness. Reason carefully before answering."
)

JUDGE_USER_TEMPLATE = """\
Compare the two hackathon projects below and decide which one is stronger overall.

Consider:
- Originality and creativity of the idea
- Technical depth and implementation difficulty
- Execution quality and completeness
- Practical usefulness and potential impact
- Clarity of the description / pitch

Each project has two sources of evidence — Devpost copy (the team's pitch) and
GitHub README excerpts (what was actually built). Weigh both.

=== Project A ===
Title: {a_title}
Tagline: {a_tagline}
Built with: {a_built_with}
Devpost description:
{a_description}

GitHub README excerpts:
{a_readmes}

=== Project B ===
Title: {b_title}
Tagline: {b_tagline}
Built with: {b_built_with}
Devpost description:
{b_description}

GitHub README excerpts:
{b_readmes}

Reason carefully, then end your response with a single line in this exact format:
VERDICT: A
or
VERDICT: B
or
VERDICT: TIE
"""


def _field(p: dict, k: str, default: str = "(none)") -> str:
    v = p.get(k)
    if v is None or v == "":
        return default
    if isinstance(v, list):
        return ", ".join(str(x) for x in v) if v else default
    return str(v)


def _readmes(p: dict) -> str:
    rs = p.get("readmes") or []
    if not rs:
        return "(none available)"
    parts: list[str] = []
    for r in rs:
        repo = r.get("repo", "?")
        content = (r.get("content") or "").strip()
        if not content:
            continue
        parts.append(f"--- {repo} ---\n{content}")
    return "\n\n".join(parts) if parts else "(none available)"


def render(project_a: dict, project_b: dict) -> str:
    return JUDGE_USER_TEMPLATE.format(
        a_title=_field(project_a, "title"),
        a_tagline=_field(project_a, "tagline"),
        a_built_with=_field(project_a, "built-with"),
        a_description=_field(project_a, "description"),
        a_readmes=_readmes(project_a),
        b_title=_field(project_b, "title"),
        b_tagline=_field(project_b, "tagline"),
        b_built_with=_field(project_b, "built-with"),
        b_description=_field(project_b, "description"),
        b_readmes=_readmes(project_b),
    )
