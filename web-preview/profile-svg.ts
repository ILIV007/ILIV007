/**
 * profile-svg.ts — ONE combined SVG containing the entire profile:
 * a single terminal window with the activity feed at top, then the
 * knight emblem (rect-based, left) and the neofetch info card (right)
 * side by side — all in ONE coordinate system, ONE frame.
 *
 * No separate images, no floating HTML prompt text. The README just
 * embeds this single SVG. Prompts (`tail -f activity.log`, `whoami`)
 * live inside as colored <text> tspans.
 *
 * The knight is rendered with RECT cells (pixel-exact, font-independent)
 * so it's always solid and recognizable. The info card uses <text> (small
 * label text, acceptable if slightly inconsistent across fonts).
 */

// ── activity fetch (inlined, no separate module) ────────────────────────
interface GithubEvent {
  type: string;
  repo: string;
  createdAt: string;
  detail: string;
}
interface ActivityData {
  username: string;
  events: GithubEvent[];
  source: "live" | "demo";
}

const actCache = new Map<string, { t: number; data: ActivityData }>();
const ACT_CACHE_TTL = 1000 * 60 * 5;

function formatEvent(raw: any): GithubEvent | null {
  const type = raw.type;
  const repo = raw.repo?.name || "unknown";
  const created = raw.created_at;
  let detail = "";
  const p = raw.payload || {};
  switch (type) {
    case "PushEvent": detail = `pushed ${p.size || p.commits?.length || 1} commit(s) to`; break;
    case "WatchEvent": detail = "starred"; break;
    case "CreateEvent": detail = `created ${p.ref_type || "branch"} in`; break;
    case "ForkEvent": detail = "forked"; break;
    case "IssuesEvent": detail = `${p.action || "opened"} issue in`; break;
    case "PullRequestEvent": detail = `${p.action || "opened"} PR in`; break;
    case "ReleaseEvent": detail = "released"; break;
    case "PublicEvent": detail = "made public"; break;
    case "DeleteEvent": detail = `deleted ${p.ref_type || "branch"} in`; break;
    case "IssueCommentEvent": detail = "commented in"; break;
    default: detail = "activity in";
  }
  return { type, repo, createdAt: created, detail };
}

function demoEvents(username: string): GithubEvent[] {
  const now = Date.now();
  const mins = (m: number) => new Date(now - m * 60000).toISOString();
  return [
    { type: "PushEvent", repo: `${username}/ILIV007`, createdAt: mins(47), detail: "pushed 3 commit(s) to" },
    { type: "WatchEvent", repo: "vercel/next.js", createdAt: mins(180), detail: "starred" },
    { type: "CreateEvent", repo: `${username}/ILIV007`, createdAt: mins(320), detail: "created branch in" },
    { type: "PullRequestEvent", repo: `${username}/ILIV007`, createdAt: mins(720), detail: "opened PR in" },
    { type: "IssuesEvent", repo: `${username}/ILIV007`, createdAt: mins(1440), detail: "opened issue in" },
    { type: "ForkEvent", repo: "shadcn-ui/ui", createdAt: mins(2880), detail: "forked" },
  ];
}

