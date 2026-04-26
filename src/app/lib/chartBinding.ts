function toNumeric(v: unknown): number | null {
  const n = Number(v);
  return Number.isFinite(n) ? n : null;
}

function toScalar(v: unknown): string | number | null {
  if (typeof v === "number" && Number.isFinite(v)) return v;
  if (typeof v === "string") return v;
  return null;
}

function asString(v: unknown): string | null {
  return typeof v === "string" && v.trim().length > 0 ? v.trim() : null;
}

export function inferSeriesKeys(series: Record<string, unknown>): { xKey: string; yKey: string } | null {
  const explicitX = asString(series.x_key);
  const explicitY = asString(series.y_key);
  if (
    explicitX &&
    explicitY &&
    Array.isArray(series[explicitX]) &&
    Array.isArray(series[explicitY]) &&
    (series[explicitX] as unknown[]).length === (series[explicitY] as unknown[]).length
  ) {
    return { xKey: explicitX, yKey: explicitY };
  }

  if (Array.isArray(series.temperature_c) && Array.isArray(series.sigma_S_cm)) {
    return { xKey: "temperature_c", yKey: "sigma_S_cm" };
  }
  if (Array.isArray(series.x) && Array.isArray(series.y)) {
    return { xKey: "x", yKey: "y" };
  }

  const arrayKeys = Object.keys(series).filter((k) => Array.isArray(series[k]));
  const looksXLike = (k: string) => /(^x$|temp|time|dose|fraction|concentration|pressure|speed|index|epoch)/i.test(k);
  const looksYLike = (k: string) => /(^y$|sigma|score|yield|response|objective|accuracy|loss|rate|metric|output)/i.test(k);

  let best: { xKey: string; yKey: string; score: number } | null = null;
  for (let i = 0; i < arrayKeys.length; i++) {
    for (let j = 0; j < arrayKeys.length; j++) {
      if (i === j) continue;
      const xKey = arrayKeys[i];
      const yKey = arrayKeys[j];
      const xa = series[xKey] as unknown[];
      const ya = series[yKey] as unknown[];
      if (!Array.isArray(xa) || !Array.isArray(ya) || xa.length !== ya.length || xa.length === 0) continue;
      const xOk = xa.every((v) => toScalar(v) !== null);
      const yOk = ya.every((v) => toNumeric(v) !== null);
      if (!xOk || !yOk) continue;
      let score = 0;
      if (looksXLike(xKey)) score += 3;
      if (looksYLike(yKey)) score += 3;
      if (!best || score > best.score) best = { xKey, yKey, score };
    }
  }
  return best ? { xKey: best.xKey, yKey: best.yKey } : null;
}
