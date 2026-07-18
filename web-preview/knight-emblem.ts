/**
 * knight-emblem.ts — a detailed knight helmet rendered as a self-typing
 * monochrome ASCII SVG.
 *
 * Source: a generated high-contrast knight-helmet photo (dark steel on pure
 * white). It is run through sharp (greyscale -> CLAHE local-contrast boost ->
 * normalise) and downsampled to a character grid. Each pixel's brightness
 * picks a glyph from a DENSE ramp full of letters and symbols — this is what
 * gives the emblem its detailed, "hand-crafted with many characters" feel
 * while still reading clearly as a knight helmet.
 *
 * Monochrome light-violet fill (purple theme). Each row "types" itself in via
 * a left-to-right SMIL clip wipe with a gold cursor riding the edge,
 * staggered top to bottom. Plays once and freezes.
 */

import sharp from "sharp";
import path from "path";
import fs from "fs";

// bright (sparse) -> dark (dense). Short, high-contrast ramp: the helmet
// body maps to the dense @/# end so the silhouette reads bold even at
// small render sizes. XML-safe (no < > & " `).
const RAMP = " .:-=+*#%@".split("");

export const ASCII_COLS = 80;
export const ASCII_ROWS = 40;
const CHAR_W = 4.0;
const CHAR_H = 8.0;
export const KNIGHT_W = ASCII_COLS * CHAR_W; // 384
export const KNIGHT_H = ASCII_ROWS * CHAR_H; // 384

const FILL = "#c8b5ff"; // light violet — purple theme
const BG = "#0d1117";
const CURSOR = "#e3b341"; // knight gold

const SOURCE = path.join(
  process.cwd(),
  "public",
  "assets",
  "knight-angled.png"
);
let cache: string | null = null;

async function buildGrid(): Promise<string[]> {
  if (!fs.existsSync(SOURCE)) {
    throw new Error("knight source not found: " + SOURCE);
  }
  const { data, info } = await sharp(SOURCE)
    .resize(512, 512, { fit: "cover", position: "center" })
    .greyscale()
    .normalise()
    .trim({ background: "#ffffff", threshold: 10 }) // crop white border → helmet fills canvas
    .resize(ASCII_COLS, ASCII_ROWS, { fit: "contain", background: "#ffffff" }) // preserve aspect, pad white
    .raw()
    .toBuffer({ resolveWithObject: true });

  const ch = info.channels;

  // 1) read brightness grid + binarize. Threshold at 140: anything darker
  //    is helmet (0), anything lighter is background/feature (255). This
  //    kills all background noise so only the helmet silhouette prints.
  const THRESH = 140;
  const bin: number[] = new Array(ASCII_COLS * ASCII_ROWS);
  for (let y = 0; y < ASCII_ROWS; y++) {
    for (let x = 0; x < ASCII_COLS; x++) {
      const b = data[(y * ASCII_COLS + x) * ch];
      bin[y * ASCII_COLS + x] = b < THRESH ? 0 : 255;
    }
  }

  // 2) morphological "inside" mask: a pixel is inside the helmet if any
  //    pixel within radius R is black (0). This fills the white visor slit
  //    and breath holes with characters so the helmet reads as a solid shape,
  //    while the real background (no black neighbours) stays blank.
  const R = 1;
  const inside: boolean[] = new Array(ASCII_COLS * ASCII_ROWS);
  for (let y = 0; y < ASCII_ROWS; y++) {
    for (let x = 0; x < ASCII_COLS; x++) {
      let hasBlack = false;
      for (let dy = -R; dy <= R && !hasBlack; dy++) {
        for (let dx = -R; dx <= R && !hasBlack; dx++) {
          const nx = x + dx, ny = y + dy;
          if (nx < 0 || ny < 0 || nx >= ASCII_COLS || ny >= ASCII_ROWS) continue;
          if (bin[ny * ASCII_COLS + nx] === 0) hasBlack = true;
        }
      }
      inside[y * ASCII_COLS + x] = hasBlack;
    }
  }

  // 3) map to ramp. Background (not inside, white) → blank. Inside helmet
  //    → use the ORIGINAL brightness (not binarized) so there's still some
  //    character variation for a rich, hand-crafted feel.
  const orig: number[] = new Array(ASCII_COLS * ASCII_ROWS);
  for (let y = 0; y < ASCII_ROWS; y++) {
    for (let x = 0; x < ASCII_COLS; x++) {
      orig[y * ASCII_COLS + x] = data[(y * ASCII_COLS + x) * ch];
    }
  }

  const rows: string[] = [];
  for (let y = 0; y < ASCII_ROWS; y++) {
    let line = "";
    for (let x = 0; x < ASCII_COLS; x++) {
      const i = y * ASCII_COLS + x;
      const isIn = inside[i];
      let idx: number;
      if (!isIn) {
        idx = 0; // background → blank
      } else {
        // inside the helmet: use original brightness for variation.
        // Push hard toward the dense end so the body reads as a bold silhouette.
        const b = orig[i];
        let t = (255 - b) / 255; // 0 bright .. 1 dark
        t = Math.pow(t, 0.5); // strong push toward dense
        idx = Math.min(RAMP.length - 1, Math.floor(t * (RAMP.length - 1) + 0.5));
        if (idx < 4) idx = 4; // interior uses at least '#' density
      }
      line += RAMP[idx];
    }
    rows.push(line);
  }
  return rows;
}

