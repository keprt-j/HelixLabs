import { describe, expect, it } from "vitest";
import { computeMae, parseCsvPairs } from "./csvSeries";

describe("csvSeries", () => {
  it("parses simple csv x,y pairs", () => {
    const rows = parseCsvPairs("x,y\n1,2\n2,4\n3,8");
    expect(rows).toEqual([
      { x: 1, y: 2 },
      { x: 2, y: 4 },
      { x: 3, y: 8 },
    ]);
  });

  it("computes mae over overlapping x", () => {
    const mae = computeMae(
      [
        { x: 1, y: 2 },
        { x: 2, y: 4 },
      ],
      [
        { x: 1, y: 3 },
        { x: 2, y: 2 },
      ],
    );
    expect(mae).toBe(1.5);
  });
});
