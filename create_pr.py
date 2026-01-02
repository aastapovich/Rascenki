#!/usr/bin/env python3
"""
create_pr.py

Создаёт Pull Request для текущего репозитория/ветки, используя `GITHUB_TOKEN`.
Как пользоваться:

1) Активировать venv (если нужно) и установить зависимость:
   . .venv/bin/activate
   pip install ghapi

2) Экспортировать токен в окружение (вставьте ваш новый токен локально, не в чат):
   export GITHUB_TOKEN=ghp_...

3) Запустить (в корне репозитория):
   python create_pr.py --base main \
       --title "Fix tooltip binding overwrite and BS4 deprecation" \
       --body "Preserve Tooltip handlers by appending legacy binds (add='+'), and replace deprecated findNextSiblings with find_next_siblings. Tests pass locally."

Если аргументы не заданы — используется ветка current head как head, base = 'main', и простое тело.
"""

import os
import subprocess
import sys
import argparse

try:
    from ghapi.core import GhApi
except Exception as e:
    print("Ошибка: требуем пакет 'ghapi'. Установите: pip install ghapi")
    raise


def get_origin_remote():
    try:
        out = subprocess.check_output(["git", "remote", "get-url", "origin"])  # raises if no origin
        url = out.decode().strip()
        return url
    except Exception as e:
        print("Не удалось получить URL origin:", e)
        return None


def parse_owner_repo(url: str):
    # handle formats: git@github.com:owner/repo.git or https://github.com/owner/repo.git
    if url.startswith("git@"):
        # git@github.com:owner/repo.git
        try:
            _, path = url.split(":", 1)
            owner, repo = path.split("/", 1)
        except Exception:
            return None, None
    else:
        # https://github.com/owner/repo.git
        try:
            parts = url.split("/")
            owner = parts[-2]
            repo = parts[-1]
        except Exception:
            return None, None
    if repo.endswith('.git'):
        repo = repo[:-4]
    return owner, repo


def get_current_branch():
    try:
        out = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"])  # bytes
        return out.decode().strip()
    except Exception:
        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="main", help="Base branch (default: main)")
    parser.add_argument("--title", default=None, help="PR title")
    parser.add_argument("--body", default=None, help="PR body")
    parser.add_argument("--head", default=None, help="Head branch (default: current branch)")
    args = parser.parse_args()

    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("Error: set GITHUB_TOKEN environment variable (do not paste token in chat).")
        sys.exit(1)

    url = get_origin_remote()
    if not url:
        print("Error: cannot determine origin remote URL. Ensure you're in a git repo with origin.")
        sys.exit(1)

    owner, repo = parse_owner_repo(url)
    if not owner or not repo:
        print("Error: cannot parse owner/repo from origin url:", url)
        sys.exit(1)

    head = args.head or get_current_branch()
    if not head:
        print("Error: cannot determine current branch. Pass --head explicitly.")
        sys.exit(1)

    title = args.title or f"Auto PR: {head} -> {args.base}"
    body = args.body or "Auto-created PR via create_pr.py"

    print(f"Repo: {owner}/{repo}")
    print(f"Creating PR: head={head} base={args.base} title='{title}'")

    try:
        api = GhApi(owner=owner, repo=repo, token=token)
        pr = api.pulls.create(title=title, head=head, base=args.base, body=body)
        print("PR created:", pr.html_url)
    except Exception as e:
        print("Failed to create PR:", e)
        sys.exit(1)


if __name__ == '__main__':
    main()
