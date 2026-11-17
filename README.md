# CHEIRO

Telegram Mini App для анализа линий руки. Ядро продукта — **RAG на профессиональной литературе по хиромантии** (RU/EN). Фото ладоней нигде не сохраняются.

## Быстрый старт

```bash
npm run setup     # зависимости, .env
# впишите OPENROUTER_API_KEY в .env
npm run dev       # весь стек в Docker Compose
```

Mini App: http://localhost:5173 · API: http://localhost:8000/docs

Нужны Git, Node 22+, Python 3.12, Docker Desktop. Подробно: [локальная разработка](docs/ops/local-development.md).

## Команды

| Команда | Что делает |
|---------|------------|
| `npm run check` | все проверки, как в CI |
| `npm run check:integration` | + интеграционные тесты pgvector |
| `npm run fix` | автоисправление и форматирование |
| `npm run eval` | прогон golden-набора RAG |
| `npm run sync` | синхронизация с GitHub и облачными агентами |

## Документация

Индекс: [docs/README.md](docs/README.md). Для агентов Cursor: [AGENTS.md](AGENTS.md).

- [Границы этапов](docs/product/scope-and-stages.md) · [Дорожная карта](docs/product/roadmap.md)
- [Архитектура](docs/architecture/overview.md) · [Решения (ADR)](docs/adr/README.md)
- [RAG](docs/rag/README.md) · [Дизайн](docs/design/README.md)
- [Railway](docs/ops/railway.md) · [GitHub и CI](docs/ops/github.md) · [Настройка Cursor](docs/ops/cursor.md)

## Стек

Python 3.12 · FastAPI · ARQ + Redis · PostgreSQL + pgvector · LangChain · OpenRouter · React + TypeScript + Vite · Railway.

## Структура

```text
backend/    FastAPI, worker, RAG, тесты, evals
frontend/   Telegram Mini App
docs/       документация
scripts/    команды для разработки (Node)
.cursor/    правила, скилы, агенты, хуки для Cursor
```

Proprietary — внутренний продукт.
