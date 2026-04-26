export type XYRow = { x: string | number; y: number };

function toNumber(v: string): number | null {
  const n = Number(v.trim());
  return Number.isFinite(n) ? n : null;
}

function maybeNumber(v: string): string | number {
  const n = Number(v.trim());
  return Number.isFinite(n) ? n : v.trim();
}

export function parseCsvPairs(csvText: string): XYRow[] {
  const lines = csvText
    .split(/\r?\n/)
    .map((l) => l.trim())
    .filter(Boolean);
  if (lines.length < 2) return [];

  const header = lines[0].split(",").map((h) => h.trim());
  const rows = lines.slice(1).map((line) => line.split(",").map((c) => c.trim()));

  const numericCounts = header.map((_, colIdx) =>
    rows.reduce((count, row) => (toNumber(row[colIdx] ?? "") == null ? count : count + 1), 0),
  );

  let xCol = 0;
  let yCol = -1;
  for (let i = 0; i < numericCounts.length; i++) {
    if (numericCounts[i] > 0 && i !== xCol) {
      yCol = i;
      break;
    }
  }
  if (yCol < 0) return [];

  const parsed: XYRow[] = [];
  for (const row of rows) {
    const xRaw = row[xCol] ?? "";
    const yRaw = row[yCol] ?? "";
    const y = toNumber(yRaw);
    if (y == null || !xRaw) continue;
    parsed.push({ x: maybeNumber(xRaw), y });
  }
  return parsed;
}

export function computeMae(simulated: XYRow[], uploaded: XYRow[]): number | null {
  if (!simulated.length || !uploaded.length) return null;
  const simMap = new Map(simulated.map((r) => [String(r.x), r.y]));
  const overlaps = uploaded
    .map((r) => {
      const base = simMap.get(String(r.x));
      return base == null ? null : Math.abs(base - r.y);
    })
    .filter((v): v is number => v != null);
  if (!overlaps.length) return null;
  return overlaps.reduce((a, b) => a + b, 0) / overlaps.length;
}