async function fetchActivity(username: string): Promise<ActivityData> {
  const key = username.trim().toLowerCase();
  const cached = actCache.get(key);
  if (cached && Date.now() - cached.t < ACT_CACHE_TTL) return cached.data;

  const url = `https://api.github.com/users/${encodeURIComponent(key)}/events/public`;
  try {
    const res = await fetch(url, {
      headers: { Accept: "application/vnd.github+json", "User-Agent": "ILIV007-profile-readme" },
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const raw = (await res.json()) as any[];
    if (!Array.isArray(raw) || raw.length === 0) throw new Error("no events");
    const events: GithubEvent[] = [];
    for (const e of raw) {
      const f = formatEvent(e);
      if (f) events.push(f);
      if (events.length >= 6) break;
    }
    if (events.length === 0) throw new Error("no parseable events");
    const data: ActivityData = { username: key, events, source: "live" };
    actCache.set(key, { t: Date.now(), data });
    return data;
  } catch {
    const data: ActivityData = { username: key, events: demoEvents(key), source: "demo" };
    actCache.set(key, { t: Date.now(), data });
    return data;
  }
}

// ── layout ──────────────────────────────────────────────────────────────
const W = 860;
const PAD = 24;
const TITLE_BAR_H = 32;

// activity section
const ACT_PROMPT_Y = TITLE_BAR_H + 26;
const ACT_LINE_H = 24;
const ACT_LINES = 6;
const ACT_SECTION_H = 30 + ACT_LINES * ACT_LINE_H + 12; // prompt + lines + pad

// divider
const DIVIDER_Y = TITLE_BAR_H + ACT_SECTION_H + 16;

// whoami section
const WHO_PROMPT_Y = DIVIDER_Y + 24;
const CONTENT_Y = WHO_PROMPT_Y + 28;

// knight (rect-based) — left
const KNIGHT_COLS = 25;
const KNIGHT_ROWS = 23;
const CELL = 13;
const GAP = 2;
const PITCH = CELL + GAP; // 15
const KNIGHT_W = KNIGHT_COLS * PITCH; // 375
const KNIGHT_H = KNIGHT_ROWS * PITCH; // 345
const KNIGHT_X = PAD;

// info card — right
const CARD_X = PAD + KNIGHT_W + 20; // 24+375+20 = 419
const CARD_W = W - CARD_X - PAD;     // 860-419-24 = 417

const H = CONTENT_Y + Math.max(KNIGHT_H, 360) + PAD; // total

// ── colors ──────────────────────────────────────────────────────────────
const BG = "#0d1117";
const TITLE_BG = "#161b22";
const BORDER = "#30363d";
const FG = "#c9d1d9";
const MUTED = "#8b949e";
const GOLD = "#e3b341";
const PURPLE = "#bc8cff";
const LAVENDER = "#d2a8ff";
const GREEN = "#39d353";
const FONT = "'Courier New', Courier, monospace";

// knight density → fill
const DENSITY_FILL: Record<string, string> = {
  " ": "transparent",
  ".": "#2d1b4e",
  ":": "#4c1d95",
  "-": "#5b21b6",
  "+": "#e3b341",
  "=": "#c4b5fd",
  "@": "#a855f7",
  "#": "#9333ea",
  "|": "#6d28d9",
  "/": "#6d28d9",
  "\\": "#6d28d9",
  "~": "#7c3aed",
  "^": "#8b5cf6",
};

// ── knight art (hand-drawn crusader great helm) ─────────────────────────
const KNIGHT_ART: string[] = [
  "        .  :  .        ",
  "         :::::         ",
  "          ...          ",
  "        .-:::-.        ",
  "       .---::---.      ",
  "       /----::----\\   ",
  "       |@@@@@@@@@@@@@| ",
  "       |@@@@@@+@@@@@@| ",
  "       |@@@@@@+@@@@@@| ",
  "       |@@@@@@@@@@@@@| ",
  "       |@@@@@@@@@@@@@| ",
  "       |@@@@@@@@@@@@@| ",
  "       |@@@@@@@@@@@@@| ",
  "       |=============| ",
  "       |=============| ",
  "       |@@@@@@@@@@@@@| ",
  "       |@@:@@:@@:@@:@| ",
  "       |@@@@@@@@@@@@@| ",
  "        \\@@@@@@@@@@@/  ",
  "    .---@@@@@@@@@@@---.",
  "    |@@@@@@@@@@@@@@@@@|",
  "    |@@@@@@@@@@@@@@@@@|",
  "     \\@@@@@@@@@@@@@@@/ ",
];

function esc(s: string): string {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const m = Math.floor(diff / 60000);
  if (m < 1) return "just now";
  if (m < 60) return `${m}m ago`;
  const h = Math.floor(m / 60);
  if (h < 24) return `${h}h ago`;
  const d = Math.floor(h / 24);
  if (d < 7) return `${d}d ago`;
  return `${Math.floor(d / 7)}w ago`;
}

// ── knight rects ────────────────────────────────────────────────────────
function buildKnightRects(): { clips: string[]; cells: string[]; cursors: string[] } {
  const clips: string[] = [];
  const cellGroups: string[] = [];
  const cursors: string[] = [];

  const rowStagger = 0.04;
  const rowDur = 0.28;
  const startDelay = 0.4;

  for (let r = 0; r < KNIGHT_ROWS; r++) {
    const row = (KNIGHT_ART[r] + " ".repeat(KNIGHT_COLS)).slice(0, KNIGHT_COLS);
    const begin = (startDelay + r * rowStagger).toFixed(3);
    const y = r * PITCH;

    clips.push(
      `<clipPath id="kr${r}"><rect x="${KNIGHT_X}" y="${(CONTENT_Y + y).toFixed(2)}" width="0" height="${PITCH}"><animate attributeName="width" from="0" to="${KNIGHT_W}" begin="${begin}s" dur="${rowDur}s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.25 0.1 0.25 1"/></rect></clipPath>`
    );

    const rowCells: string[] = [];
    for (let c = 0; c < KNIGHT_COLS; c++) {
      const ch = row[c];
      const fill = DENSITY_FILL[ch] ?? "transparent";
      if (fill === "transparent") continue;
      rowCells.push(
        `<rect x="${(KNIGHT_X + c * PITCH).toFixed(2)}" y="${(CONTENT_Y + y).toFixed(2)}" width="${CELL}" height="${CELL}" rx="2" fill="${fill}"/>`
      );
    }
    cellGroups.push(`<g clip-path="url(#kr${r})">${rowCells.join("")}</g>`);

    const cxEnd = KNIGHT_X + KNIGHT_W - 3;
    cursors.push(
      `<rect x="${KNIGHT_X}" y="${(CONTENT_Y + y + 1).toFixed(2)}" width="4" height="${PITCH - 2}" fill="${GOLD}" opacity="0"><animate attributeName="x" from="${KNIGHT_X}" to="${cxEnd}" begin="${begin}s" dur="${rowDur}s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.25 0.1 0.25 1"/><animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.12;0.82;1" begin="${begin}s" dur="${rowDur}s" fill="freeze"/></rect>`
    );
  }

  return { clips, cells: cellGroups, cursors };
}

// ── info card content ───────────────────────────────────────────────────
function buildInfoCard(user: string): string[] {
  const groups: string[] = [];
  const x = CARD_X + 16;
  let y = CONTENT_Y + 6;
  const lineH = 24;
  let delay = 0.5;
  const stagger = 0.1;
  const dur = 0.4;

  const rows: { text: string }[] = [
    { text: `<tspan fill="${GOLD}">◆</tspan>  <tspan fill="${FG}" font-weight="700" font-size="16">ILIYA</tspan>` },
    { text: `<tspan fill="${GOLD}">class   </tspan><tspan fill="${LAVENDER}">developer</tspan>` },
    { text: `<tspan fill="${GOLD}">level   </tspan><tspan fill="${LAVENDER}">?? · quest just begun</tspan>` },
    { text: `<tspan fill="${GOLD}">stack   </tspan><tspan fill="${LAVENDER}">learning · building</tspan>` },
    { text: `<tspan fill="${GOLD}">channel </tspan><tspan fill="${LAVENDER}">ILIVIR3</tspan>` },
    { text: `<tspan fill="${MUTED}" font-style="italic">  "start small, stay curious"</tspan>` },
    { text: `<tspan fill="${GOLD}">guild   </tspan><tspan fill="${LAVENDER}">github.com/${esc(user)}</tspan>` },
  ];

  for (const r of rows) {
    groups.push(
      `<g class="cardline" style="animation-delay:${delay.toFixed(2)}s"><text x="${x}" y="${y.toFixed(1)}" font-family="${FONT}" font-size="13" font-weight="600">${r.text}</text></g>`
    );
    y += lineH;
    delay += stagger;
  }
  return groups;
}

// ── activity feed lines ─────────────────────────────────────────────────
function buildActivityLines(data: ActivityData, user: string): string[] {
  const lines: string[] = [];
  const x = PAD;
  let y = ACT_PROMPT_Y + 22;
  const baseDelay = 0.3;
  const stagger = 0.12;
  const dur = 0.4;

  data.events.slice(0, ACT_LINES).forEach((e, i) => {
    const delay = (baseDelay + i * stagger).toFixed(2);
    const time = timeAgo(e.createdAt);
    const isOwn = e.repo.toLowerCase().startsWith(user.toLowerCase() + "/");
    const repoColor = isOwn ? GOLD : LAVENDER;
    lines.push(
      `<g class="logline" style="animation-delay:${delay}s"><text x="${x}" y="${y.toFixed(1)}" font-family="${FONT}" font-size="13"><tspan fill="${MUTED}">[${esc(time)}]</tspan> <tspan fill="${GREEN}">${esc(e.detail)}</tspan> <tspan fill="${repoColor}">${esc(e.repo)}</tspan></text></g>`
    );
    y += ACT_LINE_H;
  });
  return lines;
}

// ── main ────────────────────────────────────────────────────────────────
let cache: { key: string; svg: string } | null = null;

export async function makeProfileSvg(username: string): Promise<string> {
  const user = (username || "ILIV007").replace(/[<>"]/g, "").slice(0, 24);
  const cacheKey = `${user}`;
  if (cache && cache.key === cacheKey) return cache.svg;

  const activityData = await fetchActivity(user);
  const sourceTag = activityData.source === "live" ? "live" : "demo";
  const badgeColor = activityData.source === "live" ? GREEN : GOLD;

  const knight = buildKnightRects();
  const cardLines = buildInfoCard(user);
  const actLines = buildActivityLines(activityData, user);

  // prompts (inside the SVG)
  const actPrompt = `<text x="${PAD}" y="${ACT_PROMPT_Y.toFixed(1)}" font-family="${FONT}" font-size="14" font-weight="700"><tspan fill="${PURPLE}">${esc(user)}@github</tspan><tspan fill="${MUTED}"> ~ $ </tspan><tspan fill="${FG}">tail -f activity.log</tspan><tspan fill="${GOLD}"> ▮</tspan></text>`;

  const whoPrompt = `<text x="${PAD}" y="${WHO_PROMPT_Y.toFixed(1)}" font-family="${FONT}" font-size="14" font-weight="700"><tspan fill="${PURPLE}">${esc(user)}@github</tspan><tspan fill="${MUTED}"> ~ $ </tspan><tspan fill="${FG}">whoami</tspan></text>`;

  const divider = `<line x1="${PAD}" y1="${DIVIDER_Y}" x2="${W - PAD}" y2="${DIVIDER_Y}" stroke="${BORDER}" stroke-width="1" stroke-dasharray="3 4"/>`;

  const svg = `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H.toFixed(0)}" viewBox="0 0 ${W} ${H.toFixed(0)}">
  <style>
    .logline, .cardline { opacity: 0; animation: fadeIn 0.4s cubic-bezier(0.22,0.61,0.36,1) forwards; }
    @keyframes fadeIn { from { opacity: 0; transform: translateX(-8px); } to { opacity: 1; transform: translateX(0); } }
    @media (prefers-reduced-motion: reduce) { .logline, .cardline { opacity: 1; animation: none; transform: none; } }
  </style>
  <!-- frame -->
  <rect x="0.5" y="0.5" width="${W - 1}" height="${(H - 1).toFixed(0)}" rx="10" ry="10" fill="${BG}" stroke="${BORDER}" stroke-width="1"/>
  <!-- title bar -->
  <path d="M0.5 10 a10 10 0 0 1 10 -9.5 H${W - 10.5} a10 10 0 0 1 10 9.5 V${TITLE_BAR_H} H0.5 Z" fill="${TITLE_BG}"/>
  <line x1="0.5" y1="${TITLE_BAR_H}" x2="${W - 0.5}" y2="${TITLE_BAR_H}" stroke="${BORDER}" stroke-width="1"/>
  <circle cx="16" cy="16" r="5" fill="#ff5f56"/>
  <circle cx="33" cy="16" r="5" fill="#ffbd2e"/>
  <circle cx="50" cy="16" r="5" fill="#27c93f"/>
  <text x="${W / 2}" y="20.5" text-anchor="middle" font-family="${FONT}" font-size="12" fill="${MUTED}">${esc(user)}@github — profile</text>
  <text x="${W - 18}" y="20.5" text-anchor="end" font-family="${FONT}" font-size="11" fill="${badgeColor}">● ${sourceTag}</text>

  <!-- activity section -->
  ${actPrompt}
  ${actLines.join("\n  ")}

  <!-- divider -->
  ${divider}

  <!-- whoami section -->
  ${whoPrompt}

  <!-- knight (rect-based, left) -->
  <g transform="translate(0,0)">
    <defs>${knight.clips.join("\n      ")}</defs>
    ${knight.cells.join("\n    ")}
    ${knight.cursors.join("\n    ")}
  </g>

  <!-- info card (right) -->
  ${cardLines.join("\n  ")}

  <title>${esc(user)} — GitHub profile</title>
</svg>`;

  cache = { key: cacheKey, svg };
  return svg;
}

export const PROFILE_W = W;
export const PROFILE_H = H;
