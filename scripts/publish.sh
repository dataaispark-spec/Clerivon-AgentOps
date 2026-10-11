#!/usr/bin/env bash
set -euo pipefail
REPO="${GITHUB_REPO:-dataaispark-spec/Clerivon-AgentOps}"
command -v gh >/dev/null || { echo "Install GitHub CLI: https://cli.github.com/"; exit 1; }
gh auth status
if [ ! -d .git ]; then
  git init
  git branch -M main
  git add .
  git commit -m "Initial Clerivon AgentOps reference implementation"
fi
if gh repo view "$REPO" >/dev/null 2>&1; then
  git remote get-url origin >/dev/null 2>&1 || git remote add origin "https://github.com/$REPO.git"
  git push -u origin main
else
  gh repo create "$REPO" --public --source=. --remote=origin --push
fi
