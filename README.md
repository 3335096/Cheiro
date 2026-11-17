# CHEIRO

Telegram Mini App для хиромантии с **RAG** на профессиональных источниках (RU/EN).

## Документация

- [ТЗ v1](docs/tz-v1.md)
- [Архитектура](docs/architecture.md)
- [Решения](docs/decisions.md)
- [Runbook](docs/runbook.md)

## Быстрый старт

```bash
cp .env.example .env
# заполните OPENROUTER_API_KEY
docker compose up --build
```

| URL | Назначение |
|-----|------------|
| http://localhost:5173 | Mini App (+ `/admin`) |
| http://localhost:8000/health | API |

## Стек (фиксированный)

Python **FastAPI**, **ARQ**, **PostgreSQL + pgvector**, **Redis**, **React + Vite** TMA, **LangChain**, **OpenRouter**, хостинг **Railway**.

## Репозиторий

```text
backend/    API + worker + RAG
frontend/   TMA + admin UI
docs/       ТЗ и эксплуатация
```

## Лицензия

Proprietary — внутренний продукт.