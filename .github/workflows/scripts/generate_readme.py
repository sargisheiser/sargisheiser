import os
import re
import datetime as dt
import requests

USERNAME = "sargisheiser"
LINKEDIN_URL = "https://www.linkedin.com/in/sargis-heiser/"
LOCATION = "Berlin, Germany 🇩🇪"

# Optional: Wenn du bestimmte Projekte IMMER zeigen willst (in dieser Reihenfolge),
# trage sie hier ein. Sonst nimmt das Script automatisch Top-Repos nach Stars.
PINNED_REPOS = [
    "hyperfit",
    "wono_ai",
]

API_BASE = "https://api.github.com"

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
    """
    Preserve whatever is between BLOG-POST-LIST markers
    so another workflow can keep it updated.
    """
    start = "<!-- BLOG-POST-LIST:START -->"
    end = "<!-- BLOG-POST-LIST:END -->"
    if start in existing_readme and end in existing_readme:
        pattern = re.compile(rf"{re.escape(start)}.*?{re.escape(end)}", re.S)
        match = pattern.search(existing_readme)
        if match:
            return match.group(0)
    return f"{start}\n<!-- BLOG-POST-LIST:END -->"

def fetch_repos():
    return safe_get(f"{API_BASE}/users/{USERNAME}/repos", params={"per_page": 100, "sort": "updated"})

def pick_repos(all_repos):
    # exclude forks + archived
    repos = [r for r in all_repos if not r.get("fork") and not r.get("archived")]

    if PINNED_REPOS:
        by_name = {r["name"].lower(): r for r in repos}
        chosen = []
        for name in PINNED_REPOS:
            repo = by_name.get(name.lower())
            if repo:
                chosen.append(repo)
        # if not enough, fill by stars
        if len(chosen) < 6:
            remaining = [r for r in repos if r not in chosen]
            remaining = sorted(remaining, key=lambda x: x.get("stargazers_count", 0), reverse=True)
            chosen += remaining[: (6 - len(chosen))]
        return chosen[:6]

    # fallback: top 6 by stars
    repos = sorted(repos, key=lambda x: x.get("stargazers_count", 0), reverse=True)
    return repos[:6]

def count_open_prs(repo_full_name: str) -> int:
    # GitHub Search API: open PRs count
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

        # open_issues_count includes PRs too; so we compute open PRs separately and subtract
        open_prs = count_open_prs(full)
        open_issues_total = int(r.get("open_issues_count", 0))
        open_issues = max(open_issues_total - open_prs, 0)

        lines.append(f"| [{name}]({url}) | {stars} | {forks} | {open_issues} | {open_prs} |")

    return "\n".join(lines)

def main():
    # read existing README to preserve blog list section
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
I'm **Sargis**, an **AI & Full-Stack Engineer** based in **{LOCATION}**.

## Things I code with

![Python](https://img.shields.io/badge/Python-0b0f14?style=for-the-badge&logo=python&logoColor=00ff9c)
![FastAPI](https://img.shields.io/badge/FastAPI-0b0f14?style=for-the-badge&logo=fastapi&logoColor=00ff9c)
![TypeScript](https://img.shields.io/badge/TypeScript-0b0f14?style=for-the-badge&logo=typescript&logoColor=00ff9c)
![React](https://img.shields.io/badge/React-0b0f14?style=for-the-badge&logo=react&logoColor=00ff9c)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-0b0f14?style=for-the-badge&logo=postgresql&logoColor=00ff9c)
![Docker](https://img.shields.io/badge/Docker-0b0f14?style=for-the-badge&logo=docker&logoColor=00ff9c)
![GitHub_Actions](https://img.shields.io/badge/GitHub%20Actions-0b0f14?style=for-the-badge&logo=githubactions&logoColor=00ff9c)

## Open source projects

{projects_md}

## My latest posts

{blog_section}

## Stats

![Stats](https://github-readme-stats.vercel.app/api?username={USERNAME}&show_icons=true&theme=tokyonight)
![Streak](https://streak-stats.demolab.com?user={USERNAME}&theme=tokyonight)
![Activity](https://github-readme-activity-graph.vercel.app/graph?username={USERNAME}&theme=tokyo-night)

## Where to find me

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0b0f14?style=for-the-badge&logo=linkedin&logoColor=00ff9c)]({LINKEDIN_URL})
[![GitHub](https://img.shields.io/badge/GitHub-0b0f14?style=for-the-badge&logo=github&logoColor=00ff9c)](https://github.com/{USERNAME})

---

This README is generated automatically (every 3 hours).  
Last refresh: **{last_refresh}**
"""
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme)

if __name__ == "__main__":
    main()
