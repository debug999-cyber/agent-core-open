---
name: github-ops
description: Git/GitHub-операции: коммиты, пуши, создание/клонирование репозиториев, смена видимости. Использовать, когда речь о git или GitHub.
---

# github-ops

## Новая сессия (важно!)

Настройки git не переживают смену среды (песочница). Перед работой проверить:

```bash
cd <репо>
# ВАЖНО: `git remote -v` возвращает успех даже при ПУСТОМ списке — проверять так:
git remote get-url origin >/dev/null 2>&1 || git remote add origin https://github.com/<логин>/<имя>.git
# если нет кредов (токен выдаёт сам пользователь — повторять у него не просить):
[ -f ~/.git-credentials ] || printf 'https://<логин>:<ТОКЕН>@github.com\n' > ~/.git-credentials
# если это агентское ядро — поставить страховку:
cp hooks/pre-commit-check.sh .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit 2>/dev/null || true
```

**Пуш проверять по факту**, а не по тишине: `git ls-remote origin -h refs/heads/main` должен давать тот же хэш, что `git rev-parse HEAD`.

## Идентичность

- Имя и email для коммитов — то, что задано в `git config` пользователя (проверять, а не выдумывать).

## Одноразовая настройка (новая машина)

Токен (PAT, classic) выдаёт сам пользователь — в файле или сообщением. Никогда не просить токен повторно, если `~/.git-credentials` уже настроен.

```bash
git config --global user.name "<имя для коммитов>"
git config --global user.email "<email для коммитов>"
git config --global credential.helper store
printf 'https://<логин>:<ТОКЕН>@github.com\n' > ~/.git-credentials
chmod 600 ~/.git-credentials
```
Что произойдёт: git запомнит имя для коммитов и сможет пушить без ввода пароля.

## Правила

- Токен — **никогда** в файлах, которые попадают в репозитории, в коммитах, в переписке. Только `~/.git-credentials` (вне репозиториев) или переменная окружения.
- Новый репозиторий: сначала спросить public/private.
- Обычный `git push` — спокойно. `git push --force` — только после явного подтверждения.
- Удаление репозитория / смена видимости — только после явного подтверждения.
- Если токен был передан в чат/файл — напомнить пользователю ротацию (github.com → Settings → Developer settings → Personal access tokens → заменить).
- Сообщения коммитов — в языке пользователя, формат `<тип>: <что>`; типы: `memory`, `skill`, `docs`, `fix`, `self-check`.

## Рецепты API

```bash
# создать репозиторий (private:true/false)
curl -s -X POST https://api.github.com/user/repos \
  -H "Authorization: Bearer $GH_TOKEN" -H "Accept: application/vnd.github+json" \
  -d '{"name":"ИМЯ","description":"ОПИСАНИЕ","private":false}'

# залить папку в новый репозиторий
git init -b main && git add -A && git commit -m "Первый коммит"
git remote add origin https://github.com/$GH_USER/ИМЯ.git && git push -u origin main

# список репозиториев
curl -s "https://api.github.com/user/repos?per_page=100" -H "Authorization: Bearer $GH_TOKEN" \
  | python3 -c "import sys,json;[print(r['full_name'], 'private' if r['private'] else 'public') for r in json.load(sys.stdin)]"

# открыть / закрыть репозиторий
curl -s -X PATCH https://api.github.com/repos/$GH_USER/ИМЯ \
  -H "Authorization: Bearer $GH_TOKEN" -d '{"private":true}'    # true = закрыть, false = открыть
```
