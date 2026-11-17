# Архитектура CHEIRO

## Сервисы

```text
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  TMA React  │────▶│  FastAPI     │────▶│ PostgreSQL  │
│  (static)   │     │  REST + JWT  │     │ + pgvector  │
└─────────────┘     │  Telegram    │     └─────────────┘
       ▲            │  initData    │            ▲
       │            └──────┬───────┘            │
┌─────────────┐             │                    │
│ Telegram    │─────────────┘                    │
│ Bot         │                                  │
└─────────────┘            ┌──────────────┐      │
                           │ ARQ Worker   │──────┘
                           │ OCR/RAG/CV   │
                           └──────┬───────┘
                                  │
                           ┌──────▼───────┐
                           │ Redis        │
                           └──────────────┘
```

## Потоки данных

### Индексация книги

`Admin upload` → `sources` row → ARQ `ingest_source` → extract text (EPUB / PDF / OCR) → chunk → embed → `document_chunks`.

### Анализ ладони (v1)

`TMA photo` (base64, не пишется на диск) → `analysis_jobs` → worker:

1. `palm_cv` adapter (noop пока нет подрядчика) → структурированные **текстовые** признаки.
2. RAG query с признаками + system prompt.
3. Тизер + full report в job; бот забирает full по `telegram_id`.

## Репозиторий

```text
cheiro/
├── backend/          # FastAPI, worker, RAG
├── frontend/         # TMA + admin (shared design tokens)
├── docs/
├── docker-compose.yml
└── railway.toml      # шаблон multi-service на Railway
```

## Railway (prod)

Рекомендуемые сервисы в одном проекте:

1. **api** — Dockerfile `backend`, порт `$PORT`
2. **worker** — тот же образ, команда `arq app.worker.WorkerSettings`
3. **postgres** — Railway plugin или образ с pgvector
4. **redis** — Railway Redis
5. **frontend** — статика (nginx) или отдача через api `/` (v1: отдельный сервис)

Локально всё поднимается `docker compose up --build`.

## Безопасность

- Валидация Telegram `initData` HMAC на API.
- Admin routes — отдельный токен / будущая auth (v1: `ADMIN_API_TOKEN` для команды).
- CORS только для WebApp origin.