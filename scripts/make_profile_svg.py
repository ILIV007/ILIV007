#!/usr/bin/env python3
"""
make_profile_svg.py — ONE animated SVG for the GitHub profile README.
Neon terminal aesthetic with pixel bats, live stats, and glow effects.
Usage: GITHUB_USERNAME=ILIV007 python scripts/make_profile_svg.py [output.svg]
"""
import os,sys,requests
from pathlib import Path

USERNAME=os.environ.get("GITHUB_USERNAME","ILIV007")
W,H=860,560
BG="#07070e";FG="#a8a3c9";HI="#f0edff";P1="#b388ff";P2="#5fb0ff";DIM="#544e78";OK="#3fe0a0";WARN="#ffc861"
def esc(s):return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
def fmt(n):return f"{n:,}"

FONT={"I":["11111","00100","00100","00100","00100","00100","11111"],"L":["10000","10000","10000","10000","10000","10000","11111"],"V":["10001","10001","10001","10001","01010","01010","00100"],"0":["01110","10001","10011","10101","11001","10001","01110"],"7":["11111","00010","00100","00100","01000","01000","01000"]}
BS="ILIV007";BP=5;BGAP=1;CGAP=10;FR=7;FC=5;CW=FC*(BP+BGAP);CH=FR*(BP+BGAP);BW=len(BS)*CW+(len(BS)-1)*CGAP;BH=CH
BAT=["100001","111111","100001","111111","011110","100001"]

def banner(ox,oy):
    r=[];cx=ox
    for ci,ch in enumerate(BS):
        bm=FONT.get(ch)
        if not bm:continue
        col=P1 if ci<4 else P2
        for row in range(FR):
            for c in range(FC):
                if bm[row][c]=="1":
                    r.append(f'<rect x="{cx+c*(BP+BGAP)}" y="{oy+row*(BP+BGAP)}" width="{BP}" height="{BP}" rx="1" fill="{col}"/>')
        cx+=CW+CGAP
    return"\n  ".join(r)

def bats(bx,by):
    r=[]
    for i,(x,y,d,du) in enumerate([(bx-40,by+10,1.0,3.5),(bx+BW+20,by+5,1.3,4),(bx+BW/2-10,by-25,1.7,3)]):
        col=P2 if i==2 else P1
        bat=""
        for row in range(len(BAT)):
            for c in range(len(BAT[row])):
                if BAT[row][c]=="1":bat+=f'<rect x="{x+c*3}" y="{y+row*3}" width="3" height="3" rx="0.5" fill="{col}" opacity="0.7"/>'
        r.append(f'<g opacity="0"><animate attributeName="opacity" from="0" to="0.6" begin="{d}s" dur="0.5s" fill="freeze"/><animateTransform attributeName="transform" type="translate" values="0,0;0,-6;0,0;0,4;0,0" keyTimes="0;0.25;0.5;0.75;1" begin="{d}s" dur="{du}s" repeatCount="indefinite"/>{bat}</g>')
    return"\n  ".join(r)

def sparkles():
    r=[]
    for i in range(12):
        x=50+(i*67)%(W-100);y=40+(i*53)%(H-80);d=0.5+i*0.3
        r.append(f'<circle cx="{x}" cy="{y}" r="1.5" fill="{P1}" opacity="0"><animate attributeName="opacity" values="0;0.8;0" keyTimes="0;0.5;1" begin="{d}s" dur="{2+(x%3)}s" repeatCount="indefinite"/><animateTransform attributeName="transform" type="translate" values="0,0;0,-8;0,0" begin="{d}s" dur="{3+(y%2)}s" repeatCount="indefinite"/></circle>')
    return"\n  ".join(r)

def scanlines():
    return"\n  ".join(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}" stroke="#000" stroke-width="0.5" opacity="0.08"/>'for y in range(0,H,4))

def fetch_stats():
    try:
        u=requests.get(f"https://api.github.com/users/{USERNAME}",headers={"Accept":"application/vnd.github+json","User-Agent":"ILIV007-profile-readme"},timeout=15)
        u.raise_for_status();d=u.json()
        try:
            h=requests.get(f"https://github.com/users/{USERNAME}",headers={"User-Agent":"Mozilla/5.0","Accept":"text/html"},timeout=15).text
            import re;m=re.search(r"(\d[\d,]*)\s+contributions?",h,re.I);tc=int(m.group(1).replace(",",""))if m else None
        except:tc=None
        return{"repos":d.get("public_repos",0),"followers":d.get("followers",0),"following":d.get("following",0),"commits":tc}
    except:return None

