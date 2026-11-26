import math
import os
import time
from flask import Blueprint, jsonify, request, abort, Response, send_from_directory
from CTFd.models import Solves, Users, Challenges
from CTFd.utils.scores import get_standings

KEY = os.getenv("BIGSCREEN_KEY", "")
HERE = os.path.dirname(os.path.abspath(__file__))
bp = Blueprint("bigscreen", __name__)
_cache = {"t": 0.0, "v": None}
CACHE_SECONDS = 2


def _check():
    if not KEY or request.args.get("key") != KEY:
        abort(403)


def _no_store(resp):
    resp.headers["Cache-Control"] = "no-store"
    return resp


def _build():
    # First capture of each challenge = earliest solve in the DB (id breaks date ties).
    solves = (
        Solves.query.join(Users, Solves.user_id == Users.id)
        .join(Challenges, Solves.challenge_id == Challenges.id)
        .filter(Users.hidden == False, Users.banned == False)  # noqa: E712
        .order_by(Solves.date.asc(), Solves.id.asc())
        .all()
    )
    seen, bloods = set(), []
    for s in solves:
        if s.challenge_id in seen:
            continue
        if s.team and (s.team.hidden or s.team.banned):
            continue
        seen.add(s.challenge_id)
        bloods.append({
            "challenge_id": s.challenge_id,
            "challenge": s.challenge.name,
            "category": s.challenge.category,
            "team": s.team.name if s.team else s.user.name,
            "user": s.user.name,
            "date": s.date.isoformat(),
        })
    standings = []
    for i, r in enumerate(get_standings()):
        standings.append({
            "id": getattr(r, "account_id", i),
            "name": getattr(r, "name", "?"),
            "score": int(getattr(r, "score", 0) or 0),
        })
    return {"bloods": bloods, "standings": standings}



@bp.route("/bigscreen/data")
def data():
    _check()
    now = time.time()
    if _cache["v"] is None or now - _cache["t"] > CACHE_SECONDS:
        _cache["v"] = _build()
        _cache["t"] = now
    return _no_store(jsonify(_cache["v"]))



@bp.route("/bigscreen/blood.mp3")
def sound():
    _check()
    return send_from_directory(HERE, "blood.mp3", max_age=3600)