function esc(s: string): string {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

export async function makeKnightSvg(): Promise<string> {
  if (cache) return cache;
  const rows = await buildGrid();

  const rowStagger = 0.028;
  const rowDur = 0.32;
  const startDelay = 0.15;

  const clips: string[] = [];
  const texts: string[] = [];
  const cursors: string[] = [];

  for (let r = 0; r < rows.length; r++) {
    const begin = (startDelay + r * rowStagger).toFixed(3);
    const y = r * CHAR_H;
    const line = rows[r];

    clips.push(
      `<clipPath id="ke${r}"><rect x="0" y="${y.toFixed(
        2
      )}" width="0" height="${CHAR_H.toFixed(
        2
      )}"><animate attributeName="width" from="0" to="${KNIGHT_W}" begin="${begin}s" dur="${rowDur}s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.25 0.1 0.25 1"/></rect></clipPath>`
    );

    texts.push(
      `<text x="0" y="${(y + 1.5).toFixed(
        2
      )}" clip-path="url(#ke${r})" textLength="${KNIGHT_W}" lengthAdjust="spacingAndGlyphs">${esc(
        line
      )}</text>`
    );

    const cxEnd = KNIGHT_W - 2;
    cursors.push(
      `<rect x="0" y="${(y + 1).toFixed(2)}" width="2.4" height="${(CHAR_H - 2).toFixed(
        2
      )}" fill="${CURSOR}" opacity="0"><animate attributeName="x" from="0" to="${cxEnd}" begin="${begin}s" dur="${rowDur}s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.25 0.1 0.25 1"/><animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.12;0.82;1" begin="${begin}s" dur="${rowDur}s" fill="freeze"/></rect>`
    );
  }

  const svg = `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="${KNIGHT_W}" height="${KNIGHT_H}" viewBox="0 0 ${KNIGHT_W} ${KNIGHT_H}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
  <rect width="${KNIGHT_W}" height="${KNIGHT_H}" fill="${BG}"/>
  <defs>
    ${clips.join("\n    ")}
  </defs>
  <g font-size="8" fill="${FILL}" dominant-baseline="hanging" shape-rendering="crispEdges">
    ${texts.join("\n    ")}
  </g>
  <g>
    ${cursors.join("\n    ")}
  </g>
  <title>ILIV007 — knight emblem</title>
</svg>`;

  cache = svg;
  return svg;
}

export function invalidateKnightCache() {
  cache = null;
}