def make_svg():
    st=fetch_stats()
    tb=32;px=22;by=tb+20;blh=20;bd=0.15;bs_=0.25;bdur=0.4
    bl=[("","tty-blog bios — neon cold start"),("ok","mounting /dev/blog ... loading profile"),("ok",f"fetching live stats ... {'done'if st else'cached'}"),("ok","cursor blink rate ... 1.06s (CRT-accurate)"),("warn","nostalgia levels ... within legal limits"),("ok","starting fakesh 1.06 ... ready")]
    bt=[]
    for i,(tg,tx) in enumerate(bl):
        y=by+i*blh;d=f"{bd+i*bs_:.2f}";tc=OK if tg=="ok"else WARN if tg=="warn"else DIM;tt=f'<tspan fill="{tc}" font-weight="700">[ {tg} ]</tspan> 'if tg else""
        bt.append(f'<text x="{px}" y="{y}" font-family="\'Courier New\', monospace" font-size="13" fill="{DIM}" opacity="0"><animate attributeName="opacity" from="0" to="1" begin="{d}s" dur="{bdur}s" fill="freeze"/>{tt}{esc(tx)}</text>')
    bny=by+len(bl)*blh+16;bnx=(W-BW)/2;bnd=f"{bd+len(bl)*bs_:.2f}"
    bg_=f'<g opacity="0" filter="url(#glow)"><animate attributeName="opacity" from="0" to="1" begin="{bnd}s" dur="0.7s" fill="freeze"/>{banner(bnx,bny)}</g>'
    tg_y=bny+BH+16;tg_d=f"{float(bnd)+0.5:.2f}"
    tl=f'<text x="{W/2}" y="{tg_y}" text-anchor="middle" font-family="\'Courier New\', monospace" font-size="12" fill="{DIM}" opacity="0"><animate attributeName="opacity" from="0" to="1" begin="{tg_d}s" dur="0.4s" fill="freeze"/>a developer blog that behaves like a TTY</text>'
    iy=tg_y+26;ilh=18;isd=float(tg_d)+0.2
    il=[("OS","tty-blog neon"),("Shell","fakesh 1.06"),("Theme","neon (purple)")]
    if st:il+=[("Repos",fmt(st["repos"])),("Followers",fmt(st["followers"])),("Following",fmt(st["following"]))]+([("Commits",f'{fmt(st["commits"])}/yr')]if st.get("commits")else[])
    il.append(("Deps","0"))
    it=[]
    for i,(k,v) in enumerate(il):
        y=iy+i*ilh;d=f"{isd+i*0.08:.2f}";is_stat=k in("Repos","Followers","Following","Commits");vc=OK if is_stat else P1
        it.append(f'<text x="{px}" y="{y}" font-family="\'Courier New\', monospace" font-size="13" opacity="0"><animate attributeName="opacity" from="0" to="1" begin="{d}s" dur="0.3s" fill="freeze"/><tspan fill="{P1}" font-weight="700">{esc(k.ljust(12))}</tspan><tspan fill="{vc}">{esc(v)}</tspan></text>')
    cy=iy+len(il)*ilh+12
    cl=[("email","ILIV007@proton.me"),("telegram","@ILIVIR3"),("website","ilivir3.pages.dev")]
    ct=[]
    for i,(lb,v) in enumerate(cl):
        y=cy+i*ilh;d=f"{isd+len(il)*0.08+i*0.08:.2f}"
        ct.append(f'<text x="{px}" y="{y}" font-family="\'Courier New\', monospace" font-size="13" opacity="0"><animate attributeName="opacity" from="0" to="1" begin="{d}s" dur="0.3s" fill="freeze"/><tspan fill="{P2}" font-weight="700">{esc(lb.ljust(12))}</tspan><tspan fill="{HI}">{esc(v)}</tspan></text>')
    py=cy+len(cl)*ilh+18;pd=f"{isd+(len(il)+len(cl))*0.08+0.2:.2f}"
    pt=f"guest@{USERNAME.lower()}:~$ help";pw=len(pt)*7.8;cx=px+pw+2
    pr=f'<text x="{px}" y="{py}" font-family="\'Courier New\', monospace" font-size="13" opacity="0" filter="url(#glow)"><animate attributeName="opacity" from="0" to="1" begin="{pd}s" dur="0.3s" fill="freeze"/><tspan fill="{P2}" font-weight="700">guest@{esc(USERNAME.lower())}</tspan><tspan fill="{DIM}">:</tspan><tspan fill="{P1}" font-weight="700">~</tspan><tspan fill="{P2}" font-weight="700">$ </tspan><tspan fill="{HI}">help</tspan></text>'
    cur=f'<rect x="{cx:.1f}" y="{py-11}" width="8" height="14" rx="1.5" fill="{P1}" filter="url(#glow)" opacity="0"><animate attributeName="opacity" from="0" to="1" begin="{pd}s" dur="0.2s" fill="freeze"/><animate attributeName="opacity" values="1;0;1" keyTimes="0;0.5;1" begin="{float(pd)+0.3:.2f}s" dur="1.06s" repeatCount="indefinite"/></rect>'
    badge=OK if st else WARN;bs_=f"{'live'if st else'cached'}"
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs><filter id="glow" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="2.5" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="10" ry="10" fill="{BG}" stroke="{P1}" stroke-width="1" opacity="0.6"/>
<path d="M0.5 10 a10 10 0 0 1 10 -9.5 H{W-10.5} a10 10 0 0 1 10 9.5 V{tb} H0.5 Z" fill="#0d0d18"/>
<line x1="0.5" y1="{tb}" x2="{W-0.5}" y2="{tb}" stroke="{P1}" stroke-width="1" opacity="0.4"/>
<circle cx="16" cy="16" r="5" fill="#ff5f56"/><circle cx="33" cy="16" r="5" fill="#ffbd2e"/><circle cx="50" cy="16" r="5" fill="#27c93f"/>
<text x="{W/2}" y="20.5" text-anchor="middle" font-family="'Courier New', monospace" font-size="11" fill="{DIM}">guest@{esc(USERNAME.lower())}: ~ — tty0</text>
<text x="{W-18}" y="20.5" text-anchor="end" font-family="'Courier New', monospace" font-size="11" fill="{badge}">● {bs_}</text>
{sparkles()}
{chr(10).join("  "+t for t in bt)}
{bg_}
{bats(bnx,bny)}
{tl}
{chr(10).join("  "+t for t in it)}
{chr(10).join("  "+t for t in ct)}
{pr}
{cur}
{scanlines()}
<title>{esc(USERNAME)} — terminal</title>
</svg>'''

if __name__=="__main__":
    out=sys.argv[1]if len(sys.argv)>1 else"profile.svg"
    svg=make_svg()
    Path(out).write_text(svg,encoding="utf-8")
    print(f"Written {out} ({len(svg)} bytes)")
