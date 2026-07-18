/**
 * render_heatmap_svg.ts — renders the contribution calendar as a 53×7 grid
 * of rounded boxes on a violet ramp. Diagonal CSS-keyframe reveal, month/
 * day labels, Less→More legend, stats footer. Purple theme (no green).
 */

import type { ContributionData } from "./contributions";

export const HM_W = 860;
export const HM_H = 196;

const LEFT = 40;
const TOP = 30;
const CELL = 12;
const GAP = 3;
const PITCH = CELL + GAP;
const BG = "#0d1117";
const BORDER = "#30363d";
const FG = "#c9d1d9";
const MUTED = "#8b949e";

// violet ramp (none -> brightest)
const PALETTE = [
  "#161b22",
  "#2d1b4e",
  "#4c1d95",
  "#7c3aed",
  "#a855f7",
  "#c4b5fd",
];

const MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
const DAY_LABELS = ["", "Mon", "", "Wed", "", "Fri", ""];

function fmt(n: number): string {
  return n.toLocaleString("en-US");
}
function esc(s: string): string {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function levelFor(count: number): number {
  if (count <= 0) return 0;
  if (count <= 3) return 1;
  if (count <= 7) return 2;
  if (count <= 12) return 3;
  if (count <= 19) return 4;
  return 5;
}

export function renderHeatmapSvg(data: ContributionData): string {
  const days = data.days;
  if (days.length === 0) return emptySvg();
  const first = new Date(days[0].date + "T00:00:00Z");
  const firstDow = first.getUTCDay();
  const firstMs = first.getTime();
  const DAY = 86400000;

  const cells: string[] = [];
  const monthLabels: string[] = [];
  let prevMonth = -1;

  for (const d of days) {
    const dt = new Date(d.date + "T00:00:00Z");
    const dow = dt.getUTCDay();
    const daysSince = Math.round((dt.getTime() - firstMs) / DAY);
    const week = Math.floor((daysSince + firstDow) / 7);
    const x = LEFT + week * PITCH;
    const y = TOP + dow * PITCH;
    const lvl = levelFor(d.count);
    const fill = PALETTE[lvl];
    const delay = (0.1 + (week + dow) * 0.01).toFixed(3);
    cells.push(
      `<g class="cell" style="animation-delay:${delay}s"><rect x="${x.toFixed(1)}" y="${y.toFixed(1)}" width="${CELL}" height="${CELL}" rx="2.5" ry="2.5" fill="${fill}"><title>${d.date}: ${d.count}</title></rect></g>`
    );
    const m = dt.getUTCMonth();
    if (dow <= 1 && m !== prevMonth && week >= 0) {
      monthLabels.push(`<text x="${x.toFixed(1)}" y="${(TOP - 8).toFixed(1)}" font-size="11" fill="${MUTED}">${MONTHS[m]}</text>`);
      prevMonth = m;
    }
  }

  const dayLabelEls: string[] = [];
  for (let i = 0; i < 7; i++) {
    if (!DAY_LABELS[i]) continue;
    dayLabelEls.push(`<text x="${(LEFT - 8).toFixed(1)}" y="${(TOP + i * PITCH + CELL - 2).toFixed(1)}" text-anchor="end" font-size="10" fill="${MUTED}">${DAY_LABELS[i]}</text>`);
  }

  const legendY = TOP + 7 * PITCH + 18;
  const legendX = HM_W - 30 - PALETTE.length * (CELL + 4);
  const legendCells: string[] = [];
  for (let i = 0; i < PALETTE.length; i++) {
    legendCells.push(`<rect x="${(legendX + i * (CELL + 4)).toFixed(1)}" y="${legendY.toFixed(1)}" width="${CELL}" height="${CELL}" rx="2.5" ry="2.5" fill="${PALETTE[i]}"/>`);
  }

  const s = data.stats;
  const sourceTag = data.source === "live" ? "live" : "demo";
  const footerLeft =
    `<text x="40" y="${(legendY + CELL - 1).toFixed(1)}" font-size="12" fill="${FG}">` +
    `<tspan fill="#c4b5fd" font-weight="700">${fmt(s.total)}</tspan> contributions in the last year` +
    `  ·  current streak <tspan fill="#bc8cff">${s.currentStreak}d</tspan>` +
    `  ·  longest <tspan fill="#bc8cff">${s.longestStreak}d</tspan>` +
    `  ·  best day <tspan fill="#e3b341">${s.bestDay ? fmt(s.bestDay.count) : 0}</tspan>` +
    `</text>`;
  const legendText =
    `<text x="${(legendX - 8).toFixed(1)}" y="${(legendY + CELL - 1).toFixed(1)}" text-anchor="end" font-size="11" fill="${MUTED}">Less</text>` +
    `<text x="${(legendX + PALETTE.length * (CELL + 4) + 4).toFixed(1)}" y="${(legendY + CELL - 1).toFixed(1)}" font-size="11" fill="${MUTED}">More</text>`;
  const userTag =
    `<text x="${HM_W - 30}" y="${(TOP - 8).toFixed(1)}" text-anchor="end" font-size="11" fill="${MUTED}">${esc(data.username)} · ${sourceTag}</text>`;

  return `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="${HM_W}" height="${HM_H}" viewBox="0 0 ${HM_W} ${HM_H}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
  <style>
    .cell { opacity: 0; animation: cellIn 0.45s ease-out forwards; transform-box: fill-box; transform-origin: center; }
    @keyframes cellIn { from { opacity: 0; transform: translateY(-4px) scale(0.5); } to { opacity: 1; transform: translateY(0) scale(1); } }
    @media (prefers-reduced-motion: reduce) { .cell { opacity: 1; animation: none; transform: none; } }
  </style>
  <rect x="0.5" y="0.5" width="${HM_W - 1}" height="${HM_H - 1}" rx="8" ry="8" fill="${BG}" stroke="${BORDER}" stroke-width="1"/>
  ${userTag}
  ${monthLabels.join("\n  ")}
  ${dayLabelEls.join("\n  ")}
  ${cells.join("\n  ")}
  ${legendText}
  ${legendCells.join("\n  ")}
  ${footerLeft}
  <title>Contribution heatmap for ${esc(data.username)}</title>
</svg>`;
}

function emptySvg(): string {
  return `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="${HM_W}" height="${HM_H}" viewBox="0 0 ${HM_W} ${HM_H}"><rect width="${HM_W}" height="${HM_H}" fill="${BG}"/><text x="${HM_W/2}" y="${HM_H/2}" text-anchor="middle" fill="${MUTED}">no data</text></svg>`;
}
