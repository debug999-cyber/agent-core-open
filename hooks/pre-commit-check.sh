#!/usr/bin/env bash
# pre-commit: не пускать секреты в репозиторий.
# Установка: cp hooks/pre-commit-check.sh .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit

# 1) Файлы, похожие на секреты
if git diff --cached --name-only -r | grep -Eq '(\.env$|\.key$|\.pem$|\.p12$|id_rsa|id_ed25519|credentials|\.token$)'; then
  echo "❌ Коммит отклонён: в коммит попадает файл, похожий на секрет:"
  git diff --cached --name-only -r | grep -E '(\.env$|\.key$|\.pem$|\.p12$|id_rsa|id_ed25519|credentials|\.token$)'
  echo "   Если это нужно — добавь файл в .gitignore."
  exit 1
fi

# 2) Строки, похожие на токены GitHub
if git diff --cached -U0 | grep -E '^\+' | grep -Eq 'ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|xox[baprs]-[A-Za-z0-9-]{10,}'; then
  echo "❌ Коммит отклонён: в изменениях есть строка, похожая на токен."
  echo "   Токены живут только в ~/.git-credentials (вне репозиториев) или в переменных окружения."
  exit 1
fi

exit 0
