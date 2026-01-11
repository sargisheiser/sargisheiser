import os
from pathlib import Path
import yaml
import datetime as dt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

TEMPLATE_PATH = ROOT / "README.template.md"
OUTPUT_PATH = ROOT / "README.md"

PROFILE_YML = DATA / "profile.yml"
PROOF_YML = DATA / "proof.yml"
PROJECTS_YML = DATA / "projects.yml"
SKILLS_YML = DATA / "skills.yml"

# Blog block is updated by fetch_blog.py (Step 4). If missing, use placeholder.
BLOG_SNIPPET_PATH = DATA / "blog_snippet.md"


def load_yaml(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Missing required file: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8").strip()


def render_proof_block(proof_data: dict) -> str:
    items = proof_data.get("proof", [])
    if not items:
        return "- (Add proof points in `data/proof.yml`)"
    lines = []
    for p in items:
        metric = p.get("metric", "").strip()
        context = p.get("context", "").strip()
        if metric and context:
            lines.append(f"- **{metric}** — {context}")
        elif metric:
            lines.append(f"- **{metric}**")
    return "\n".join(lines)


def render_now_block(profile: dict) -> str:
    focus = profile.get("focus", [])
    if not focus:
        return "- (Add focus areas in `data/profile.yml`)"
    return "\n".join([f"- {x}" for x in focus])


def render_projects_block(projects_data: dict, max_flagship: int = 3, max_secondary: int = 2) -> str:
    projects = projects_data.get("projects", [])
    if not projects:
        return "- (Add projects in `data/projects.yml`)"

    flagship = [p for p in projects if p.get("category") == "flagship"]
    secondary = [p for p in projects if p.get("category") == "secondary"]

    def render_project(p: dict) -> str:
        name = p.get("name", "Unnamed")
        url = p.get("url", "")
        one_liner = p.get("one_liner", "").strip()
        impact = p.get("impact", []) or []
        stack = p.get("stack", []) or []

        title = f"### [{name}]({url})" if url else f"### {name}"
        lines = [title]
        lines.append("---")

        if one_liner:
            lines.append(f"**What it is:** {one_liner}")

        if impact:
            lines.append("")
            lines.append("**Why it matters:**")
            for i in impact[:3]:
                lines.append(f"- {i}")

        if stack:
            lines.append("")
            lines.append(f"**Stack:** {', '.join(stack[:10])}")

        lines.append("")
        lines.append("—")
        return "\n".join(lines)


    out = []

    # Flagship
    for p in flagship[:max_flagship]:
        out.append(render_project(p))
        out.append("")

    # Secondary
    if secondary[:max_secondary]:
        out.append("## Additional projects")
        for p in secondary[:max_secondary]:
            out.append(render_project(p))
            out.append("")

    return "\n".join(out).strip()


def render_stack_block(skills_data: dict) -> str:
    skills = skills_data.get("skills", {})
    if not skills:
        return "- (Add skills in `data/skills.yml`)"

    # Compact, recruiter-friendly. No badge spam.
    # Render as grouped bullet lists (ATS-friendly).
    lines = []
    group_titles = {
        "ai_engineering": "AI Engineering",
        "backend": "Backend",
        "data": "Data",
        "tooling": "Tooling",
        "methods": "Methods",
    }

    for key in ["ai_engineering", "backend", "data", "tooling", "methods"]:
        items = skills.get(key, [])
        if not items:
            continue
        title = group_titles.get(key, key.replace("_", " ").title())
        lines.append(f"**{title}:** {', '.join(items)}")

    if not lines:
        return "- (Skills groups present but empty.)"

    return "\n\n".join(lines)


def apply_placeholders(template: str, mapping: dict) -> str:
    out = template
    for k, v in mapping.items():
        out = out.replace(f"{{{{{k}}}}}", v)
    return out


def main():
    template = TEMPLATE_PATH.read_text(encoding="utf-8")

    profile = load_yaml(PROFILE_YML)
    proof = load_yaml(PROOF_YML)
    projects = load_yaml(PROJECTS_YML)
    skills = load_yaml(SKILLS_YML)

    blog_block = load_text(BLOG_SNIPPET_PATH)
    if not blog_block:
        blog_block = "- Writing in progress — technical notes coming soon."

    linkedin = profile.get("contact", {}).get("linkedin", "")
    github = profile.get("contact", {}).get("github", "")
    email = profile.get("contact", {}).get("email", "")

    # Build blocks
    proof_block = render_proof_block(proof)
    now_block = render_now_block(profile)
    projects_block = render_projects_block(projects)
    stack_block = render_stack_block(skills)

    refreshed = dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    footer = f"\n\n---\n_Last refresh: **{refreshed}** (auto-generated)_\n"

    mapping = {
        "PROOF_BLOCK": proof_block,
        "NOW_BLOCK": now_block,
        "PROJECTS_BLOCK": projects_block,
        "STACK_BLOCK": stack_block,
        "BLOG_BLOCK": blog_block,
        "LINKEDIN": linkedin,
        "GITHUB": github,
        "EMAIL": email,
    }

    readme = apply_placeholders(template, mapping) + footer

    OUTPUT_PATH.write_text(readme, encoding="utf-8")
    print(f"✅ Generated {OUTPUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
