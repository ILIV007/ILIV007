# web-preview — ILIV007 profile route source

Next.js 16 (App Router) source for the live /ILIV007 preview route.

## Files → destination
- `page.tsx` → `src/app/ILIV007/page.tsx`
- `profile-page.tsx`, `profile-preview.tsx`, `readme-source-panel.tsx`,
  `terminal-window.tsx` → `src/components/`
- `knight-portrait.ts`, `info-card.ts`, `activity-feed.ts` → `src/lib/`

## Three separate SVGs
- **knight.svg** — professional ASCII portrait (image→ASCII via sharp)
- **info-card.svg** — minimal neofetch card (purple+gold, level ??, ILIVIR3)
- **activity-feed.svg** — live GitHub events feed (no token)

All prompts live inside each SVG. Composed cohesively in one terminal layout.
