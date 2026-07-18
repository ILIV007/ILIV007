"use client";

import { useState } from "react";
import { Shield, RefreshCw, FileCode2, Download } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ProfilePreview } from "@/components/profile-preview";
import { ReadmeSourcePanel } from "@/components/readme-source-panel";

const USERNAME = "ILIV007";
const NAME = "ILIYA";
const ZIP = "/ILIV007-profile-v0.6.zip";

export function ProfilePage() {
  const [replayKey, setReplayKey] = useState(0);
  const [showSource, setShowSource] = useState(false);

  return (
    <div className="flex min-h-screen flex-col bg-[#010409] font-mono text-[#c9d1d9]">
      {/* slim header */}
      <header className="border-b border-[#21262d] bg-[#0d1117]/80 backdrop-blur">
        <div className="mx-auto flex w-full max-w-5xl items-center justify-between px-4 py-4">
          <div className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-md border border-[#e3b341]/40 bg-[#e3b341]/10">
              <Shield className="h-4 w-4 text-[#e3b341]" />
            </div>
            <div className="leading-tight">
              <p className="text-sm font-bold text-white">
                {NAME}{" "}
                <span className="font-normal text-[#8b949e]">/ {USERNAME}</span>
              </p>
              <p className="text-[11px] text-[#8b949e]">
                github profile · animated svg · minimal
              </p>
            </div>
          </div>
          <a href={ZIP} download>
            <Button
              variant="outline"
              size="sm"
              className="gap-1.5 border-[#30363d] bg-[#0d1117] text-[#c9d1d9] hover:bg-[#161b22] hover:text-white"
            >
              <Download className="h-3.5 w-3.5" /> profile v0.6
            </Button>
          </a>
        </div>
      </header>

      <main className="mx-auto flex w-full max-w-5xl flex-1 flex-col gap-6 px-4 py-8">
        {/* controls */}
        <div className="flex items-center gap-2">
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={() => setReplayKey((k) => k + 1)}
            className="gap-1.5 border-[#30363d] bg-[#0d1117] text-[#c9d1d9] hover:bg-[#161b22] hover:text-white"
          >
            <RefreshCw className="h-3.5 w-3.5" /> replay
          </Button>
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={() => setShowSource((s) => !s)}
            className="gap-1.5 border-[#30363d] bg-[#0d1117] text-[#c9d1d9] hover:bg-[#161b22] hover:text-white"
          >
            <FileCode2 className="h-3.5 w-3.5" />
            {showSource ? "hide" : "README.md"}
          </Button>
        </div>

        {/* the profile */}
        <ProfilePreview username={USERNAME} replayKey={replayKey} />

        {/* readme source */}
        {showSource && <ReadmeSourcePanel username={USERNAME} />}
      </main>

      {/* sticky footer */}
      <footer className="mt-auto border-t border-[#21262d] bg-[#0d1117]">
        <div className="mx-auto flex w-full max-w-5xl flex-col items-center justify-between gap-1.5 px-4 py-4 text-[11px] text-[#8b949e] sm:flex-row">
          <p>
            {NAME} · animated svg · smil + css keyframes · no javascript in the
            readme
          </p>
          <p className="flex items-center gap-1.5">
            <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-[#bc8cff]" />
            knight theme · minimal
          </p>
        </div>
      </footer>
    </div>
  );
}
