import React from "react";
import { createRoot } from "react-dom/client";
import { act } from "react-dom/test-utils";
import { describe, expect, it } from "vitest";
import { PipelineJsonInspector } from "./PipelineJsonInspector";

function render(element: React.ReactElement) {
  const host = document.createElement("div");
  document.body.appendChild(host);
  const root = createRoot(host);
  act(() => root.render(element));
  return { host, root };
}

describe("PipelineJsonInspector", () => {
  it("renders summary first and keeps JSON collapsed", () => {
    const { host, root } = render(
      React.createElement(PipelineJsonInspector, {
        title: "Planning Pipeline JSON",
        summary: "Planning summary.",
        data: { artifact: { ok: true } },
      }),
    );

    expect(host.textContent).toContain("Planning summary.");
    expect(host.textContent).toContain("View JSON");
    expect(host.textContent).not.toContain('"artifact"');
    act(() => root.unmount());
  });

  it("expands and renders pretty JSON", () => {
    const { host, root } = render(
      React.createElement(PipelineJsonInspector, {
        title: "Runtime Pipeline JSON",
        summary: "Runtime summary.",
        data: { execution_log: { status: "complete" } },
      }),
    );

    const button = Array.from(host.querySelectorAll("button")).find((node) => node.textContent?.includes("View JSON"));
    act(() => button?.dispatchEvent(new MouseEvent("click", { bubbles: true })));

    expect(host.textContent).toContain("Hide JSON");
    expect(host.textContent).toContain('"execution_log"');
    expect(host.textContent).toContain('"complete"');
    act(() => root.unmount());
  });

  it("handles empty data", () => {
    const { host, root } = render(
      React.createElement(PipelineJsonInspector, {
        title: "Outcomes & Provenance JSON",
        data: {},
      }),
    );

    expect(host.textContent).toContain("No pipeline JSON is available yet.");
    act(() => root.unmount());
  });
});
