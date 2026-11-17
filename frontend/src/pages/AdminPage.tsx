import { useEffect, useState, type FormEvent } from "react";
import { BrandMark } from "../components/BrandMark";
import { adminListSources, adminUploadSource } from "../api/client";
import "./pages.css";

type SourceRow = {
  id: string;
  title: string;
  author?: string;
  language: string;
  filename: string;
  status: string;
  error_message?: string;
};

export function AdminPage() {
  const [token, setToken] = useState(() => localStorage.getItem("cheiro.adminToken") ?? "");
  const [sources, setSources] = useState<SourceRow[]>([]);
  const [message, setMessage] = useState<string | null>(null);

  const refresh = async () => {
    if (!token) return;
    const data = await adminListSources(token);
    setSources(data);
  };

  useEffect(() => {
    refresh().catch((e) => setMessage(String(e)));
  }, [token]);

  const onUpload = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const form = new FormData(e.currentTarget);
    const file = form.get("file") as File;
    if (!file || !token) return;
    setMessage("Загрузка…");
    try {
      await adminUploadSource(token, file, {
        title: String(form.get("title") ?? ""),
        author: String(form.get("author") ?? "") || undefined,
        language: String(form.get("language") ?? "ru"),
      });
      setMessage("Книга поставлена в очередь индексации");
      await refresh();
      e.currentTarget.reset();
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Ошибка");
    }
  };

  return (
    <main className="page admin">
      <header className="page-header">
        <BrandMark />
        <span className="admin-tag">Admin</span>
      </header>
      <label className="field">
        Admin API token
        <input
          value={token}
          onChange={(e) => {
            setToken(e.target.value);
            localStorage.setItem("cheiro.adminToken", e.target.value);
          }}
          placeholder="X-Admin-Token"
        />
      </label>

      <form className="upload-form" onSubmit={onUpload}>
        <h3>База знаний</h3>
        <label className="field">
          Название
          <input name="title" required />
        </label>
        <label className="field">
          Автор
          <input name="author" />
        </label>
        <label className="field">
          Язык
          <select name="language" defaultValue="ru">
            <option value="ru">RU</option>
            <option value="en">EN</option>
          </select>
        </label>
        <label className="field">
          Файл (EPUB/PDF)
          <input name="file" type="file" accept=".epub,.pdf" required />
        </label>
        <button className="btn-primary" type="submit" disabled={!token}>
          Загрузить и индексировать
        </button>
      </form>

      {message && <p className="muted">{message}</p>}

      <section className="source-list">
        <h3>Источники</h3>
        {sources.map((s) => (
          <article key={s.id} className="source-card">
            <strong>{s.title}</strong>
            <span>
              {s.language.toUpperCase()} · {s.status}
            </span>
            {s.error_message && <small className="error">{s.error_message}</small>}
          </article>
        ))}
      </section>
    </main>
  );
}