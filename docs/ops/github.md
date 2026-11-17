# GitHub: защита ветки, CI, Bugbot, синхронизация

GitHub — источник правды. Компьютер и облачные агенты Cursor (в том числе с телефона) работают через ветки и pull request.

## Что настроить один раз (в интерфейсе GitHub)

Репозиторий переименован в `Cheiro`; GitHub перенаправляет со старого адреса. Обновите remote локально:

```bash
git remote set-url origin https://github.com/3335096/Cheiro.git
```

**Settings → Branches → Add branch ruleset** для `main`:

- Require a pull request before merging.
- Require status checks: `backend`, `frontend`, `docker`, `secrets-scan` (из CI) и **Cursor Bugbot**.
- Block force pushes и deletions.
- Разрешите автоудаление веток после слияния (Settings → General → Automatically delete head branches).

Для одного владельца запрет «обойти правила» можно оставить включённым: так облачные агенты не смогут записать в `main`, а вы всегда проходите CI.

## CI (`.github/workflows/ci.yml`)

| Задание | Что проверяет |
|---------|---------------|
| `backend` | ruff, mypy, pytest вместе с интеграционными тестами на pgvector (сервис Postgres) |
| `frontend` | oxlint, prettier, tsc, vitest, build |
| `docker` | сборка образов backend и frontend |
| `secrets-scan` | gitleaks по истории |

Локально те же проверки: `npm run check` и `npm run check:integration`.

Dependabot (`.github/dependabot.yml`) раз в неделю предлагает обновления pip и npm, раз в месяц GitHub Actions.

## Bugbot

Автоматическое ревью каждого PR. Включается в Cursor Dashboard → Bugbot (подключить репозиторий). Правила ревью лежат в `.cursor/BUGBOT.md` (приватность, авторизация, секреты, RAG, интерфейсы). Правила `.cursor/rules/*.mdc` на Bugbot **не действуют**, поэтому его правила ведутся отдельным файлом.

Ручной запуск: комментарий `bugbot run` в PR. Чтобы Bugbot блокировал слияние, добавьте его проверку в обязательные.

## Ежедневная работа

- Утро или смена устройства: `npm run sync`.
- Закончили на этом компьютере и хотите продолжить с телефона или другого ноутбука: в чате Cursor **на этом компьютере** напишите «закончил работу локально». Агент закоммитит изменения, запушит ветку и откроет pull request. В ответ будет имя ветки.
- На другом устройстве напишите «продолжи ветку <имя>». Агент заберёт её с GitHub и продолжит. Пока фраза не сказана на компьютере, где лежат файлы, другое устройство их не увидит.
- В `main` эта фраза ничего не сливает. Слияние — отдельная фраза «слей в main», и только у PR с зелёным CI.
- Облачный агент для новой задачи создаёт ветку `cursor/<описание>-<суффикс>` и открывает PR.
- После слияния: `git checkout main && git pull`, удалите локальную ветку.

Подробно: скилы `handoff-work` и `sync-with-github`.
