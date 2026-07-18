# web-preview — ILIV007 profile route source

This folder contains the Next.js source for the live /ILIV007 preview route.
Drop these files into a Next.js 16 project (App Router) under their
respective paths:

- `page.tsx` → `src/app/ILIV007/page.tsx`
- `profile-page.tsx`, `profile-preview.tsx`, `readme-source-panel.tsx`,
  `terminal-window.tsx` → `src/components/`
- `knight-emblem.ts`, `neofetch-card.ts`, `contributions.ts`,
  `heatmap.ts` → `src/lib/`

Requires: `sharp` for the knight image→ASCII pipeline.
