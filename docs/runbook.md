# CHEIRO — runbook (самостоятельный запуск)

## Локально

1. Скопируйте `.env.example` → `.env`, добавьте `OPENROUTER_API_KEY`.
2. `docker compose up --build`
3. Откройте:
   - Mini App (dev): http://localhost:5173
   - API health: http://localhost:8000/health
   - Admin: http://localhost:5173/admin (токен = `ADMIN_API_TOKEN`)

## RAG smoke-test

1. В админке загрузите EPUB или текстовый PDF.
2. Дождитесь статуса `ready` у источника.
3. Запрос (curl):

```bash
curl -s -X POST http://localhost:8000/api/admin/rag/query \
  -H "X-Admin-Token: dev-admin-change-me" \
  -H "Content-Type: application/json" \
  -d '{"query":"What does the heart line represent?"}'
```

## Telegram (с нуля)

1. @BotFather → `/newbot` → сохраните токен в `TELEGRAM_BOT_TOKEN`.
2. `/newapp` привяжите Web App URL (после деплоя HTTPS).
3. `TELEGRAM_WEBAPP_URL` = публичный URL фронтенда.

## Railway

Сервисы:

| Service | Start command |
|---------|----------------|
| api | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| worker | `arq app.worker.WorkerSettings` |
| postgres | plugin pgvector |
| redis | plugin Redis |
| frontend | build `frontend/Dockerfile`, env `VITE_API_URL=https://<api-domain>` |

Переменные окружения — как в `.env.example` (без файла, через UI).

## Этап 2 (не включено)

- CloudPayments env
- zhivo.crm webhook
- Astro upsell modules