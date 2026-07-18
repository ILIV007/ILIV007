# web-preview — ILIV007 profile route source

Next.js 16 (App Router) source for the live /ILIV007 preview route.

## Files → destination
- `page.tsx` → `src/app/ILIV007/page.tsx`
- `profile-page.tsx`, `profile-preview.tsx`, `readme-source-panel.tsx`,
  `terminal-window.tsx` → `src/components/`
- `profile-svg.ts` → `src/lib/`

## What it does
ONE single SVG (`profile.svg`) contains the entire profile:
- Terminal frame with title bar
- Live activity feed (scrapes GitHub public events API, no token)
- Knight emblem (rect-based, hand-drawn crusader great helm)
- Neofetch info card (ILIYA, level ??, channel ILIVIR3)

All prompts live inside the SVG. No separate images, no floating HTML text.
