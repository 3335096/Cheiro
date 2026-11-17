import { useNavigate } from "react-router-dom";
import { BrandMark } from "../components/BrandMark";
import "./pages.css";

export function ResultPage() {
  const navigate = useNavigate();
  const teaser = sessionStorage.getItem("cheiro.teaser") ?? "Ваш отчёт формируется…";

  return (
    <main className="page">
      <header className="page-header">
        <BrandMark size="sm" />
      </header>
      <h2>Ваш фрагмент отчёта</h2>
      <article className="teaser-card">{teaser}</article>
      <p className="muted">
        Полная версия отправляется в чат с ботом CHEIRO (этап 1 — без оплаты, для тестирования
        качества RAG).
      </p>
      <button type="button" className="btn-secondary" onClick={() => navigate("/")}>
        Новый анализ
      </button>
    </main>
  );
}