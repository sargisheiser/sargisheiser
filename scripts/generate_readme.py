import os
import re
import datetime as dt
import requests

USERNAME = "sargisheiser"
LINKEDIN_URL = "https://www.linkedin.com/in/sargis-heiser/"
LOCATION = "Berlin, Germany 🇩🇪"

API_BASE = "https://api.github.com"

# Badge style (neutral, recruiter-friendly)
BG = "111827"       # dark slate
ACCENT = "60A5FA"   # blue

# Curated (max 12–14). Recruiter wants focus, not 50 labels.
BADGES = [
    ("Python", "python"),
    ("FastAPI", "fastapi"),
    ("PostgreSQL", "postgresql"),
    ("SQLAlchemy", "sqlalchemy"),
    ("Docker", "docker"),
    ("GitHub Actions", "githubactions"),
    ("OpenAI", "openai"),
    ("Claude", None),          # no reliable shields logo -> text badge
    ("LangChain", None),       # text badge (safe)
    ("RAG", None),             # text badge (safe)
    ("Jira", "jira"),
    ("Notion", "notion"),
    ("Linear", "linear"),
]

# Selected projects with context (this is what sells)
SELECTED_PROJECTS = [
    {
        "name": "HyperFit",
        "url": "https://github.com/sargisheiser/hyperfit",
        "one_liner": "AI-powered fitness analysis using computer vision + LLM-based coaching.",
        "stack": "Python · MediaPipe · OpenAI · FastAPI",
    },
    {
        "name": "WONO AI",
        "url": "https://github.com/sargisheiser/wono_ai",
        "one_liner": "Automation-focused AI platform for data-driven workflows and integrations.",
        "stack": "Python · APIs · LLMs",
    },
    {
        "name": "masterblog_api",
        "url": "https://github.com/sargisheiser/masterblog_api",
        "one_liner": "Backend service for content & data workflows (API-first).",
        "stack": "Python · FastAPI · PostgreSQL",
    },
]

def gh_headers():
    h = {"Accept": "application/vnd.github+json"}
    token = os.getenv("GITHUB_TOKEN")
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h

def safe_get(url: str, params=None):
    r = requests.get(url, headers=gh_headers(), params=params, timeout=30)
    r.raise_for_status()
    return r.json()

def get_blog_section(existing_readme: str) -> str:
    start = "<!-- BLOG-POST-LIST:START -->"
    end = "<!-- BLOG-POST-LIST:END -->"
    if start in existing_readme and end in existing_readme:
        pattern = re.compile(rf"{re.escape(start)}.*?{re.escape(end)}", re.S)
        m = pattern.search(existing_readme)
        if m:
            return m.group(0)

    # Placeholder (will be replaced by blog workflow once posts exist)
    return f"""{start}
- (Blog feed connected — posts will appear here automatically.)
{end}"""

def badge(label: str, logo: str | None):
    safe_label = label.replace(" ", "%20")
    if logo:
        return f"![{label}](https://img.shields.io/badge/{safe_label}-{BG}?style=for-the-badge&logo={logo}&logoColor={ACCENT})"
    return f"![{label}](https://img.shields.io/badge/{safe_label}-{BG}?style=for-the-badge&logoColor={ACCENT})"

def render_badges():
    return "\n".join(badge(lbl, lg) for (lbl, lg) in BADGES)

def render_selected_projects():
    lines = []
    for p in SELECTED_PROJECTS:
        lines.append(f"**[{p['name']}]({p['url']})**  ")
        lines.append(f"{p['one_liner']}  ")
        lines.append(f"*{p['stack']}*")
        lines.append("")  # blank line
    return "\n".join(lines).strip()

def main():
    existing = ""
    if os.path.exists("README.md"):
        with open("README.md", "r", encoding="utf-8") as f:
            existing = f.read()

    blog_section = get_blog_section(existing)
    last_refresh = dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    readme = f"""# Sargis Heiser

**AI Engineer (Python, LLMs, Automation)**  
Background in IT Project & Product Management · {LOCATION}

---

## Profile

AI Engineer with a strong background in **IT project and product management**, now focused on building  
**AI-driven backend systems, LLM applications, and automation solutions**.

I translate business requirements into scalable technical solutions with hands-on work in  
**Python APIs, data systems, and modern AI tooling**.

---

## Core Expertise

- **AI Engineering & LLM Systems** (RAG, agents, prompt engineering, automation workflows)  
- **Backend Engineering (Python)** (FastAPI, SQL, PostgreSQL, APIs)  
- **Product & Delivery** (Agile execution, Jira/Linear, stakeholder communication, end-to-end ownership)

---

## Tech Stack

{render_badges()}

---

## Selected Projects

{render_selected_projects()}

---

## My latest posts

{blog_section}

---

## Contact

- LinkedIn: {LINKEDIN_URL}  
- GitHub: https://github.com/{USERNAME}

---

_Last refresh: **{last_refresh}** (auto-generated)_
"""
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme)

if __name__ == "__main__":
    main()
