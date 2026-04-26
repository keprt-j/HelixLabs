import React from "react";
import { createRoot } from "react-dom/client";
import { act } from "react-dom/test-utils";
import { describe, expect, it, vi } from "vitest";
import { LiteratureReviewLive } from "./LiteratureReviewLive";

describe("LiteratureReviewLive", () => {
  it("renders a home button and invokes onHomeClick", async () => {
    const onHomeClick = vi.fn();
    const onProceedToDashboard = vi.fn();
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => ({
        ok: true,
        json: async () => ({
          run: {
            pipeline: {
              intake: {
                literature: { studies: [] },
                prior_work: { novelty_score: 0 },
              },
            },
          },
        }),
      })),
    );

    const host = document.createElement("div");
    document.body.appendChild(host);
    const root = createRoot(host);

    await act(async () => {
      root.render(
        React.createElement(LiteratureReviewLive, {
          experiment: "Optimize LLZO conductivity",
          runId: "RUN-1",
          onHomeClick,
          onProceedToDashboard,
        }),
      );
      await Promise.resolve();
      await Promise.resolve();
    });

    const home = Array.from(host.querySelectorAll("button")).find((node) => node.textContent?.includes("Home"));
    expect(home).toBeTruthy();
    act(() => home?.dispatchEvent(new MouseEvent("click", { bubbles: true })));
    expect(onHomeClick).toHaveBeenCalledTimes(1);

    act(() => root.unmount());
    vi.unstubAllGlobals();
  });
});
