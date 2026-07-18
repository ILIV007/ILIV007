/**
 * info-card.ts — a minimal, fantasy-flavored neofetch-style info card SVG.
 *
 * Title bar + `ILIV007@github ~ $ summon` prompt (INSIDE the SVG), then
 * ◆ ILIYA (gold) and short key/value rows — class / level / stack /
 * channel / oath / guild. level is "??". channel is ILIVIR3. Each line
 * fades + slides in (CSS keyframes, freeze). Purple + gold palette.
 *
 * Height matches the knight portrait so they align side by side.
 */

const W = 460;
const H = 514; // matches knight portrait height

const BG = "#0d1117";
const TITLE_BG = "#161b22";
const BORDER = "#30363d";
const FG = "#c9d1d9";
const MUTED = "#8b949e";
const GOLD = "#e3b341";
const PURPLE = "#bc8cff";
const LAVENDER = "#d2a8ff";
const FONT = "'Courier New', Courier, monospace";

export function makeInfoCardSvg(opts?: { username?: string }): string {
  const user = (opts?.username || "ILIV007").replace(/[<>"]/g, "").slice(0, 24);

  type Row =
    | { kind: "sep" }
    | { kind: "cmd" }
    | { kind: "name" }
    | { kind: "kv"; key: string; val: string }
    | { kind: "motto"; text: string };

  const rows: Row[] = [
    { kind: "cmd" },
    { kind: "sep" },
    { kind: "name" },
    { kind: "kv", key: "class", val: "developer" },
    { kind: "kv", key: "level", val: "?? · quest just begun" },
    { kind: "kv", key: "stack", val: "learning · building" },
    { kind: "kv", key: "channel", val: "ILIVIR3" },
    { kind: "motto", text: '"start small, stay curious"' },
    { kind: "sep" },
    { kind: "kv", key: "guild", val: `github.com/${user}` },
  ];

  const titleBarH = 30;
  const padX = 22;
  const lineHeight = 26;
  let y = titleBarH + 32;
  const delay = 0.3;
  const stagger = 0.1;
  const dur = 0.4;

  const groups: string[] = [];
  let d = delay;

  for (const r of rows) {
    let inner = "";
    if (r.kind === "sep") {
      inner = `<line x1="${padX}" y1="${y - 9}" x2="${W - padX}" y2="${y - 9}" stroke="${BORDER}" stroke-width="1" stroke-dasharray="2 3"/>`;
    } else if (r.kind === "cmd") {
      inner = `<text x="${padX}" y="${y}" font-family="${FONT}" font-size="13" font-weight="700"><tspan fill="${PURPLE}">${esc(user)}@github</tspan><tspan fill="${MUTED}"> ~ $ </tspan><tspan fill="${FG}">summon</tspan><tspan fill="${GOLD}"> ▮</tspan></text>`;
    } else if (r.kind === "name") {
      inner = `<text x="${padX}" y="${y}" font-family="${FONT}" font-size="18" font-weight="700"><tspan fill="${PURPLE}">◆ </tspan><tspan fill="${GOLD}">ILIYA</tspan></text>`;
    } else if (r.kind === "kv") {
      inner = `<text x="${padX}" y="${y}" font-family="${FONT}" font-size="13"><tspan fill="${GOLD}">${pad(r.key, 8)}</tspan><tspan fill="${LAVENDER}">${esc(r.val)}</tspan></text>`;
    } else if (r.kind === "motto") {
      inner = `<text x="${padX + 8}" y="${y}" font-family="${FONT}" font-size="12" font-style="italic" fill="${MUTED}">${esc(r.text)}</text>`;
    }
    groups.push(`<g class="cardline" style="animation-delay:${d.toFixed(2)}s">${inner}</g>`);
    y += lineHeight;
    d += stagger;
  }

  return `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" font-family="${FONT}">
  <style>
    .cardline { opacity: 0; animation: ci ${dur}s cubic-bezier(0.22,0.61,0.36,1) forwards; }
    @keyframes ci { from { opacity: 0; transform: translateX(-8px); } to { opacity: 1; transform: translateX(0); } }
    @media (prefers-reduced-motion: reduce) { .cardline { opacity: 1; animation: none; transform: none; } }
  </style>
  <rect x="0.5" y="0.5" width="${W - 1}" height="${H - 1}" rx="8" ry="8" fill="${BG}" stroke="${BORDER}" stroke-width="1"/>
  <path d="M0.5 8 a8 8 0 0 1 8 -7.5 H${W - 8.5} a8 8 0 0 1 8 7.5 V${titleBarH} H0.5 Z" fill="${TITLE_BG}"/>
  <line x1="0.5" y1="${titleBarH}" x2="${W - 0.5}" y2="${titleBarH}" stroke="${BORDER}" stroke-width="1"/>
  <circle cx="14" cy="15" r="5" fill="#ff5f56"/>
  <circle cx="30" cy="15" r="5" fill="#ffbd2e"/>
  <circle cx="46" cy="15" r="5" fill="#27c93f"/>
  <text x="${W / 2}" y="19.5" text-anchor="middle" font-family="${FONT}" font-size="12" fill="${MUTED}">${esc(user)}@github — profile</text>
  ${groups.join("\n  ")}
  <title>ILIYA — neofetch card</title>
</svg>`;
}

function esc(s: string): string {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
function pad(s: string, n: number): string {
  return (s + " ".repeat(n)).slice(0, n);
}

export { W as INFOCARD_W, H as INFOCARD_H };
