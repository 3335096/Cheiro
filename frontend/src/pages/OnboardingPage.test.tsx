import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { describe, expect, it } from "vitest";
import { OnboardingPage } from "./OnboardingPage";

describe("OnboardingPage", () => {
  it("shows the brand and leads the user to photo capture", async () => {
    render(
      <MemoryRouter initialEntries={["/"]}>
        <Routes>
          <Route path="/" element={<OnboardingPage />} />
          <Route path="/capture" element={<p>capture screen</p>} />
        </Routes>
      </MemoryRouter>,
    );

    expect(screen.getByLabelText("CHEIRO")).toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: /начать анализ/i }));

    expect(screen.getByText("capture screen")).toBeInTheDocument();
  });
});
