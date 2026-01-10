import os
import re
import datetime as dt
import requests

USERNAME = "sargisheiser"
LINKEDIN_URL = "https://www.linkedin.com/in/sargis-heiser/"
LOCATION = "Berlin, Germany 🇩🇪"

# Always show these first (order matters). Then fill up to 6 by stars.
PINNED_REPOS = [
    "hyperfit",
    "wono_ai",
    "hyperfit_mobile",
    "masterblog_api",
    "book_alchemy",
]

API_BASE = "https://api.github.com"

# Cyberpunk palette
BG = "0b0f14"
NEON = "00ff9c"   # neon green
NEON2 = "ff2bd6"  # neon pink (optional accents)

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
    return f"""{start}
- ░░░ NO FEED CONNECTED YET ░░░
{end}"""

def fetch_repos():
    return safe_get(f"{API_BASE}/users/{USERNAME}/repos", params={"per_page": 100, "sort": "updated"})

def pick_repos(all_repos):
    repos = [r for r in all_repos if not r.get("fork") and not r.get("archived")]
    by_name = {r["name"].lower(): r for r in repos}

    chosen = []
    for name in PINNED_REPOS:
        repo = by_name.get(name.lower())
        if repo:
            chosen.append(repo)

    remaining = [r for r in repos if r not in chosen]
    remaining = sorted(remaining, key=lambda x: x.get("stargazers_count", 0), reverse=True)

    # Fill up to 6
    chosen += remaining[: max(0, 6 - len(chosen))]
    return chosen[:6]

def count_open_prs(repo_full_name: str) -> int:
    q = f"repo:{repo_full_name} is:pr is:open"
    data = safe_get(f"{API_BASE}/search/issues", params={"q": q, "per_page": 1})
    return int(data.get("total_count", 0))

def build_projects_table(repos):
    lines = []
    lines.append("| Project | ⭐ Stars | 🍴 Forks | 🐛 Open Issues | 🔀 Open PRs |")
    lines.append("|---|---:|---:|---:|---:|")

    for r in repos:
        name = r["name"]
        url = r["html_url"]
        full = r["full_name"]

        stars = r.get("stargazers_count", 0)
        forks = r.get("forks_count", 0)

        open_prs = count_open_prs(full)
        open_issues_total = int(r.get("open_issues_count", 0))
        open_issues = max(open_issues_total - open_prs, 0)

        lines.append(f"| [{name}]({url}) | {stars} | {forks} | {open_issues} | {open_prs} |")

    return "\n".join(lines)

def badge(label, logo=None):
    # label without spaces for URL
    safe_label = label.replace(" ", "%20")
    if logo:
        return f"![{label}](https://img.shields.io/badge/{safe_label}-{BG}?style=for-the-badge&logo={logo}&logoColor={NEON})"
    return f"![{label}](https://img.shields.io/badge/{safe_label}-{BG}?style=for-the-badge&logoColor={NEON})"

def main():
    existing = ""
    if os.path.exists("README.md"):
        with open("README.md", "r", encoding="utf-8") as f:
            existing = f.read()

    blog_section = get_blog_section(existing)
    repos = fetch_repos()
    chosen = pick_repos(repos)
    projects_md = build_projects_table(chosen)

    last_refresh = dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    readme = f"""# 😎 Hey! Nice to see you.

Welcome to my page!  
I’m **Sargis**, an **AI & Full-Stack Engineer** based in **{LOCATION}**.


## Things I code with

### Core
{badge("Python", "python")}
{badge("FastAPI", "fastapi")}
{badge("TypeScript", "typescript")}
{badge("JavaScript", "javascript")}
{badge("React", "react")}
{badge("Vite", "vite")}
{badge("Tailwind CSS", "tailwindcss")}
{badge("Node.js", "nodedotjs")}

### AI / LLM / Agents
{badge("OpenAI", "openai")}
{badge("Claude", "claude-ai")}
{badge("LangChain", "langchain")}
{badge("Cursor", "cursor")}
{badge("RAG")}
{badge("Embeddings")}
{badge("Vector DB")}
{badge("Prompt Engineering")}
{badge("AI Agents")}
{badge("n8n", "n8n")}

### Data / Backend
{badge("PostgreSQL", "postgresql")}
{badge("SQL")}
{badge("SQLAlchemy", "sqlalchemy")}
{badge("Pydantic", "pydantic")}
{badge("REST API")}
{badge("Web Scraping")}
{badge("APIs")}

### DevOps / Tools
{badge("Docker", "docker")}
{badge("Git", "git")}
{badge("GitHub Actions", "githubactions")}
{badge("Linux", "linux")}

### Product / Project
{badge("Agile")}
{badge("Scrum")}
{badge("Notion", "notion")}
{badge("Linear", "linear")}
{badge("Jira", "jira")}
{badge("SaaS")}


---

## Open source projects

{projects_md}

---

## My latest posts

{blog_section}

---

## Stats
![Stats](https://github-readme-stats.vercel.app/api?username=sargisheiser&show_icons=true&theme=tokyonight)
![Streak](https://streak-stats.demolab.com?user=sargisheiser&theme=tokyonight)



---

## Where to find me

[![LinkedIn](https://img.shields.io/badge/LinkedIn-{BG}?style=for-the-badge&logo=linkedin&logoColor={NEON})]({LINKEDIN_URL})
[![GitHub](https://img.shields.io/badge/GitHub-{BG}?style=for-the-badge&logo=github&logoColor={NEON})](https://github.com/{USERNAME})

---

> This README is generated automatically (every 3 hours).  
> Last refresh: **{last_refresh}**
"""
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme)

if __name__ == "__main__":
    main()

