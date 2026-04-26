import React from "react";
import { createRoot } from "react-dom/client";
import { act } from "react-dom/test-utils";
import { describe, expect, it } from "vitest";
import { ClaimGraphPanel } from "./ClaimGraphPanel";

describe("ClaimGraphPanel", () => {
  it("prefers readable display fields over raw claim fields", () => {
    const host = document.createElement("div");
    document.body.appendChild(host);
    const root = createRoot(host);

    act(() =>
      root.render(
        React.createElement(ClaimGraphPanel, {
          claimGraph: {
            main_claim: "Evidence indicates conductivity, dopant, ionic strongly influences the target outcome.",
            display_main_claim: "Readable main claim about dopant concentration and ionic conductivity.",
            weakest_claim: "Li&lt;sub&gt;7&lt;/sub&gt; raw weak claim",
            display_weakest_claim: "Readable weakest claim about the uncertain stability boundary.",
            next_target: "Raw next target",
            display_next_target: "Readable next target for boundary validation.",
            selected_hypothesis_id: "H1",
            hypotheses: [{ id: "H1", title: "Raw title", statement: "Raw statement" }],
            display_hypotheses: [
              {
                id: "H1",
                title: "Readable hypothesis",
                statement: "Readable hypothesis statement.",
                rationale: "Readable rationale.",
              },
            ],
          },
        }),
      ),
    );

    expect(host.textContent).toContain("Readable main claim about dopant concentration and ionic conductivity.");
    expect(host.textContent).toContain("Readable weakest claim about the uncertain stability boundary.");
    expect(host.textContent).toContain("Readable hypothesis statement.");
    expect(host.textContent).not.toContain("conductivity, dopant, ionic strongly influences");
    act(() => root.unmount());
  });
});
