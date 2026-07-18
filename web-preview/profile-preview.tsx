"use client";

import { TerminalWindow } from "@/components/terminal-window";

interface ProfilePreviewProps {
  username: string;
  replayKey: number;
}

/**
 * README preview — ONE single SVG containing the entire profile:
 * terminal frame + activity feed + knight + info card, all cohesive.
 * No separate images, no floating prompt text.
 */
export function ProfilePreview({ username, replayKey }: ProfilePreviewProps) {
  const user = username || "ILIV007";
  const profileSrc = `/api/svg/profile?username=${encodeURIComponent(user)}&v=${replayKey}`;

  return (
    <TerminalWindow title={`${user}@github: ~/profile — README.md preview`}>
      <div className="mx-auto w-full max-w-[860px]">
        <div className="overflow-x-auto custom-scroll">
          <img
            key={profileSrc}
            src={profileSrc}
            alt={`${user} — GitHub profile`}
            className="block h-auto w-full max-w-[860px] rounded-lg border border-[#30363d]"
            style={{ minWidth: 560 }}
          />
        </div>
      </div>
    </TerminalWindow>
  );
}
