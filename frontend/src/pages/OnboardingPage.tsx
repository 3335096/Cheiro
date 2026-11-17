import { useNavigate } from "react-router-dom";
import { BrandMark } from "../components/BrandMark";
import "./pages.css";

export function OnboardingPage() {
  const navigate = useNavigate();

  return (
    <main className="page">
      <header className="page-header">
        <BrandMark />
      </header>
      <section className="hero-copy">
        <h1>Точная хиромантия на основе профессиональных источников</h1>
        <p>
          CHEIRO анализирует линии ладони и сопоставляет наблюдения с индексированной
          библиотекой (RU/EN). Это не медицинский диагноз — формат осмысленного отчёта.
        </p>
      </section>
      <button type="button" className="btn-primary" onClick={() => navigate("/capture")}>
        Начать анализ
      </button>
    </main>
  );
}