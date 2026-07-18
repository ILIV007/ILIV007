"use client";

import { TerminalWindow } from "@/components/terminal-window";

interface ProfilePreviewProps {
  username: string;
  replayKey: number;
}

/**
 * README preview — a single terminal window with two fake shell prompts:
 *   1) ./contributions.sh  → heatmap (860 wide)
 *   2) whoami              → knight emblem (370) + info card (490) side by side
 *
 * Alignment: the heatmap is 860px wide; the knight (370) + card (490) = 860,
 * so all three SVGs line up edge-to-edge. The prompt and the SVG row share
 * the same max-width container so the prompt never falls outside the row.
 */
export function ProfilePreview({ username, replayKey }: ProfilePreviewProps) {
  const user = username || "ILIV007";
  const heatmapSrc = `/api/svg/heatmap?username=${encodeURIComponent(user)}&v=${replayKey}`;
  const knightSrc = `/api/svg/knight?v=${replayKey}`;
  const cardSrc = `/api/svg/info-card?username=${encodeURIComponent(user)}&v=${replayKey}`;

  return (
    <TerminalWindow title={`${user}@github: ~/profile — README.md preview`}>
      <div className="mx-auto w-full max-w-[860px]">
        {/* contributions.sh */}
        <div className="mb-2 flex items-center gap-2 font-mono text-sm">
          <span className="text-[#bc8cff]">{user}@github</span>
          <span className="text-[#8b949e]">~ $</span>
          <span className="text-[#c9d1d9]">./contributions.sh</span>
          <span className="ml-1 inline-block h-4 w-2 animate-pulse bg-[#e3b341]" />
        </div>
        <div className="overflow-x-auto custom-scroll">
          <img
            key={heatmapSrc}
            src={heatmapSrc}
            alt={`Contribution heatmap for ${user}`}
            className="block h-auto w-full max-w-[860px] rounded-lg border border-[#30363d]"
            style={{ minWidth: 560 }}
          />
        </div>

        {/* whoami */}
        <div className="mb-2 mt-6 flex items-center gap-2 font-mono text-sm">
          <span className="text-[#bc8cff]">{user}@github</span>
          <span className="text-[#8b949e]">~ $</span>
          <span className="text-[#c9d1d9]">whoami</span>
        </div>
        {/* table-like row, top-aligned, stacks on mobile */}
        <div className="flex flex-col items-stretch gap-3 md:flex-row md:items-start">
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
