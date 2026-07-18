/**
 * fetch_contributions.ts — scrapes GitHub's PUBLIC contribution calendar.
 * No token, no GraphQL. Parses <td class="ContributionCalendar-day"> +
 * <tool-tip for="id"> elements, derives stats. 10-min in-memory cache.
 * Falls back to deterministic demo data if the scrape fails.
 */

export interface ContribDay {
  date: string;
  count: number;
  level: number;
}

export interface ContribStats {
  total: number;
  currentStreak: number;
  longestStreak: number;
  bestDay: { date: string; count: number } | null;
  monthly: { month: string; count: number }[];
  firstDate: string | null;
  lastDate: string | null;
  daysCount: number;
}

export interface ContributionData {
  username: string;
  days: ContribDay[];
  stats: ContribStats;
  source: "live" | "demo";
  fetchedAt: string;
}

const UA =
  "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) " +
  "Chrome/124.0 Safari/537.36";

const cache = new Map<string, { t: number; data: ContributionData }>();
const CACHE_TTL = 1000 * 60 * 10;

function parseRects(html: string): ContribDay[] {
  const days: ContribDay[] = [];
  const counts = new Map<string, number>();
  const tipRe = /<tool-tip\b[^>]*\bfor="([^"]+)"[^>]*>([\s\S]*?)<\/tool-tip>/gi;
  let m: RegExpExecArray | null;
  while ((m = tipRe.exec(html)) !== null) {
    const cm = /(\d+)\s+contributions?/i.exec(m[2]);
    if (cm) counts.set(m[1], parseInt(cm[1], 10));
    else if (/no contributions/i.test(m[2])) counts.set(m[1], 0);
  }
  const tdRe = /<(?:td|rect)\b[^>]*ContributionCalendar-day[^>]*>/gi;
  while ((m = tdRe.exec(html)) !== null) {
    const el = m[0];
    const date = /data-date="([^"]+)"/.exec(el)?.[1];
    const level = /data-level="(\d+)"/.exec(el)?.[1];
    const id = /id="([^"]+)"/.exec(el)?.[1];
    if (!date) continue;
    days.push({
      date,
      count: id ? counts.get(id) ?? 0 : 0,
      level: level ? parseInt(level, 10) : 0,
    });
  }
  days.sort((a, b) => (a.date < b.date ? -1 : 1));
  return days;
}

function computeStats(days: ContribDay[]): ContribStats {
  let total = 0;
  let best: ContribDay | null = null;
  const monthMap = new Map<string, number>();
  for (const d of days) {
    total += d.count;
    if (!best || d.count > best.count) best = d;
    const month = d.date.slice(0, 7);
    monthMap.set(month, (monthMap.get(month) ?? 0) + d.count);
  }
  let longest = 0;
  let run = 0;
  for (const d of days) {
    if (d.count > 0) {
      run += 1;
      if (run > longest) longest = run;
    } else run = 0;
  }
  let current = 0;
  for (let i = days.length - 1; i >= 0; i--) {
    if (days[i].count > 0) current += 1;
    else if (current > 0) break;
  }
  const lastNonZero = [...days].reverse().find((d) => d.count > 0);
  if (lastNonZero) {
    const daysAgo = (Date.now() - new Date(lastNonZero.date).getTime()) / 86400000;
    if (daysAgo > 2.5) current = 0;
  }
  const monthly = [...monthMap.entries()]
    .sort((a, b) => (a[0] < b[0] ? -1 : 1))
    .map(([month, count]) => ({ month, count }));
  return {
    total,
    currentStreak: current,
    longestStreak: longest,
    bestDay: best ? { date: best.date, count: best.count } : null,
    monthly,
    firstDate: days[0]?.date ?? null,
    lastDate: days[days.length - 1]?.date ?? null,
    daysCount: days.length,
  };
}

function demoData(username: string): ContributionData {
  const days: ContribDay[] = [];
  const today = new Date();
  const start = new Date(today);
  start.setDate(start.getDate() - 53 * 7 + 1);
  let seed = 0;
  for (let i = 0; i < 53 * 7; i++) {
    const d = new Date(start);
    d.setDate(start.getDate() + i);
    if (d > today) break;
    const yyyy = d.getFullYear();
    const mm = String(d.getMonth() + 1).padStart(2, "0");
    const dd = String(d.getDate()).padStart(2, "0");
    seed = (seed * 9301 + 49297) % 233280;
    const r = seed / 233280;
    const weekend = d.getDay() === 0 || d.getDay() === 6;
    let count = 0;
    if (r > 0.3) count = Math.floor(r * (weekend ? 5 : 14)) + (weekend ? 0 : 1);
    if (r > 0.96) count += 8;
    let level = 0;
    if (count >= 15) level = 4;
    else if (count >= 9) level = 3;
    else if (count >= 5) level = 2;
    else if (count >= 2) level = 1;
    days.push({ date: `${yyyy}-${mm}-${dd}`, count, level });
  }
  return {
    username,
    days,
    stats: computeStats(days),
    source: "demo",
    fetchedAt: new Date().toISOString(),
  };
}

export async function fetchContributions(
  username: string
): Promise<ContributionData> {
  const key = username.trim().toLowerCase();
  if (!key) return demoData("ILIV007");
  const cached = cache.get(key);
  if (cached && Date.now() - cached.t < CACHE_TTL) return cached.data;
  const url = `https://github.com/users/${encodeURIComponent(key)}/contributions`;
  try {
    const res = await fetch(url, {
      headers: { "User-Agent": UA, Accept: "text/html" },
      redirect: "follow",
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const html = await res.text();
    const days = parseRects(html);
    if (days.length === 0) throw new Error("no day cells parsed");
    const data: ContributionData = {
      username: key,
      days,
      stats: computeStats(days),
      source: "live",
      fetchedAt: new Date().toISOString(),
    };
    cache.set(key, { t: Date.now(), data });
    return data;
  } catch {
    const data = demoData(key);
    cache.set(key, { t: Date.now(), data });
    return data;
  }
}
