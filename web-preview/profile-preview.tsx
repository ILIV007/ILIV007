"use client";

import { TerminalWindow } from "@/components/terminal-window";

interface ProfilePreviewProps {
  username: string;
  replayKey: number;
}

/**
 * README preview — all prompts live INSIDE the SVGs (no floating HTML text).
 * Layout:
 *   1) Activity feed SVG (860 wide) — live GitHub events, prompt inside.
 *   2) Knight emblem SVG (400) + info card SVG (460) side by side —
 *      the `whoami` prompt is inside the knight SVG.
 */
export function ProfilePreview({ username, replayKey }: ProfilePreviewProps) {
  const user = username || "ILIV007";
  const activitySrc = `/api/svg/activity?username=${encodeURIComponent(user)}&v=${replayKey}`;
  const knightSrc = `/api/svg/knight?username=${encodeURIComponent(user)}&v=${replayKey}`;
  const cardSrc = `/api/svg/info-card?username=${encodeURIComponent(user)}&v=${replayKey}`;

  return (
    <TerminalWindow title={`${user}@github: ~/profile — README.md preview`}>
      <div className="mx-auto w-full max-w-[860px]">
        {/* Activity feed — live GitHub events */}
        <div className="overflow-x-auto custom-scroll">
          <img
            key={activitySrc}
            src={activitySrc}
            alt={`Live activity feed for ${user}`}
            className="block h-auto w-full max-w-[860px] rounded-lg border border-[#30363d]"
            style={{ minWidth: 560 }}
          />
        </div>

        {/* Knight + info card — whoami prompt is inside the knight SVG */}
        <div className="mt-4 flex flex-col items-stretch gap-3 md:flex-row md:items-start">
          <img
            key={knightSrc}
            src={knightSrc}
            alt="ILIV007 — knight emblem"
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
