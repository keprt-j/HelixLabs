import { describe, expect, it } from "vitest";
import { inferSeriesKeys } from "./chartBinding";

describe("inferSeriesKeys", () => {
  it("prefers explicit x_key and y_key", () => {
    const result = inferSeriesKeys({
      x_key: "dose",
      y_key: "score",
      dose: [1, 2, 3],
      score: [0.3, 0.4, 0.6],
      x: [10, 20, 30],
      y: [1, 2, 3],
    });
    expect(result).toEqual({ xKey: "dose", yKey: "score" });
  });
});
