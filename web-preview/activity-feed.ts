/**
 * activity-feed.ts — a LIVE GitHub activity feed rendered as an animated
 * terminal log SVG.
 *
 * Scrapes the public events API at
 *   https://api.github.com/users/<username>/events/public
 * (no token, no auth — same data the profile page uses). Renders the last
 * ~6 events as terminal log lines that fade+slide in one by one, replacing
 * the contribution heatmap (GitHub already shows that on the profile).
 *
 * The `tail -f activity.log` prompt lives INSIDE the SVG. 5-min cache.
 * Falls back to deterministic demo events if the API is unreachable.
 */

export interface GithubEvent {
  type: string;
  repo: string;
  createdAt: string;
  detail: string;
}

export interface ActivityData {
  username: string;
  events: GithubEvent[];
  source: "live" | "demo";
  fetchedAt: string;
}

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
  const w = Math.floor(d / 7);
  return `${w}w ago`;
}

function formatEvent(raw: any): GithubEvent | null {
  const type = raw.type;
  const repo = raw.repo?.name || "unknown";
  const created = raw.created_at;
  let detail = "";

  switch (type) {
    case "PushEvent":
      const size = raw.payload?.size || raw.payload?.commits?.length || 1;
      detail = `pushed ${size} commit${size === 1 ? "" : "s"} to`;
      break;
    case "WatchEvent":
      detail = "starred";
      break;
    case "CreateEvent":
      const refType = raw.payload?.ref_type || "branch";
      detail = `created ${refType} in`;
      break;
    case "ForkEvent":
      detail = "forked";
      break;
    case "IssuesEvent":
      const action = raw.payload?.action || "opened";
      detail = `${action} issue in`;
      break;
    case "PullRequestEvent":
      const prAction = raw.payload?.action || "opened";
      detail = `${prAction} PR in`;
      break;
    case "ReleaseEvent":
      detail = "released";
      break;
    case "PublicEvent":
      detail = "made public";
      break;
    case "DeleteEvent":
      const delType = raw.payload?.ref_type || "branch";
      detail = `deleted ${delType} in`;
      break;
    case "IssueCommentEvent":
      detail = "commented in";
      break;
    case "CommitCommentEvent":
      detail = "commented on commit in";
      break;
    default:
      detail = `activity in`;
  }

  return { type, repo, createdAt: created, detail };
}

function demoEvents(username: string): GithubEvent[] {
  const now = Date.now();
  const mins = (m: number) => new Date(now - m * 60000).toISOString();
  return [
    { type: "PushEvent", repo: `${username}/ILIV007`, createdAt: mins(47), detail: "pushed 3 commits to" },
    { type: "WatchEvent", repo: "vercel/next.js", createdAt: mins(180), detail: "starred" },
    { type: "CreateEvent", repo: `${username}/ILIV007`, createdAt: mins(320), detail: "created branch in" },
    { type: "PullRequestEvent", repo: `${username}/ILIV007`, createdAt: mins(720), detail: "opened PR in" },
    { type: "IssuesEvent", repo: `${username}/ILIV007`, createdAt: mins(1440), detail: "opened issue in" },
    { type: "ForkEvent", repo: "shadcn-ui/ui", createdAt: mins(2880), detail: "forked" },
  ];
}

