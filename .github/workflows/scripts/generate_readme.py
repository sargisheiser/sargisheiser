import os
import datetime as dt
import requests

USERNAME = "sargisheiser"  # <-- HIER deinen GitHub-Username eintragen

def fetch_repos():
    url = f"https://api.github.com/users/{USERNAME}/repos?per_page=100&sort=updated"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    repos = r.json()

    # nur eigene repos, keine forks
    repos = [x for x in repos if not x.get("fork")]

    # sortiere nach stars, nimm top 6
    repos = sorted(repos, key=lambda x: x.get("stargazers_count", 0), reverse=True)[:6]
    return repos

def build_projects_table(repos):
    lines = []
    lines.append("| Project | ⭐ Stars | 🍴 Forks | 🐛 Issues |")
    lines.append("|---|---:|---:|---:|")
    for r in repos:
        name = r["name"]
        url = r["html_url"]
        stars = r.get("stargazers_count", 0)
        forks = r.get("forks_count", 0)
        issues = r.get("open_issues_count", 0)
        lines.append(f"| [{name}]({url}) | {stars} | {forks} | {issues} |")
    return "\n".join(lines)

def main():
    repos = fetch_repos()
    projects = build_projects_table(repos)

    last_refresh = dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    readme = f"""# 😎 Hey! Nice to see you.

Welcome to my page!  
I'm **Sargis**, AI / Full-Stack Engineer based in **Berlin, Germany** 🇩🇪

---

## Things I code with
![Python](https://img.shields.io/badge/Python-0b0f14?style=for-the-badge&logo=python&logoColor=00ff9c)
![FastAPI](https://img.shields.io/badge/FastAPI-0b0f14?style=for-the-badge&logo=fastapi&logoColor=00ff9c)
![React](https://img.shields.io/badge/React-0b0f14?style=for-the-badge&logo=react&logoColor=00ff9c)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-0b0f14?style=for-the-badge&logo=postgresql&logoColor=00ff9c)
![Docker](https://img.shields.io/badge/Docker-0b0f14?style=for-the-badge&logo=docker&logoColor=00ff9c)

---

## Open source projects
{projects}

---

## Stats
![Stats](https://github-readme-stats.vercel.app/api?username={USERNAME}&show_icons=true&theme=tokyonight)
![Streak](https://streak-stats.demolab.com?user={USERNAME}&theme=tokyonight)

---

## Where to find me
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0b0f14?style=for-the-badge&logo=linkedin&logoColor=00ff9c)](https://www.linkedin.com/)
[![GitHub](https://img.shields.io/badge/GitHub-0b0f14?style=for-the-badge&logo=github&logoColor=00ff9c)](https://github.com/{USERNAME})

---

This README file is generated every 3 hours.  
Last refresh: **{last_refresh}**
"""
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme)

if __name__ == "__main__":
    main()
