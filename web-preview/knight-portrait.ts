/**
 * knight-portrait.ts — a professional ASCII portrait of a knight helmet,
 * rendered from a generated photo via the image→ASCII pipeline.
 *
 * Pipeline (same as the original portrait version):
 *   sharp: greyscale → CLAHE (local contrast) → normalise → threshold/binarize
 *   → morphological "inside" fill (fills visor/breath holes) → char ramp
 *
 * The knight is rendered as <text> with a monospace font. font-size is set
 * directly on each <text> element AND on the <svg> root for maximum
 * compatibility. NO textLength (it distorts glyphs). The `whoami` prompt
 * is the first line inside the SVG.
 *
 * Each row "types" itself in via a left-to-right SMIL clip wipe with a gold
 * cursor, staggered top to bottom. Plays once, freezes.
 */

import sharp from "sharp";
import path from "path";
import fs from "fs";

// ASCII density ramp: bright (sparse) → dark (dense).
// Uses letters + symbols for a rich, artistic portrait feel.
const RAMP = " .'`,:-=+*rcs#%@".split("");

const COLS = 90;
const ROWS = 44;
const FONT_SIZE = 11;
// Empirical: Courier New at font-size 11 → ~6.6px per char advance.
const CHAR_W = 6.6;
const CHAR_H = 11;
const W = Math.round(COLS * CHAR_W); // 594 → but we want ~400
// Scale down: use a viewBox and let the SVG scale.
const SVG_W = 400;
const SVG_H = ROWS * CHAR_H + 30; // 44*11+30 = 514 → scale to fit

const FILL = "#c8b5ff"; // light violet
const BG = "#0d1117";
const CURSOR = "#e3b341";
const PURPLE = "#bc8cff";
const MUTED = "#8b949e";
const FG = "#c9d1d9";
const FONT = "'Courier New', Courier, monospace";

const SOURCE = path.join(process.cwd(), "public", "assets", "knight-portrait.png");
let cache: string | null = null;

async function buildGrid(): Promise<string[]> {
  if (!fs.existsSync(SOURCE)) throw new Error("knight source not found: " + SOURCE);

  const { data, info } = await sharp(SOURCE)
    .resize(600, 600, { fit: "cover", position: "center" })
    .greyscale()
    .clahe({ width: 8, height: 8, maxSlope: 6 })
    .normalise()
    .resize(COLS, ROWS, { fit: "fill" })
    .raw()
    .toBuffer({ resolveWithObject: true });

  const ch = info.channels;

  // Read brightness
  const bright: number[] = new Array(COLS * ROWS);
  for (let y = 0; y < ROWS; y++) {
    for (let x = 0; x < COLS; x++) {
      bright[y * COLS + x] = data[(y * COLS + x) * ch];
    }
  }

  // Binarize: helmet (dark < threshold) vs background (light)
  // Use a threshold that separates the dark helmet from the light bg.
  const THRESH = 130;
  const binary: number[] = bright.map((b) => (b < THRESH ? 0 : 255));

  // Morphological "inside" mask: a pixel is inside the helmet if any pixel
  // within radius R is dark. This fills visor slits and breath holes so
  // the helmet reads as a solid shape.
  const R = 1;
  const inside: boolean[] = new Array(COLS * ROWS);
  for (let y = 0; y < ROWS; y++) {
    for (let x = 0; x < COLS; x++) {
      let hasDark = false;
      for (let dy = -R; dy <= R && !hasDark; dy++) {
        for (let dx = -R; dx <= R && !hasDark; dx++) {
          const nx = x + dx, ny = y + dy;
          if (nx < 0 || ny < 0 || nx >= COLS || ny >= ROWS) continue;
          if (binary[ny * COLS + nx] === 0) hasDark = true;
        }
      }
      inside[y * COLS + x] = hasDark;
    }
  }

  // Map to ramp: background → space, inside helmet → density char
  const rows: string[] = [];
  for (let y = 0; y < ROWS; y++) {
    let line = "";
    for (let x = 0; x < COLS; x++) {
      const i = y * COLS + x;
      if (!inside[i]) {
        line += RAMP[0]; // background → blank
      } else {
        const b = bright[i];
        let t = (255 - b) / 255;
        t = Math.pow(t, 0.6); // push toward dense for solid silhouette
        const idx = Math.min(RAMP.length - 1, Math.floor(t * (RAMP.length - 1) + 0.5));
        line += RAMP[Math.max(2, idx)]; // interior at least '-
      }
    }
    rows.push(line);
  }
  return rows;
}

function esc(s: string): string {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

export async function makeKnightPortraitSvg(username?: string): Promise<string> {
  if (cache) return cache;
  const user = (username || "ILIV007").replace(/[<>"]/g, "").slice(0, 24);
  const rows = await buildGrid();

  const rowStagger = 0.022;
  const rowDur = 0.25;
  const startDelay = 0.2;
  const promptH = 24;

  const clips: string[] = [];
  const texts: string[] = [];
  const cursors: string[] = [];

  for (let r = 0; r < rows.length; r++) {
    const begin = (startDelay + r * rowStagger).toFixed(3);
    const y = promptH + r * CHAR_H;
    const line = rows[r];

    clips.push(
      `<clipPath id="kp${r}"><rect x="0" y="${y}" width="0" height="${CHAR_H}"><animate attributeName="width" from="0" to="${SVG_W}" begin="${begin}s" dur="${rowDur}s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.25 0.1 0.25 1"/></rect></clipPath>`
    );

    texts.push(
      `<text x="0" y="${y + 1}" font-family="${FONT}" font-size="${FONT_SIZE}" clip-path="url(#kp${r})">${esc(line)}</text>`
    );

    const cxEnd = SVG_W - 2;
    cursors.push(
      `<rect x="0" y="${y}" width="2" height="${CHAR_H - 1}" fill="${CURSOR}" opacity="0"><animate attributeName="x" from="0" to="${cxEnd}" begin="${begin}s" dur="${rowDur}s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.25 0.1 0.25 1"/><animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.12;0.82;1" begin="${begin}s" dur="${rowDur}s" fill="freeze"/></rect>`
    );
  }

  // Prompt line (row 0)
  const promptText = `<text x="0" y="16" font-family="${FONT}" font-size="${FONT_SIZE + 2}" font-weight="700"><tspan fill="${PURPLE}">${esc(user)}@github</tspan><tspan fill="${MUTED}"> ~ $ </tspan><tspan fill="${FG}">whoami</tspan><tspan fill="${CURSOR}"> ▮</tspan></text>`;

  const totalH = promptH + rows.length * CHAR_H + 8;

  const svg = `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="${SVG_W}" height="${totalH}" viewBox="0 0 ${SVG_W} ${totalH}" font-family="${FONT}" font-size="${FONT_SIZE}">
  <rect width="${SVG_W}" height="${totalH}" fill="${BG}"/>
  ${promptText}
  <defs>
    ${clips.join("\n    ")}
  </defs>
  <g fill="${FILL}" dominant-baseline="hanging">
    ${texts.join("\n    ")}
  </g>
  <g>
    ${cursors.join("\n    ")}
  </g>
  <title>${esc(user)} — knight portrait</title>
</svg>`;

  cache = svg;
  return svg;
}

export function invalidateKnightCache() {
  cache = null;
}