export async function fetchActivity(username: string): Promise<ActivityData> {
  const key = username.trim().toLowerCase();
  if (!key) return { username: "ILIV007", events: demoEvents("ILIV007"), source: "demo", fetchedAt: new Date().toISOString() };

  const cached = cache.get(key);
  if (cached && Date.now() - cached.t < CACHE_TTL) return cached.data;

  const url = `https://api.github.com/users/${encodeURIComponent(key)}/events/public`;
  try {
    const res = await fetch(url, {
      headers: {
        Accept: "application/vnd.github+json",
        "User-Agent": "ILIV007-profile-readme",
      },
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

    const data: ActivityData = {
      username: key,
      events,
      source: "live",
      fetchedAt: new Date().toISOString(),
    };
    cache.set(key, { t: Date.now(), data });
    return data;
  } catch {
    const data: ActivityData = {
      username: key,
      events: demoEvents(key),
      source: "demo",
      fetchedAt: new Date().toISOString(),
    };
    cache.set(key, { t: Date.now(), data });
    return data;
  }
}

// --- SVG rendering ---

const W = 860;
const H = 260;
const BG = "#0d1117";
const BORDER = "#30363d";
const FG = "#c9d1d9";
const MUTED = "#8b949e";
const PURPLE = "#bc8cff";
const GOLD = "#e3b341";
const LAVENDER = "#d2a8ff";
const GREEN = "#39d353";

function esc(s: string): string {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

export function renderActivitySvg(data: ActivityData): string {
  const user = data.username;
  const events = data.events.slice(0, 6);
  const sourceTag = data.source === "live" ? "live" : "demo";

  const titleBarH = 30;
  const padX = 22;
  const lineH = 26;
  const promptY = titleBarH + 24;
  const logStartY = promptY + 22;

  // Prompt line
  const prompt = `<text x="${padX}" y="${promptY.toFixed(1)}" font-size="14"><tspan fill="${PURPLE}">${esc(user)}@github</tspan><tspan fill="${MUTED}"> ~ $ </tspan><tspan fill="${FG}">tail -f activity.log</tspan><tspan fill="${GOLD}"> _</tspan></text>`;

  // Event lines
  const lines: string[] = [];
  const baseDelay = 0.3;
  const stagger = 0.12;
  const dur = 0.4;

  events.forEach((e, i) => {
    const y = logStartY + i * lineH;
    const delay = (baseDelay + i * stagger).toFixed(2);
    const time = timeAgo(e.createdAt);
    const isOwn = e.repo.toLowerCase().startsWith(user.toLowerCase() + "/");
    const repoColor = isOwn ? GOLD : LAVENDER;

    lines.push(
      `<g class="logline" style="animation-delay:${delay}s">` +
      `<text x="${padX}" y="${y.toFixed(1)}" font-size="13">` +
      `<tspan fill="${MUTED}">[${esc(time)}]</tspan> ` +
      `<tspan fill="${GREEN}">${esc(e.detail)}</tspan> ` +
      `<tspan fill="${repoColor}">${esc(e.repo)}</tspan>` +
      `</text></g>`
    );
  });

  // source badge
  const badgeColor = data.source === "live" ? GREEN : GOLD;
  const badge = `<text x="${W - 22}" y="${(titleBarH - 10).toFixed(1)}" text-anchor="end" font-size="11" fill="${badgeColor}">● ${sourceTag}</text>`;

  const svg = `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
  <style>
    .logline { opacity: 0; animation: logline ${dur}s cubic-bezier(0.22,0.61,0.36,1) forwards; }
    @keyframes logline {
      from { opacity: 0; transform: translateX(-10px); }
      to { opacity: 1; transform: translateX(0); }
    }
    @media (prefers-reduced-motion: reduce) {
      .logline { opacity: 1; animation: none; transform: none; }
    }
  </style>
  <rect x="0.5" y="0.5" width="${W - 1}" height="${H - 1}" rx="8" ry="8" fill="${BG}" stroke="${BORDER}" stroke-width="1"/>
  <path d="M0.5 8 a8 8 0 0 1 8 -7.5 H${W - 8.5} a8 8 0 0 1 8 7.5 V${titleBarH} H0.5 Z" fill="#161b22"/>
  <line x1="0.5" y1="${titleBarH}" x2="${W - 0.5}" y2="${titleBarH}" stroke="${BORDER}" stroke-width="1"/>
  <circle cx="14" cy="15" r="5" fill="#ff5f56"/>
  <circle cx="30" cy="15" r="5" fill="#ffbd2e"/>
  <circle cx="46" cy="15" r="5" fill="#27c93f"/>
  <text x="${W / 2}" y="19.5" text-anchor="middle" font-size="12" fill="${MUTED}">${esc(user)}@github — activity.log</text>
  ${badge}
  ${prompt}
  ${lines.join("\n  ")}
  <title>Live activity for ${esc(user)}</title>
</svg>`;

  return svg;
}
