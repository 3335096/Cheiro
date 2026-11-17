# Выкладка на Railway

Чек-лист для первых тестов. Деплой, секреты и изменения продакшена выполняет владелец; репозиторий содержит Dockerfile и этот runbook.

> Статус: инструкция составлена по устройству проекта, но на самом Railway ещё не проверялась. При первом деплое уточните названия настроек в интерфейсе Railway и обновите документ.

## Сервисы проекта

| Сервис | Источник | Root Directory | Команда запуска |
|--------|----------|----------------|-----------------|
| `postgres` | шаблон Postgres с pgvector или образ `pgvector/pgvector:pg16` с томом | — | — |
| `redis` | Redis из каталога Railway | — | — |
| `api` | репозиторий GitHub | `backend` | по умолчанию (`CMD` в Dockerfile, учитывает `$PORT`) |
| `worker` | тот же репозиторий | `backend` | `arq app.worker.WorkerSettings` (задать в Settings → Deploy → Custom Start Command) |
| `frontend` | тот же репозиторий | `frontend` | по умолчанию (nginx слушает `$PORT`) |
| `admin` | после появления `admin/` | `admin` | по умолчанию |

Для `api` задайте Healthcheck Path `/health`. Для `worker` healthcheck не задавайте (HTTP-порта нет).

## Переменные окружения

Задаются в Railway Variables (не в репозитории). Значения не присылайте в чат.

| Переменная | Сервисы | Значение |
|------------|---------|----------|
| `DEBUG` | api, worker | `false` |
| `ADMIN_API_TOKEN` | api, worker | случайная строка 24+ символов |
| `TELEGRAM_BOT_TOKEN` | api, worker | токен из @BotFather |
| `TELEGRAM_WEBAPP_URL` | api | публичный HTTPS-адрес сервиса `frontend` |
| `OPENROUTER_API_KEY` | api, worker | ключ OpenRouter |
| `LLM_MODEL`, `EMBEDDING_MODEL` | api, worker | по необходимости (по умолчанию в `.env.example`) |
| `DATABASE_URL` | api, worker | ссылка на переменную Postgres (`postgresql://…`; приложение само заменит драйвер на asyncpg) |
| `REDIS_URL` | api, worker | ссылка на переменную Redis |
| `OCR_PROVIDER`, `PALM_CV_API_URL` | api, worker | по мере подключения |
| `VITE_API_URL` | frontend | публичный HTTPS-адрес сервиса `api`; нужна на этапе сборки образа |

При `DEBUG=false` приложение откажется стартовать с небезопасным `ADMIN_API_TOKEN` или без `TELEGRAM_BOT_TOKEN`: так и задумано.

В Postgres должно быть доступно расширение `vector`; приложение выполняет `CREATE EXTENSION IF NOT EXISTS vector` при старте, учётной записи нужны на это права.

## Порядок выкладки

1. Убедитесь, что `main` зелёный в CI.
2. Создайте проект, добавьте `postgres` и `redis`.
3. Добавьте `api` и `worker`, задайте переменные, дождитесь успешного старта.
4. Добавьте `frontend` с `VITE_API_URL`. Затем впишите его адрес в `TELEGRAM_WEBAPP_URL` у `api` и перезапустите `api`.
5. В @BotFather укажите адрес `frontend` как Web App бота.
6. Включите автодеплой из `main` (после первого ручного успешного деплоя).

## Проверка после выкладки

1. `GET <api>/health` → `{"status":"ok"}`.
2. Логи `worker`: подключился к Redis и БД, нет ошибок.
3. Загрузите книгу через админку: статус доходит до `ready`.
4. В Telegram: бот открывает Mini App; проходит сценарий «фото → статусы → тизер → полный отчёт в боте».
5. В логах нет изображений и base64.

## Откат

В Railway откатите деплой сервиса на предыдущую успешную версию. Изменения схемы БД откатываются только если миграция обратима, поэтому перед первым продакшеном нужны миграции Alembic (см. дорожную карту).
