import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { createAnalysis, getAnalysis } from "./client";

function mockFetch(body: unknown, ok = true) {
  const fetchMock = vi.fn().mockResolvedValue({
    ok,
    json: async () => body,
    text: async () => JSON.stringify(body),
  });
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

describe("api client", () => {
  beforeEach(() => {
    window.Telegram = { WebApp: { initData: "signed-init-data", ready: vi.fn(), expand: vi.fn() } };
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    delete window.Telegram;
  });

  it("sends Telegram init data when polling job status", async () => {
    const fetchMock = mockFetch({ job_id: "1", status: "queued" });

    await getAnalysis("1");

    const [, init] = fetchMock.mock.calls[0];
    expect(init.headers["X-Telegram-Init-Data"]).toBe("signed-init-data");
  });

  it("posts the photo and locale when creating an analysis", async () => {
    const fetchMock = mockFetch({ job_id: "1", status: "queued" });

    await createAnalysis("BASE64", "en");

    const [url, init] = fetchMock.mock.calls[0];
    expect(String(url)).toContain("/api/analysis");
    expect(JSON.parse(init.body)).toEqual({ image_base64: "BASE64", locale: "en" });
  });

  it("surfaces server errors", async () => {
    mockFetch({ detail: "nope" }, false);

    await expect(getAnalysis("1")).rejects.toThrow("nope");
  });
});
