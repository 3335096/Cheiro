import "./BrandMark.css";

export function BrandMark({ size = "md" }: { size?: "sm" | "md" }) {
  return (
    <div className={`brand brand-${size}`} aria-label="CHEIRO">
      <span className="brand-word">CHEIRO</span>
      <span className="brand-dot" />
    </div>
  );
}