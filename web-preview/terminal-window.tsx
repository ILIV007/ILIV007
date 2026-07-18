"use client";

import { ReactNode } from "react";

interface TerminalWindowProps {
  title?: string;
  children: ReactNode;
  className?: string;
}

/**
 * A faux terminal window: title bar with traffic-light dots + a title,
 * then a dark body. Used to frame the README preview so it reads like a
 * terminal the way the article describes.
 */
export function TerminalWindow({
  title = "terminal",
  children,
  className = "",
}: TerminalWindowProps) {
  return (
    <div
      className={`rounded-xl border border-[#30363d] bg-[#0d1117] overflow-hidden shadow-2xl shadow-black/40 ${className}`}
    >
      <div className="flex items-center gap-2 border-b border-[#30363d] bg-[#161b22] px-4 py-2.5">
        <span className="h-3 w-3 rounded-full bg-[#ff5f56]" />
        <span className="h-3 w-3 rounded-full bg-[#ffbd2e]" />
        <span className="h-3 w-3 rounded-full bg-[#27c93f]" />
        <span className="ml-3 truncate font-mono text-xs text-[#8b949e]">
          {title}
        </span>
      </div>
      <div className="p-4 sm:p-6">{children}</div>
    </div>
  );
}
