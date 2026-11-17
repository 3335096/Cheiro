const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

function telegramInitData(): string {
  return window.Telegram?.WebApp?.initData ?? "";
}

export async function createAnalysis(imageBase64: string, locale = "ru") {
  const res = await fetch(`${API_URL}/api/analysis`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Telegram-Init-Data": telegramInitData(),
    },
    body: JSON.stringify({ image_base64: imageBase64, locale }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json() as Promise<{ job_id: string; status: string }>;
}

export async function getAnalysis(jobId: string) {
  const res = await fetch(`${API_URL}/api/analysis/${jobId}`, {
    headers: { "X-Telegram-Init-Data": telegramInitData() },
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json() as Promise<{
    job_id: string;
    status: string;
    teaser?: string;
    error_message?: string;
  }>;
}

export async function adminListSources(token: string) {
  const res = await fetch(`${API_URL}/api/admin/sources`, {
    headers: { "X-Admin-Token": token },
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function adminUploadSource(
  token: string,
  file: File,
  meta: { title: string; author?: string; language: string },
) {
  const form = new FormData();
  form.append("title", meta.title);
  if (meta.author) form.append("author", meta.author);
  form.append("language", meta.language);
  form.append("file", file);
  const res = await fetch(`${API_URL}/api/admin/sources`, {
    method: "POST",
    headers: { "X-Admin-Token": token },
    body: form,
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
