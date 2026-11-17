import { useEffect } from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { AdminPage } from "./pages/AdminPage";
import { AnalysisPage } from "./pages/AnalysisPage";
import { CapturePage } from "./pages/CapturePage";
import { OnboardingPage } from "./pages/OnboardingPage";
import { ResultPage } from "./pages/ResultPage";
import "./styles/tokens.css";

export default function App() {
  useEffect(() => {
    const tg = window.Telegram?.WebApp;
    tg?.ready();
    tg?.expand();
    const scheme = tg?.colorScheme;
    if (scheme === "light") {
      document.documentElement.style.setProperty("--cheiro-bg", "#f7f4ef");
      document.documentElement.style.setProperty("--cheiro-surface", "#ffffff");
      document.documentElement.style.setProperty("--cheiro-text", "#12131a");
      document.documentElement.style.setProperty("--cheiro-muted", "#5d5a54");
    }
  }, []);

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<OnboardingPage />} />
        <Route path="/capture" element={<CapturePage />} />
        <Route path="/analysis" element={<AnalysisPage />} />
        <Route path="/result" element={<ResultPage />} />
        <Route path="/admin" element={<AdminPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}