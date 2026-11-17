import { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { BrandMark } from "../components/BrandMark";
import "./pages.css";

export function CapturePage() {
  const navigate = useNavigate();
  const inputRef = useRef<HTMLInputElement>(null);
  const [preview, setPreview] = useState<string | null>(null);

  const onFile = (file: File | undefined) => {
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      const dataUrl = reader.result as string;
      setPreview(dataUrl);
      sessionStorage.setItem("cheiro.capture", dataUrl.split(",")[1] ?? "");
    };
    reader.readAsDataURL(file);
  };

  return (
    <main className="page">
      <header className="page-header">
        <BrandMark size="sm" />
        <span className="step">Шаг 1 из 2</span>
      </header>
      <h2>Сфотографируйте ладонь</h2>
      <p className="muted">Поместите ладонь в рамку. Фото не сохраняется на сервере.</p>

      <div className="palm-frame" onClick={() => inputRef.current?.click()}>
        {preview ? (
          <img src={preview} alt="Превью ладони" className="palm-preview" />
        ) : (
          <div className="palm-guide">
            <div className="palm-outline" />
            <span>Нажмите, чтобы сделать снимок</span>
          </div>
        )}
      </div>

      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        capture="environment"
        hidden
        onChange={(e) => onFile(e.target.files?.[0])}
      />

      <button
        type="button"
        className="btn-primary"
        disabled={!preview}
        onClick={() => navigate("/analysis")}
      >
        Продолжить
      </button>
    </main>
  );
}