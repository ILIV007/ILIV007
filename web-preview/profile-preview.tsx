"use client";

import { TerminalWindow } from "@/components/terminal-window";

interface ProfilePreviewProps {
  username: string;
  replayKey: number;
}

/**
 * README preview — three SEPARATE SVG files (professional code structure),
 * composed cohesively in one terminal window:
 *
 *   [activity-feed.svg]         ← full width 860px, top
 *   [knight.svg]  [info-card.svg]  ← side by side, vertically aligned (top)
 *
 * All prompts live INSIDE each SVG — no floating HTML text.
 * The knight (400px) + info card (460px) = 860px = activity feed width,
 * so all three line up edge-to-edge.
 */
export function ProfilePreview({ username, replayKey }: ProfilePreviewProps) {
  const user = username || "ILIV007";
  const actSrc = `/api/svg/activity?username=${encodeURIComponent(user)}&v=${replayKey}`;
  const knightSrc = `/api/svg/knight?username=${encodeURIComponent(user)}&v=${replayKey}`;
  const cardSrc = `/api/svg/info-card?username=${encodeURIComponent(user)}&v=${replayKey}`;

  return (
    <TerminalWindow title={`${user}@github: ~/profile — README.md preview`}>
      <div className="mx-auto w-full max-w-[860px]">
        {/* Activity feed — full width */}
        <div className="overflow-x-auto custom-scroll">
          <img
            key={actSrc}
            src={actSrc}
            alt={`Activity feed for ${user}`}
            className="block h-auto w-full max-w-[860px] rounded-lg border border-[#30363d]"
            style={{ minWidth: 560 }}
          />
        </div>

        {/* Knight + info card — side by side, top-aligned (items-start) */}
        <div className="mt-4 flex flex-col items-stretch gap-3 md:flex-row md:items-start">
          <img
            key={knightSrc}
            src={knightSrc}
            alt="ILIV007 — knight portrait"
            className="block h-auto w-full rounded-lg border border-[#30363d] md:w-[400px] md:shrink-0"
          />
          <img
            key={cardSrc}
            src={cardSrc}
            alt="ILIYA — neofetch info card"
            className="block h-auto w-full rounded-lg border border-[#30363d] md:w-[460px] md:shrink-0"
          />
        </div>
      </div>
    </TerminalWindow>
  );
}
