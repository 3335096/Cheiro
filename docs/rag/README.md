# RAG — конвейер и качество

RAG на профессиональной литературе — сердце CHEIRO. Здесь описано, как он устроен и как мы измеряем качество.

## Конвейер

```text
EPUB/PDF → извлечение текста → очистка → чанкинг → эмбеддинги → pgvector
запрос → эмбеддинг запроса → top-k по косинусной близости → промпт + контекст → LLM → ответ + источники
```

| Шаг | Реализация | Параметры |
|-----|------------|-----------|
| Извлечение | `app/rag/extract.py`: EPUB (ebooklib), PDF с текстом (pypdf); скан → OCR-адаптер | порог «нужен OCR»: < 400 символов |
| Чанкинг | `app/rag/chunking.py`, `RecursiveCharacterTextSplitter` | `RAG_CHUNK_SIZE=1000`, `RAG_CHUNK_OVERLAP=150` |
| Эмбеддинги | `app/rag/embeddings.py`, OpenRouter, батч 100 | `EMBEDDING_MODEL`, размерность 1536 |
| Поиск | `app/rag/retrieve.py`, `<=>` (косинус) | `RAG_TOP_K=8` |
| Генерация | `app/rag/pipeline.py`, `app/rag/llm.py` | `LLM_MODEL`, системный промпт `app/rag/prompts/system_default.txt` |

## Принципы качества

- Ответ опирается на найденные фрагменты; если данных мало, ответ говорит об этом.
- Ответ на языке запроса (RU/EN). У каждой книги задан язык.
- Хиромантия подаётся как интерпретация, без медицинских и категоричных утверждений.
- Любая правка, влияющая на ответы, измеряется до и после (`npm run eval`), по одному рычагу за раз.

## Измерение

- Golden-набор: [`backend/evals/rag_golden.json`](../../backend/evals/rag_golden.json). Поля: `query`, `language`, `expected_source_titles`, `must_include`, `must_not_include`.
- Запуск: `npm run eval` (нужны БД с проиндексированными книгами и `OPENROUTER_API_KEY`). Отчёт сохраняется в [`docs/eval/`](../eval/README.md).
- Автопроверки: `cited` (есть источники), `retrieval` (ожидаемые книги найдены), `include`, `exclude`. Они ловят очевидное; ответы дополнительно читаются вручную.
- Эксперименты записываются в [experiments.md](experiments.md). Корпус: [corpus.md](corpus.md).

## Что запланировано

- Prompt Studio в админке: промпт и модель из БД с историей версий.
- Фильтр retrieval по языку; индекс HNSW при росте корпуса.
- OCR-провайдер для PDF-сканов.
