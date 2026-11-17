import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { createAnalysis, getAnalysis } from "../api/client";
import { BrandMark } from "../components/BrandMark";
import "./pages.css";

const STATUS_COPY: Record<string, string> = {
  queued: "Подготовка сессии…",
  recognizing: "Распознавание линий",
  searching: "Поиск в архивах CHEIRO",
  generating: "Генерация отчёта",
  done: "Готово",
  failed: "Ошибка",
};

export function AnalysisPage() {
  const navigate = useNavigate();
  const [label, setLabel] = useState("Подготовка…");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const image = sessionStorage.getItem("cheiro.capture");
    if (!image) {
      navigate("/capture", { replace: true });
      return;
    }

    let cancelled = false;
    let timer: number;

    (async () => {
      try {
        const { job_id } = await createAnalysis(image);
        const poll = async () => {
          const job = await getAnalysis(job_id);
          if (cancelled) return;
          setLabel(STATUS_COPY[job.status] ?? job.status);
          if (job.status === "done") {
            sessionStorage.setItem("cheiro.teaser", job.teaser ?? "");
            sessionStorage.setItem("cheiro.report", job.full_report ?? "");
            navigate("/result", { replace: true });
            return;
          }
          if (job.status === "failed") {
            setError(job.error_message ?? "Не удалось сформировать отчёт");
            return;
          }
          timer = window.setTimeout(poll, 1200);
        };
        await poll();
      } catch (e) {
        setError(e instanceof Error ? e.message : "Ошибка запроса");
      }
    })();

    return () => {
      cancelled = true;
      window.clearTimeout(timer);
    };
  }, [navigate]);

  return (
    <main className="page center">
      <BrandMark />
      <div className="scan-anim" aria-hidden />
      <p className="status">{label}</p>
      {error && <p className="error">{error}</p>}
    </main>
  );
}