PAGE = r"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>First Blood · Live</title>
<link rel="stylesheet" href="/themes/mytheme/static/custom/css/capture-the-cup.css">
<style>
:root{--void:#02040b;--panel:#0a1429;--raised:#111f3b;--ink:#eaf6ff;--muted:#8295b8;--blue:#397dff;--cyan:#55e7ff;--violet:#8b5cff;--line:rgba(116,174,255,.22)}
*{box-sizing:border-box}html,body{height:100%}body{margin:0;overflow:hidden;color:var(--ink);font-family:Lato,system-ui,sans-serif;background:var(--void)}h1,h2,.title{font-family:Raleway,Lato,sans-serif}
/* Cosmic background */
.space{position:fixed;inset:0;z-index:0;pointer-events:none;background:radial-gradient(ellipse at 50% 52%,rgba(31,77,160,.2),transparent 48%),radial-gradient(circle at 12% 5%,rgba(64,123,255,.12),transparent 35%),radial-gradient(circle at 90% 75%,rgba(111,62,255,.1),transparent 36%),#02040b}
.space:before{content:"";position:absolute;inset:0;background:linear-gradient(90deg,transparent 49.9%,rgba(67,139,255,.09) 50%,transparent 50.1%),linear-gradient(transparent 49.9%,rgba(67,139,255,.07) 50%,transparent 50.1%);background-size:9vw 9vw;opacity:.45}
.space:after{content:"";position:absolute;inset:0;background:radial-gradient(ellipse at center,transparent 42%,rgba(0,0,0,.58) 100%)}
.app{position:relative;z-index:1;display:grid;grid-template-rows:auto minmax(0,1fr);height:100vh;padding:.9rem 1.4rem 1rem;gap:.6rem}
header{position:relative;display:flex;flex-wrap:wrap;align-items:center;gap:1rem;padding-bottom:.7rem}header::after{content:"";position:absolute;left:0;right:0;bottom:0;height:2px;background:linear-gradient(90deg,var(--blue),var(--cyan),var(--violet));box-shadow:0 0 16px rgba(85,231,255,.5)}
header img{height:clamp(36px,6vh,64px)}header h1{margin:0;font-size:clamp(1.2rem,3.2vh,2.2rem);letter-spacing:.14em;text-transform:uppercase;text-shadow:0 0 18px rgba(56,189,248,.45)}
.live{margin-left:1.2rem;display:flex;align-items:center;gap:.5rem;font-size:clamp(.8rem,1.8vh,1.1rem);color:var(--cyan)}.dot{width:.7em;height:.7em;border-radius:50%;background:var(--cyan);box-shadow:0 0 10px var(--cyan);animation:pulse 1.4s infinite}.dot.off{background:#ff647c;box-shadow:0 0 10px #ff647c;animation:none}@keyframes pulse{50%{opacity:.25}}
main{display:grid;min-height:0;align-items:stretch;align-content:stretch;padding:0;margin:0}.app main section{display:flex;flex-direction:column;min-height:0;padding:0;margin:0;height:100%}.app main h2{margin:0 0 .5rem;padding:0;line-height:1.1;color:var(--cyan);letter-spacing:.18em;font-size:clamp(.85rem,2vh,1.2rem)}
#board{display:grid;gap:6px;flex:1;min-height:0;overflow:hidden;align-content:start}.row{position:relative;display:flex;align-items:center;justify-content:space-between;gap:.8rem;background:linear-gradient(90deg,rgba(15,28,52,.92),rgba(6,13,27,.94));border:1px solid var(--line);border-left:4px solid var(--line);border-radius:8px;padding:0 1rem;min-width:0}.nm{display:flex;align-items:center;overflow:hidden;white-space:nowrap;text-overflow:ellipsis}.rk{min-width:2.2em;opacity:.65;font-variant-numeric:tabular-nums}.row b{color:var(--cyan);font-variant-numeric:tabular-nums;background:rgba(2,4,11,.7);border:1px solid var(--line);border-radius:6px;padding:0 .45em;line-height:1.35}.ci{width:1.2em;height:1.2em;margin-right:.45em;flex:none;filter:drop-shadow(0 0 6px rgba(85,231,255,.8))}
.row.r1{border-left-color:var(--cyan);border-color:rgba(85,231,255,.5);background:linear-gradient(90deg,rgba(40,124,255,.25),rgba(6,13,27,.92) 60%);box-shadow:0 0 22px rgba(56,189,248,.18)}.row.r2{border-left-color:var(--blue);background:linear-gradient(90deg,rgba(57,125,255,.14),rgba(6,13,27,.92) 55%)}.row.r3{border-left-color:var(--violet);background:linear-gradient(90deg,rgba(139,92,255,.14),rgba(6,13,27,.92) 55%)}.row.up{animation:rowflash 1.6s}@keyframes rowflash{0%{background:#123c76;transform:scale(1.02)}100%{transform:none}}
.fb-card{position:relative;margin-left:auto;display:flex;align-items:center;gap:.8rem;min-width:0;max-width:min(58vw,52rem);padding:.4rem 1.1rem .4rem 1.2rem;background:linear-gradient(145deg,var(--raised),var(--panel));border:1px solid var(--line);border-radius:8px;box-shadow:0 0 24px rgba(47,140,255,.16)}.fb-card::before{content:"";position:absolute;inset:0 auto 0 0;width:4px;border-radius:8px 0 0 8px;background:linear-gradient(var(--blue),var(--cyan));box-shadow:0 0 12px var(--blue)}.fb-star{width:clamp(30px,4.6vh,46px);height:clamp(30px,4.6vh,46px);flex:none;filter:drop-shadow(0 0 8px rgba(85,231,255,.7))}.fb-body{min-width:0}.fb-label{color:var(--cyan);font-size:clamp(.6rem,1.2vh,.75rem);font-weight:800;letter-spacing:.18em}.fb-line{display:flex;align-items:baseline;gap:.8rem;min-width:0;white-space:nowrap}.fb-team{font-family:Raleway,Lato,sans-serif;font-size:clamp(1rem,2.6vh,1.6rem);font-weight:800;overflow:hidden;text-overflow:ellipsis;flex:0 1 auto}.fb-chal{font-size:clamp(.8rem,1.8vh,1.05rem);color:var(--cyan);overflow:hidden;text-overflow:ellipsis;flex:0 1 auto}.fb-meta{color:var(--muted);font-size:clamp(.7rem,1.4vh,.85rem);overflow:hidden;text-overflow:ellipsis;flex:0 100 auto}.fb-card.empty{opacity:.7}
/* First-blood star event */
#overlay{position:fixed;inset:0;display:none;align-items:center;justify-content:center;z-index:10;overflow:hidden;background:radial-gradient(circle at 50% 50%,rgba(32,91,190,.22),transparent 48%),#02040b}#overlay.show{display:flex;animation:fadein .3s}@keyframes fadein{from{opacity:0}}
#stars,#particles{position:absolute;inset:0;pointer-events:none}.starfield i{position:absolute;width:2px;height:2px;border-radius:50%;background:#d8f7ff;box-shadow:0 0 8px #55e7ff;opacity:var(--o);animation:twinkle var(--t) ease-in-out var(--d) infinite alternate}@keyframes twinkle{to{opacity:.15;transform:scale(.45)}}
.gridfloor{position:absolute;left:-35%;right:-35%;bottom:-8vh;height:58vh;z-index:0;pointer-events:none;background:linear-gradient(rgba(64,148,255,.28) 1px,transparent 1px),linear-gradient(90deg,rgba(64,148,255,.25) 1px,transparent 1px);background-size:7vw 7vw;transform:perspective(500px) rotateX(66deg);transform-origin:50% 100%;mask-image:linear-gradient(to top,#000 10%,transparent 90%);animation:floorflow 2.5s linear infinite}@keyframes floorflow{to{background-position:0 7vw,7vw 0}}
#particles b{position:absolute;left:var(--x);top:var(--y);width:var(--s);height:var(--s);border-radius:50%;background:var(--c);box-shadow:0 0 12px var(--c);opacity:0;animation:particleburst var(--dur) ease-out var(--delay) forwards}@keyframes particleburst{0%{opacity:0;transform:translate(0,0) scale(.3)}12%{opacity:1}100%{opacity:0;transform:translate(var(--dx),var(--dy)) scale(.05)}}
.event{position:relative;z-index:3;display:flex;flex-direction:column;align-items:center;text-align:center;padding:0 2vw;min-width:0}.star-stage{position:relative;width:min(42vw,52vh);aspect-ratio:1;display:grid;place-items:center;margin-bottom:-1vh}
.star-core{position:relative;width:23%;aspect-ratio:1;border-radius:50%;background:radial-gradient(circle at 35% 30%,#fff 0 12%,#d9fbff 30%,#72eaff 48%,#3584ff 68%,transparent 74%);box-shadow:0 0 22px 10px rgba(85,231,255,.9),0 0 80px 38px rgba(56,139,255,.55),0 0 180px 80px rgba(93,66,255,.22);animation:ignite .95s cubic-bezier(.2,.8,.2,1) .35s both,starpulse 2.8s ease-in-out 1.4s infinite}@keyframes ignite{0%{transform:scale(.05);opacity:0;filter:blur(20px)}65%{transform:scale(1.7);opacity:1;filter:blur(0)}100%{transform:scale(1)}}@keyframes starpulse{50%{transform:scale(1.13);filter:brightness(1.35)}}
.star-core:before{content:"";position:absolute;inset:-90%;border-radius:50%;background:radial-gradient(circle,rgba(117,235,255,.22),transparent 60%);animation:halo 3s ease-in-out infinite}@keyframes halo{50%{transform:scale(1.2);opacity:.4}}
.orbit{position:absolute;border:1px solid rgba(85,231,255,.5);border-radius:50%;width:68%;height:68%;transform:rotate(-28deg);box-shadow:0 0 18px rgba(56,139,255,.15);opacity:0;animation:orbitin 1.1s ease-out .8s forwards,orbitspin 18s linear 2s infinite}.orbit.o2{width:92%;height:38%;border-color:rgba(139,92,255,.65);transform:rotate(32deg);animation:orbitin 1.1s ease-out 1s forwards,orbitspin 24s linear 2s infinite reverse}.orbit.o3{width:104%;height:104%;border-color:rgba(85,231,255,.2);animation:orbitin 1.2s ease-out 1.1s forwards,orbitspin 30s linear 2s infinite}@keyframes orbitin{from{opacity:0;transform:scale(.1) rotate(0)}to{opacity:1}}@keyframes orbitspin{to{transform:rotate(360deg)}}
.ring{position:absolute;left:50%;top:50%;width:20%;aspect-ratio:1;border:2px solid var(--cyan);border-radius:50%;opacity:0;transform:translate(-50%,-50%) scale(.1);box-shadow:0 0 20px var(--blue),inset 0 0 20px rgba(57,125,255,.4);animation:shock 1.6s ease-out 1.15s both}.ring.r2{border-color:var(--violet);animation-delay:1.35s}.ring.r3{border-color:#fff;animation-delay:1.5s}@keyframes shock{0%{transform:translate(-50%,-50%) scale(.1);opacity:.9}100%{transform:translate(-50%,-50%) scale(12);opacity:0}}
.eyebrow{margin-top:.2vh;color:var(--cyan);font-weight:900;letter-spacing:.42em;font-size:clamp(1rem,2.6vh,1.8rem);text-shadow:0 0 12px var(--cyan),0 0 34px var(--blue);animation:rise .6s ease-out 1.15s both,glitchblink 3s ease-in-out 2s infinite}@keyframes glitchblink{48%,52%{opacity:1}50%{opacity:.5}}
.title{position:relative;display:inline-block;white-space:nowrap;margin:.2vh 0;font-size:min(12vh,11vw);font-weight:900;line-height:1;letter-spacing:.04em;color:#fff;text-shadow:0 0 28px rgba(85,231,255,.75),0 0 80px rgba(47,140,255,.5);animation:titlepop .75s cubic-bezier(.2,.9,.2,1.1) 1.15s both}.title:before,.title:after{content:attr(data-text);position:absolute;left:0;top:0;width:100%;pointer-events:none;mix-blend-mode:screen}.title:before{color:#55e7ff;transform:translate(-.025em,0);animation:glitch1 2.5s ease-in-out 2s infinite}.title:after{color:#8b5cff;transform:translate(.025em,0);animation:glitch2 2.5s ease-in-out 2s infinite}@keyframes glitch1{50%{transform:translate(-.07em,.015em)}}@keyframes glitch2{50%{transform:translate(.07em,-.015em)}}@keyframes titlepop{0%{transform:scale(2.8);opacity:0;filter:blur(18px)}65%{transform:scale(.95);opacity:1;filter:none}100%{transform:scale(1)}}
.team{position:relative;margin:1.2vh 0 .5vh;padding-bottom:1.3vh;max-width:92vw;font-family:Raleway,Lato,sans-serif;font-size:min(8.5vh,8.5vw);font-weight:800;word-break:break-word;text-shadow:0 0 40px rgba(56,189,248,.6);animation:rise .7s ease-out 1.5s both}.team:after{content:"";position:absolute;left:50%;bottom:0;height:3px;width:0;transform:translateX(-50%);background:linear-gradient(90deg,var(--blue),var(--cyan),var(--violet));box-shadow:0 0 14px var(--cyan);animation:bar 1s ease-out 1.8s forwards}@keyframes bar{to{width:80%}}
.plate{display:inline-flex;align-items:stretch;margin-top:1.3vh;font-weight:800;font-size:clamp(1rem,3.4vh,2.3rem);box-shadow:0 0 30px rgba(47,140,255,.25);animation:plate .6s ease-out 1.85s both}.plate .cat{background:rgba(47,125,255,.35);border:1px solid var(--blue);padding:.15em .7em;letter-spacing:.14em;text-transform:uppercase}.plate .chal{background:rgba(85,231,255,.08);border:1px solid rgba(85,231,255,.6);border-left:0;padding:.15em .8em;color:var(--cyan)}@keyframes plate{from{transform:translateY(24px);opacity:0}}
.by{font-size:clamp(1rem,2.6vh,1.8rem);color:var(--muted);margin-top:1.2vh;animation:rise .6s ease-out 2.1s both}@keyframes rise{from{transform:translateY(30px);opacity:0}}
.ticker{position:absolute;left:0;right:0;bottom:0;z-index:4;height:clamp(28px,5.2vh,56px);display:flex;align-items:center;overflow:hidden;background:linear-gradient(90deg,#1456d6,#18aee6,#6040c9);box-shadow:0 -6px 30px rgba(47,140,255,.4);transform:translateY(105%);animation:tkup .5s ease-out 1.8s forwards}#tk{white-space:nowrap;font-weight:900;letter-spacing:.2em;font-size:clamp(.8rem,2.4vh,1.4rem);animation:marq 26s linear infinite}@keyframes tkup{to{transform:none}}@keyframes marq{to{transform:translateX(-50%)}}
.wipe{position:absolute;top:-10%;bottom:-10%;width:150%;left:-170%;z-index:9;pointer-events:none;transform:skewX(-20deg);animation:wipe .85s cubic-bezier(.7,0,.3,1) forwards}.wipe.a{background:#3478ff}.wipe.b{background:#55e7ff;animation-delay:.1s}@keyframes wipe{from{left:-170%}to{left:130%}}.whiteout{position:absolute;inset:0;z-index:8;background:#fff;opacity:0;pointer-events:none;animation:whiteout .9s ease-out 1.1s forwards}@keyframes whiteout{0%{opacity:0}3%{opacity:1}100%{opacity:0}}
#gate{position:fixed;inset:0;z-index:20;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:1.2rem;background:radial-gradient(circle at center,rgba(47,125,255,.24),transparent 48%),#02040b;cursor:pointer;text-align:center}#gate svg{width:clamp(90px,20vh,200px);filter:drop-shadow(0 0 24px rgba(85,231,255,.8));animation:gatefloat 2.4s ease-in-out infinite}#gate b{font-family:Raleway,Lato,sans-serif;letter-spacing:.3em;font-size:clamp(1.2rem,4vh,2.4rem);text-shadow:0 0 22px var(--blue)}#gate span{color:var(--muted);letter-spacing:.08em}@keyframes gatefloat{50%{transform:translateY(-2vh) scale(1.04)}}
@media(max-width:900px){.fb-meta{display:none}}@media(max-width:620px){.app{padding:.9rem 1rem}.fb-card{order:3;flex-basis:100%;max-width:none;margin-left:0}}@media(prefers-reduced-motion:reduce){*,*:before,*:after{animation-duration:.01ms!important;animation-iteration-count:1!important}}
</style></head><body>
<div class="space"></div>
<div id="gate"><svg viewBox="0 0 100 100"><defs><radialGradient id="g"><stop stop-color="#fff"/><stop offset=".3" stop-color="#b9f9ff"/><stop offset=".7" stop-color="#4d9dff"/><stop offset="1" stop-color="#182b78"/></radialGradient></defs><path d="M50 3 60 37 94 50 60 60 50 97 39 60 6 50 39 39Z" fill="url(#g)"/><circle cx="50" cy="50" r="10" fill="white"/></svg><b>ENTER THE DIGITAL NIGHT</b><span>Click once to launch the big screen and enable sound</span></div>
<div class="app"><header><img src="/themes/mytheme/static/img/logo1.png" alt="" onerror="this.style.display='none'"><h1>Digital Night · CTF</h1><aside class="fb-card empty" id="fb" aria-live="polite"><svg class="fb-star" viewBox="0 0 100 100"><path d="M50 3 61 39 97 50 61 61 50 97 39 61 3 50 39 39Z" fill="#8beeff"/><circle cx="50" cy="50" r="11" fill="#fff"/></svg><div class="fb-body"><div class="fb-label">LATEST FIRST BLOOD</div><div class="fb-line"><span class="fb-team" id="fb-team">Waiting for the first solve</span><span class="fb-chal" id="fb-chal">The next capture appears here</span><span class="fb-meta" id="fb-meta"></span></div></div></aside><div class="live"><span class="dot" id="dot"></span><span id="status">LIVE</span></div></header><main><section><h2>SCOREBOARD <span id="count" style="opacity:.6"></span></h2><div id="board"></div></section></main></div>
<div id="overlay"><div class="gridfloor"></div><div class="starfield" id="stars"></div><div id="particles"></div><div class="event"><div class="star-stage"><div class="orbit"></div><div class="orbit o2"></div><div class="orbit o3"></div><div class="star-core"></div><i class="ring"></i><i class="ring r2"></i><i class="ring r3"></i></div><div class="eyebrow">SIGNAL DETECTED · NEW CAPTURE</div><div class="title" data-text="FIRST BLOOD">FIRST BLOOD</div><div class="team" id="ot"></div><div class="plate"><span class="cat" id="ocat"></span><span class="chal" id="oc"></span></div><div class="by" id="ob"></div></div><div class="ticker"><div id="tk"></div></div><div class="wipe a"></div><div class="wipe b"></div><div class="whiteout"></div></div>
<script>
const key=new URLSearchParams(location.search).get("key");const $=id=>document.getElementById(id);const boardEl=$("board"),overlay=$("overlay");const esc=s=>String(s).replace(/[&<>\"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));let known=null,queue=[],showing=false,prev={},lastN=0,soundOn=false;
const snd=new Audio("/bigscreen/blood.mp3?key="+encodeURIComponent(key));snd.preload="auto";
$("gate").onclick=()=>{snd.volume=0;snd.play().then(()=>{snd.pause();snd.currentTime=0;snd.volume=1;soundOn=true;}).catch(()=>{});$("gate").remove();if(document.documentElement.requestFullscreen)document.documentElement.requestFullscreen().catch(()=>{});};
(function makeStars(){const box=$("stars");for(let i=0;i<180;i++){const s=document.createElement("i");s.style.cssText=`left:${Math.random()*100}%;top:${Math.random()*100}%;--o:${.15+Math.random()*.7};--t:${1.5+Math.random()*4}s;--d:${Math.random()*3}s`;box.appendChild(s);}})();
function burst(){const box=$("particles");box.innerHTML="";const colors=["#55e7ff","#ffffff","#397dff","#8b5cff"];for(let i=0;i<130;i++){const p=document.createElement("b"),a=Math.random()*Math.PI*2,dist=180+Math.random()*Math.min(innerWidth,innerHeight)*.55;p.style.cssText=`--x:${50+(Math.random()-.5)*8}%;--y:${48+(Math.random()-.5)*8}%;--s:${1+Math.random()*4}px;--c:${colors[i%colors.length]};--dur:${1.4+Math.random()*2.6}s;--delay:${.4+Math.random()*1.2}s;--dx:${Math.cos(a)*dist}px;--dy:${Math.sin(a)*dist}px`;box.appendChild(p);}}
function next(){if(!queue.length){showing=false;return;}showing=true;const b=queue.shift();$("ot").textContent=b.team;$("ocat").textContent=b.category;$("oc").textContent=b.challenge;$("ob").textContent=b.user!==b.team?"captured by "+b.user:"";$("tk").textContent=("FIRST BLOOD ✦ "+b.team+" ✦ "+b.challenge+" ✦ ").repeat(14);overlay.className="";void overlay.offsetWidth;burst();overlay.className="show";if(soundOn){snd.currentTime=0;snd.play().catch(()=>{});}setTimeout(()=>{overlay.className="";setTimeout(next,500);},10000);}
function renderLatest(bloods){const b=bloods[bloods.length-1];if(!b)return;$("fb").classList.remove("empty");$("fb-team").textContent=b.team;$("fb-chal").textContent=b.challenge+" / "+b.category;$("fb-meta").textContent=b.user!==b.team?"captured by "+b.user:"first solve recorded";}
function layout(n){const H=boardEl.clientHeight,W=boardEl.clientWidth,GAP=5,MIN=34,MAX=58;const cap=Math.max(1,Math.floor((H+GAP)/(MIN+GAP)));let cols=Math.min(4,Math.max(1,Math.ceil(n/cap)));if(W<700)cols=1;const rows=Math.max(1,Math.ceil(n/cols));const rowH=Math.max(MIN,Math.min(MAX,Math.floor((H-(rows-1)*GAP)/rows)));boardEl.style.gridAutoFlow="column";boardEl.style.gridTemplateColumns="repeat("+cols+",1fr)";boardEl.style.rowGap=GAP+"px";boardEl.style.gridTemplateRows="repeat("+rows+","+rowH+"px)";boardEl.style.fontSize=Math.max(13,rowH*.4)+"px";}
function render(standings){const keep=boardEl.scrollTop;layout(standings.length);if(!standings.length){boardEl.innerHTML='<div class="empty">No scores yet</div>';}else{boardEl.innerHTML=standings.map((t,i)=>{const old=prev[t.id];let cls="row";if(i<3)cls+=" r"+(i+1);if(old!==undefined&&t.score>old)cls+=" up";const icon=i===0?`<svg class="ci" viewBox="0 0 100 100"><path d="M50 3 61 39 97 50 61 61 50 97 39 61 3 50 39 39Z" fill="#55e7ff"/><circle cx="50" cy="50" r="10" fill="#fff"/></svg>`:"";return '<div class="'+cls+'">' + '<span class="nm"><span class="rk">'+(i+1)+'.</span>'+icon+esc(t.name)+'</span><b>'+t.score+'</b></div>';}).join("");}prev={};standings.forEach(t=>prev[t.id]=t.score);boardEl.scrollTop=keep;$("count").textContent="("+standings.length+")";lastN=standings.length;}
async function tick(){try{const r=await fetch("/bigscreen/data?key="+encodeURIComponent(key),{cache:"no-store"});if(!r.ok)throw new Error(r.status);const d=await r.json();if(known===null){known=new Set(d.bloods.map(b=>b.challenge_id));}else{d.bloods.forEach(b=>{if(!known.has(b.challenge_id)){known.add(b.challenge_id);queue.push(b);}});}if(!showing)next();renderLatest(d.bloods);render(d.standings);$("dot").className="dot";$('status').textContent="LIVE · SOUND "+(soundOn?"ON":"OFF");}catch(e){$("dot").className="dot off";$('status').textContent="RECONNECTING";}}
document.addEventListener("keydown",e=>{if(e.key.toLowerCase()==="t"){queue.push({team:"Demo Team",challenge:"Test Challenge",category:"web",user:"demo player"});if(!showing)next();}});let dir=1;setInterval(()=>{if(boardEl.scrollHeight<=boardEl.clientHeight+2)return;boardEl.scrollTop+=dir;if(boardEl.scrollTop+boardEl.clientHeight>=boardEl.scrollHeight-1)dir=-1;else if(boardEl.scrollTop<=0)dir=1;},40);window.addEventListener("resize",()=>layout(lastN));tick();setInterval(tick,3000);
</script></body></html>"""


@bp.route("/bigscreen")
def page():
    _check()
    return _no_store(Response(PAGE, mimetype="text/html"))



def load(app):
    app.register_blueprint(bp)