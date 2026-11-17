# Локальная разработка (Windows, macOS, Linux)

## Что установить

- **Git**
- **Node.js 22+** (команды проекта на Node, работают одинаково на всех ОС)
- **Python 3.12** (на Windows с установленным `py`-лаунчером: python.org → галочка «py launcher»)
- **Docker Desktop** (на Windows с бэкендом WSL2)

Команды выполняйте в PowerShell, Git Bash или WSL из корня репозитория. `make` не нужен.

## Первый запуск

```bash
npm run setup     # venv в backend/.venv, зависимости backend и frontend, .env из .env.example
```

Откройте `.env` и впишите `OPENROUTER_API_KEY` (без него не работают эмбеддинги и LLM). Остальные значения по умолчанию подходят для разработки.

```bash
npm run dev       # весь стек: postgres+pgvector, redis, api, worker, frontend
```

| Адрес | Что |
|-------|-----|
| http://localhost:5173 | Mini App |
| http://localhost:5173/admin | Временная админка (токен = `ADMIN_API_TOKEN` из `.env`) |
| http://localhost:8000/docs | Swagger API |
| http://localhost:8000/health | Проверка живости |

Остановка: `npm run dev:down`. Данные Postgres хранятся в Docker-томе `cheiro_pg` и переживают перезапуск.

В режиме `DEBUG=true` Mini App работает в обычном браузере без Telegram (пользователь `dev-user`). В продакшене требуется подпись Telegram.

## Ежедневные команды

| Команда | Что делает |
|---------|------------|
| `npm run check` | ruff, mypy, pytest, oxlint, prettier, tsc, vitest, build — как в CI, без БД |
| `npm run check:backend` / `check:frontend` | только одна часть |
| `npm run check:integration` | дополнительно интеграционные тесты pgvector |
| `npm run fix` | автоисправление и форматирование |
| `npm run eval` | прогон golden-набора RAG (нужны книги в индексе и ключ) |
| `npm run sync` | синхронизация с GitHub и облачными агентами |

### Интеграционные тесты

```bash
docker compose up -d postgres redis
npm run check:integration
```

Тесты используют отдельную базу `cheiro_test` (создаётся сама) и отказываются работать с базой, имя которой не оканчивается на `_test`: рабочие данные не пострадают.

## Проверка RAG вручную

1. Загрузите EPUB или текстовый PDF в админке.
2. Дождитесь статуса `ready`.
3. Задайте вопрос. Проще всего через Swagger (работает одинаково на любой ОС): http://localhost:8000/docs → `POST /api/admin/rag/query` → Try it out → в поле `X-Admin-Token` вставьте значение `ADMIN_API_TOKEN` из `.env` → тело `{"query": "What does the heart line represent?"}`.

   То же из Git Bash или WSL:

```bash
curl -s -X POST http://localhost:8000/api/admin/rag/query \
  -H "X-Admin-Token: $ADMIN_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"What does the heart line represent?"}'
```

   В PowerShell `curl` является псевдонимом другой команды: используйте Swagger или `curl.exe`.

## Telegram (бот и Mini App с нуля)

1. @BotFather → `/newbot` → токен в `TELEGRAM_BOT_TOKEN`.
2. Mini App требует HTTPS-адрес. Для локальной проверки используйте туннель (например, Cloudflare Tunnel или ngrok) на порт 5173; для первых тестов — Railway.
3. В @BotFather `/newapp` (или кнопка меню бота) укажите URL Mini App; `TELEGRAM_WEBAPP_URL` должен совпадать с ним.

## Особенности Windows

- **Горячая перезагрузка в Docker** включена через polling (`WATCHFILES_FORCE_POLLING`, `VITE_USE_POLLING`): события файловой системы через bind-mount в Docker Desktop не доходят. Для самой быстрой работы держите репозиторий внутри файловой системы WSL2.
- **Worker не перезагружается сам:** после правок `docker compose restart worker`.
- **`node_modules` frontend в контейнере** живут в отдельном томе, поэтому не конфликтуют с Windows-версиями из `npm run setup`.
- Переводы строк фиксируются `.gitattributes` (LF), скрипты безопасны для Linux-окружений.

## Частые проблемы

| Симптом | Причина и решение |
|---------|-------------------|
| `Backend virtualenv not found` | выполните `npm run setup` |
| Источник в статусе `failed`, «Missing Authentication header» | не задан `OPENROUTER_API_KEY` |
| `failed`: «OCR_PROVIDER=none» | PDF без текстового слоя (скан); нужен OCR-провайдер |
| Порт 5432 или 6379 занят | остановите локальные Postgres/Redis или измените порты в `docker-compose.yml` |
