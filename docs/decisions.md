# CHEIRO — зафиксированные решения (v1)

Документ дополняет `tz-v1.md` ответами заказчика. Стек выбран так, чтобы **не менять** его на этапах масштабирования.

## Продукт и бренд

| Параметр | Значение |
|----------|----------|
| Бренд | **CHEIRO** |
| Тип | Telegram Mini App + бот |
| География v1 | РФ (архитектурно — мультиязычность RU/EN в корпусе и UI) |

## Фазы

### Этап 1 (текущий фокус)

- RAG Foundation: 3–5 книг, EPUB/PDF, RU + EN.
- Один тип отчёта по хиромантии (без платежей).
- Telegram: бот и Mini App **с нуля**.
- Admin: полноценный UI (не «голый» SQLAdmin).
- CV линий руки: **заглушка / контракт API** до выбора подрядчика; качество ядра — RAG + промпты + UX.
- Astro, CloudPayments, юрлицо — **не в v1**.

### Этап 2

- Платежи (CloudPayments), CRM **zhivo.crm** (webhooks).
- Astro как дополнение к отчётам.
- Несколько типов отчётов, free/paid, апсейлы (совместимость, даты, подписки и т.д.).

## Инфраструктура

| Компонент | Выбор |
|-----------|--------|
| Хостинг prod | **Railway** |
| Локальная разработка | Docker Compose (те же образы, что на Railway) |
| PostgreSQL | **pgvector** (единый кластер: users, jobs, chunks, embeddings) |
| Очередь | Redis + **ARQ** (лёгкий async worker, мало moving parts) |
| Backend | **Python 3.12 + FastAPI** |
| Frontend TMA | **React 18 + TypeScript + Vite** + `@twa-dev/sdk` |
| RAG | **LangChain** (ingest, split, retrieve); embeddings через OpenAI-compatible API (OpenRouter) |
| OCR | Google Cloud Vision / AWS Textract (переключается env; этап 1 — интерфейс + очередь) |

## Принципы команды

- Разработка **своими силами**, без расширения штата.
- Любая фича должна запускаться локально одной командой `docker compose up`.
- Секреты только в `.env` / Railway variables.

## Интеграции (задел)

- `ZHIVO_CRM_WEBHOOK_URL` — пусто до этапа 2.
- `CLOUDPAYMENTS_*` — пусто до этапа 2.
- `PALM_CV_API_URL` — пусто до подрядчика; worker вызывает noop-адаптер.