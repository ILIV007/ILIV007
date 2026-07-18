/**
 * knight-emblem.ts — a HAND-DRAWN crusader great helm rendered as a
 * self-typing monochrome ASCII SVG.
 *
 * CRITICAL: CANVAS_W is ODD (39) and every art row has ODD content width,
 * so every row centers EXACTLY on column 19. This is what makes the
 * silhouette symmetric and clean — even-width rows shift by half a char
 * and break the shape.
 *
 * The helmet is a filled silhouette (not an outline): plumed dome, crusader
 * cross on the forehead, a wide horizontal eye-slit, symmetric breath holes,
 * and a flared gorget. Widths transition smoothly (5→7→9→11→13→15 dome,
 * 15 body, 19 gorget) so the outline is clean.
 *
 * The `whoami` prompt lives INSIDE the SVG (first line). Each art row types
 * itself in via a left-to-right SMIL clip wipe with a gold cursor,
 * staggered top to bottom. Plays once and freezes.
 */

// Hand-authored crusader great helm. ONLY the content is written here (no
// manual padding) — the centering code below pads each row to CANVAS_W so
// it's always exactly centered. Every row has ODD content width so it
// centers precisely on column 19 of the 39-wide canvas.
//
// Width map:  plume 5,7,5  →  dome 7,11,13,15  →  body 15  →  gorget 19,17
const KNIGHT_LINES: string[] = [
  "~~~~~",            //  0  plume         w=5
  "~~~~~~~",          //  1  plume         w=7
  "|||||",            //  2  plume stem    w=5
  ".-|||-.",          //  3  dome top      w=7
  ".---|||---.",      //  4  dome          w=11
  ".----|||----.",    //  5  dome          w=13
  "/-----|||-----\\", //  6  dome edge     w=15  ← body width starts
  "|@@@@@@@@@@@@@|",  //  7  body          w=15
  "|@@@@@@@@@@@@@|",  //  8
  "|@@@@@@+@@@@@@|",  //  9  cross         w=15  (+ at center)
  "|@@@@@@+@@@@@@|",  // 10  cross
  "|@@@@@@@@@@@@@|",  // 11
  "|@@@@@@@@@@@@@|",  // 12
  "|@@@@@@@@@@@@@|",  // 13
  "|@@@@@@@@@@@@@|",  // 14
  "|=============|",  // 15  EYE SLIT      w=15
  "|=============|",  // 16  EYE SLIT
  "|@@@@@@@@@@@@@|",  // 17
  "|@@@:@@:@@:@@@|",  // 18  breath holes  w=15  (colons at 3,6,9)
  "|@@@@@@@@@@@@@|",  // 19
  "|@@@@@@@@@@@@@|",  // 20
  "\\@@@@@@@@@@@/",   // 21  narrowing     w=13
  ".---@@@@@@@@@@@---.", // 22  gorget top    w=19  ← flares out
  "|@@@@@@@@@@@@@@@@@|", // 23  gorget        w=19
  "|@@@@@@@@@@@@@@@@@|", // 24
  "|@@@@@@@@@@@@@@@@@|", // 25
  "\\@@@@@@@@@@@@@@@/", // 26  gorget bottom w=17
];

const CANVAS_W = 39; // ODD — so odd-width rows center exactly

// Center + pad each row to CANVAS_W. Since CANVAS_W is odd and every content
// row is odd-width, (CANVAS_W - w) is even → left === right → perfect center.
const ART: string[] = KNIGHT_LINES.map((r) => {
  const w = r.length;
  const left = Math.floor((CANVAS_W - w) / 2);
  return " ".repeat(left) + r + " ".repeat(CANVAS_W - left - w);
});

const PROMPT_ROW = 0;
const ART_START_ROW = 2;
const TOTAL_ROWS = ART_START_ROW + ART.length; // 2 + 27 = 29

const CHAR_W = 10;
const CHAR_H = 13;
export const KNIGHT_W = CANVAS_W * CHAR_W; // 390
export const KNIGHT_H = TOTAL_ROWS * CHAR_H; // 377

const FILL = "#c8b5ff"; // light violet
const BG = "#0d1117";
const CURSOR = "#e3b341"; // knight gold
const PURPLE = "#bc8cff";
const MUTED = "#8b949e";
const FG = "#c9d1d9";

let cache: string | null = null;

function esc(s: string): string {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

export function makeKnightSvg(username?: string): string {
  if (cache) return cache;
  const user = (username || "ILIV007").replace(/[<>"]/g, "").slice(0, 24);

  const rowStagger = 0.035;
  const rowDur = 0.28;
  const startDelay = 0.2;

  const clips: string[] = [];
  const texts: string[] = [];
  const cursors: string[] = [];

  for (let r = 0; r < ART.length; r++) {
    const begin = (startDelay + r * rowStagger).toFixed(3);
    const y = (ART_START_ROW + r) * CHAR_H;
    const line = ART[r];

    clips.push(
      `<clipPath id="ke${r}"><rect x="0" y="${y.toFixed(2)}" width="0" height="${CHAR_H.toFixed(2)}"><animate attributeName="width" from="0" to="${KNIGHT_W}" begin="${begin}s" dur="${rowDur}s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.25 0.1 0.25 1"/></rect></clipPath>`
    );

    texts.push(
      `<text x="0" y="${(y + 1.5).toFixed(2)}" clip-path="url(#ke${r})" textLength="${KNIGHT_W}" lengthAdjust="spacingAndGlyphs">${esc(line)}</text>`
    );

    const cxEnd = KNIGHT_W - 2;
    cursors.push(
      `<rect x="0" y="${(y + 1).toFixed(2)}" width="3" height="${(CHAR_H - 2).toFixed(2)}" fill="${CURSOR}" opacity="0"><animate attributeName="x" from="0" to="${cxEnd}" begin="${begin}s" dur="${rowDur}s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.25 0.1 0.25 1"/><animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.12;0.82;1" begin="${begin}s" dur="${rowDur}s" fill="freeze"/></rect>`
    );
  }

  // Prompt line (row 0) — colored tspans, appears instantly
  const promptY = PROMPT_ROW * CHAR_H + 1.5;
  const promptText = `<text x="0" y="${promptY.toFixed(2)}" font-size="13"><tspan fill="${PURPLE}">${esc(user)}@github</tspan><tspan fill="${MUTED}"> ~ $ </tspan><tspan fill="${FG}">whoami</tspan><tspan fill="${CURSOR}"> _</tspan></text>`;

  const svg = `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="${KNIGHT_W}" height="${KNIGHT_H}" viewBox="0 0 ${KNIGHT_W} ${KNIGHT_H}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
  <rect width="${KNIGHT_W}" height="${KNIGHT_H}" fill="${BG}"/>
  ${promptText}
  <defs>
    ${clips.join("\n    ")}
  </defs>
  <g font-size="12" fill="${FILL}" dominant-baseline="hanging" shape-rendering="crispEdges">
    ${texts.join("\n    ")}
  </g>
  <g>
    ${cursors.join("\n    ")}
  </g>
  <title>${esc(user)} — knight emblem</title>
</svg>`;

  cache = svg;
  return svg;
}

export function invalidateKnightCache() {
  cache = null;
}
