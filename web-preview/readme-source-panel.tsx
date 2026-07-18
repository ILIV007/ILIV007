"use client";

import { useState } from "react";
import { Check, Copy, FileCode2 } from "lucide-react";
import { Button } from "@/components/ui/button";

export function buildReadmeMd(username: string): string {
  const u = username || "ILIV007";
  return `<div align="center">

<h3><code>${u}@github ~ $ tail -f activity.log</code></h3>
<img src="./activity-feed.svg" width="860" />

<br><br>

<h3><code>${u}@github ~ $ whoami</code></h3>
<table>
  <tr>
    <td valign="top"><img src="./knight.svg" width="400" /></td>
    <td valign="top"><img src="./info-card.svg" width="460" /></td>
  </tr>
</table>

</div>

<!-- animated SVG · SMIL + CSS keyframes · no JavaScript -->`;
}

export function ReadmeSourcePanel({ username }: { username: string }) {
  const [copied, setCopied] = useState(false);
  const md = buildReadmeMd(username);
  const copy = async () => {
    try {
      await navigator.clipboard.writeText(md);
      setCopied(true);
      setTimeout(() => setCopied(false), 1800);
    } catch { /* ignore */ }
  };
  return (
    <div className="rounded-xl border border-[#30363d] bg-[#0d1117] overflow-hidden">
      <div className="flex items-center justify-between border-b border-[#30363d] bg-[#161b22] px-4 py-2.5">
        <div className="flex items-center gap-2 text-xs font-mono text-[#8b949e]">
          <FileCode2 className="h-4 w-4 text-[#e3b341]" />
          README.md
        </div>
        <Button size="sm" variant="ghost" onClick={copy} className="h-7 gap-1.5 text-xs text-[#c9d1d9] hover:bg-[#30363d] hover:text-white">
          {copied ? (<><Check className="h-3.5 w-3.5 text-[#bc8cff]" /> copied</>) : (<><Copy className="h-3.5 w-3.5" /> copy</>)}
        </Button>
      </div>
      <pre className="max-h-72 overflow-auto p-4 text-xs leading-relaxed text-[#c9d1d9] font-mono custom-scroll">
        <code>{md}</code>
      </pre>
    </div>
  );
}
