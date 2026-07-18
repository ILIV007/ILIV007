/**
 * activity-feed.ts — a LIVE GitHub activity feed rendered as an animated
 * terminal log SVG.
 *
 * Scrapes the public events API at
 *   https://api.github.com/users/<username>/events/public
 * (no token, no auth). Renders the last ~6 events as terminal log lines
 * that fade+slide in. The `tail -f activity.log` prompt lives INSIDE the
 * SVG. 5-min cache. Falls back to demo events if rate-limited.
 */

export interface ActivityData {
  username: string;
  events: { type: string; repo: string; createdAt: string; detail: string }[];
  source: "live" | "demo";
}

const W = 860;
const H = 230;
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

const cache = new Map<string, { t: number; data: ActivityData }>();
const CACHE_TTL = 1000 * 60 * 5;

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

function formatEvent(raw: any) {
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

function demoEvents(username: string) {
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

export async function fetchActivity(username: string): Promise<ActivityData> {
  const key = username.trim().toLowerCase();
  const cached = cache.get(key);
  if (cached && Date.now() - cached.t < CACHE_TTL) return cached.data;

  const url = `https://api.github.com/users/${encodeURIComponent(key)}/events/public`;
  try {
    const res = await fetch(url, {
      headers: { Accept: "application/vnd.github+json", "User-Agent": "ILIV007-profile-readme" },
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const raw = (await res.json()) as any[];
    if (!Array.isArray(raw) || raw.length === 0) throw new Error("no events");
    const events = [];
    for (const e of raw) {
      const f = formatEvent(e);
      if (f) events.push(f);
      if (events.length >= 6) break;
    }
    if (events.length === 0) throw new Error("no parseable events");
    const data: ActivityData = { username: key, events, source: "live" };
    cache.set(key, { t: Date.now(), data });
    return data;
  } catch {
    const data: ActivityData = { username: key, events: demoEvents(key), source: "demo" };
    cache.set(key, { t: Date.now(), data });
    return data;
  }
}

function esc(s: string): string {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

export function renderActivitySvg(data: ActivityData): string {
  const user = data.username;
  const events = data.events.slice(0, 6);
  const sourceTag = data.source === "live" ? "live" : "demo";

  const titleBarH = 30;
  const padX = 22;
  const lineH = 24;
  const promptY = titleBarH + 26;
  const logStartY = promptY + 22;

  const prompt = `<text x="${padX}" y="${promptY}" font-family="${FONT}" font-size="14" font-weight="700"><tspan fill="${PURPLE}">${esc(user)}@github</tspan><tspan fill="${MUTED}"> ~ $ </tspan><tspan fill="${FG}">tail -f activity.log</tspan><tspan fill="${GOLD}"> ▮</tspan></text>`;

  const lines: string[] = [];
  let delay = 0.3;
  const stagger = 0.12;
  const dur = 0.4;

  events.forEach((e, i) => {
    const y = logStartY + i * lineH;
    const t = timeAgo(e.createdAt);
    const isOwn = e.repo.toLowerCase().startsWith(user.toLowerCase() + "/");
    const repoColor = isOwn ? GOLD : LAVENDER;
    lines.push(
      `<g class="logline" style="animation-delay:${delay.toFixed(2)}s"><text x="${padX}" y="${y}" font-family="${FONT}" font-size="13"><tspan fill="${MUTED}">[${esc(t)}]</tspan> <tspan fill="${GREEN}">${esc(e.detail)}</tspan> <tspan fill="${repoColor}">${esc(e.repo)}</tspan></text></g>`
    );
    delay += stagger;
  });

  const badgeColor = data.source === "live" ? GREEN : GOLD;
  const badge = `<text x="${W - 22}" y="${titleBarH - 10}" text-anchor="end" font-family="${FONT}" font-size="11" fill="${badgeColor}">● ${sourceTag}</text>`;

  return `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" font-family="${FONT}">
  <style>
    .logline { opacity: 0; animation: al ${dur}s cubic-bezier(0.22,0.61,0.36,1) forwards; }
    @keyframes al { from { opacity: 0; transform: translateX(-10px); } to { opacity: 1; transform: translateX(0); } }
    @media (prefers-reduced-motion: reduce) { .logline { opacity: 1; animation: none; transform: none; } }
  </style>
  <rect x="0.5" y="0.5" width="${W - 1}" height="${H - 1}" rx="8" ry="8" fill="${BG}" stroke="${BORDER}" stroke-width="1"/>
  <path d="M0.5 8 a8 8 0 0 1 8 -7.5 H${W - 8.5} a8 8 0 0 1 8 7.5 V${titleBarH} H0.5 Z" fill="${TITLE_BG}"/>
  <line x1="0.5" y1="${titleBarH}" x2="${W - 0.5}" y2="${titleBarH}" stroke="${BORDER}" stroke-width="1"/>
  <circle cx="14" cy="15" r="5" fill="#ff5f56"/>
  <circle cx="30" cy="15" r="5" fill="#ffbd2e"/>
  <circle cx="46" cy="15" r="5" fill="#27c93f"/>
  <text x="${W / 2}" y="19.5" text-anchor="middle" font-family="${FONT}" font-size="12" fill="${MUTED}">${esc(user)}@github — activity.log</text>
  ${badge}
  ${prompt}
  ${lines.join("\n  ")}
  <title>Live activity for ${esc(user)}</title>
</svg>`;
}

export { W as ACT_W, H as ACT_H };
