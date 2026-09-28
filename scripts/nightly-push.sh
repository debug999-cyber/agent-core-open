#!/bin/bash
# Ночной работник «мозга» agent-core: записывает накопленное и отправляет в облако.
# Запускается расписанием ОС (launchd на macOS, cron на Linux) — без агента.
# Токены чата не тратятся.
# Путь к репозиторию: переменная AGENT_CORE_HOME (по умолчанию ~/agent-core).
# Лог: ~/.agent-core-nightly-push.log
set -u

REPO="${AGENT_CORE_HOME:-$HOME/agent-core}"
LOG="$HOME/.agent-core-nightly-push.log"

log() { printf '%s  %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$1" >> "$LOG"; }

cd "$REPO" 2>/dev/null || { log "ОШИБКА: нет папки $REPO"; exit 1; }
log "--- ночное сохранение: старт"

# 1) Записать в снимок всё, что накопилось (правки в заметках, заметки агента)
if [ -n "$(git status --porcelain)" ]; then
  if git add -A && git commit -m "nightly: авто-сохранение $(date '+%Y-%m-%d %H:%M')" >>"$LOG" 2>&1; then
    log "незаписанное сохранено"
  else
    log "ОШИБКА: не удалось сохранить (смотри лог выше)"
  fi
  # 2) Отправить в облако и проверить по факту
  if git push >>"$LOG" 2>&1; then
    log "отправлено в облако"
  else
    log "ОШИБКА: не удалось отправить (смотри лог выше)"
  fi
else
  log "незаписанного нет"
fi
log "--- ночное сохранение: готово"
