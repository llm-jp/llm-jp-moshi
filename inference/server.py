#!/usr/bin/env python3
import argparse
import asyncio
import hashlib
import json
import random

import numpy as np
import sentencepiece
import torch
from aiohttp import WSMsgType, web
from huggingface_hub import hf_hub_download

from moshi.client_utils import make_log
from moshi.models import LMGen, loaders



def log(level: str, msg: str):
    print(make_log(level, msg))


MODEL_NAME = "LLM-jp-Moshi-v1.1-topic-prompted"

TOPICAL_PROMPTS = [
 "最近ハマっている趣味や休日の過ごし方の話から始めて、相手に質問しながら雑談します。",
 "最近の物価高と、節約や家事の工夫の話から始めて、相手に質問しながら雑談します。",
 "健康づくりや美容で気をつけていることの話から始めて、相手に質問しながら雑談します。",
 "結婚式やお葬式などのマナー、家族の行事の話から始めて、相手に質問しながら雑談します。",
 "恋愛や結婚、人間関係の悩みの話から始めて、相手に質問しながら雑談します。",
 "学生時代の思い出や、学校のことの話から始めて、相手に質問しながら雑談します。",
 "サブスクやネットショッピングの使い方の話から始めて、相手に質問しながら雑談します。",
 "最近の家電やスマートウォッチ、便利な生活アプリの話から始めて、相手に質問しながら雑談します。",
 "aiやvrなどの新しい技術と、デジタル依存の話から始めて、相手に質問しながら雑談します。",
 "勉強や大学での学び、学び直しの話から始めて、相手に質問しながら雑談します。",
 "投資やふるさと納税、老後のお金の話から始めて、相手に質問しながら雑談します。",
 "最近のニュースや災害、社会の出来事の話から始めて、相手に質問しながら雑談します。",
 "仕事やキャリア、子どもの頃の夢の話から始めて、相手に質問しながら雑談します。",
 "アウトドアやスポーツ、運動の習慣の話から始めて、相手に質問しながら雑談します。",
 "旅行や温泉、お出かけの計画の話から始めて、相手に質問しながら雑談します。",
]
DEFAULT_PROMPT = TOPICAL_PROMPTS[-1]


def build_prefix(role_ids, silence, sine, n_streams, n_main, text_pad, delim=5, pause=6):
    def tile(c, L):
        return np.tile(c, (1, -(-L // c.shape[1])))[:, :L]
    Lt = len(role_ids)
    T = pause + (1 + Lt + 1) + pause
    p = np.empty((n_streams, T), dtype=np.int64)
    p[0, :] = text_pad
    p[1:1 + n_main] = tile(silence, T)
    p[1 + n_main:] = tile(sine, T)[: n_streams - 1 - n_main]
    c = pause
    p[0, c] = delim
    p[0, c + 1:c + 1 + Lt] = role_ids
    p[0, c + 1 + Lt] = delim
    return p

PAGE = """<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>__MODEL_NAME__</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#020617;color:#e2e8f0;font-family:system-ui,-apple-system,sans-serif;
     min-height:100vh;display:flex;flex-direction:column;align-items:center;padding:20px 16px}
.mono{font-family:ui-monospace,SFMono-Regular,monospace}
.wrap{width:100%;max-width:980px;display:flex;flex-direction:column;gap:14px}
.head{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap}
.title{font-size:11px;letter-spacing:.2em;text-transform:uppercase;color:#60a5fa;font-weight:700}
.status{display:flex;align-items:center;gap:8px}
.dot{height:12px;width:12px;border-radius:9999px;background:#475569}
.dot.on{background:#22c55e;animation:pulse 1.5s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.4}}
.stlabel{font-size:10px;letter-spacing:.2em;text-transform:uppercase;color:#64748b}
.card{background:#0f172a;border:1px solid rgba(255,255,255,.08);border-radius:14px;padding:14px 16px}
.card .lb{font-size:10px;letter-spacing:.15em;text-transform:uppercase;color:#60a5fa;
          font-weight:700;margin-bottom:6px}
.card .nt{font-size:11px;color:#64748b;margin-bottom:8px;line-height:1.6}
select,textarea{width:100%;background:#020617;color:#e2e8f0;border:1px solid rgba(255,255,255,.14);
  border-radius:8px;padding:8px 10px;font-size:13px;font-family:inherit}
textarea{margin-top:8px;min-height:3.6em;resize:vertical}
.frame{background:#0f172a;border:8px solid #1e293b;border-radius:2rem;overflow:hidden;
       box-shadow:0 25px 50px -12px rgba(0,0,0,.6)}
.bar{display:flex;justify-content:center;align-items:center;gap:10px;padding:12px;
     background:rgba(15,23,42,.5);border-bottom:1px solid rgba(255,255,255,.05)}
button{cursor:pointer;border:none;border-radius:8px;padding:9px 26px;font-weight:700;
       font-size:11px;letter-spacing:.2em;text-transform:uppercase}
#connect{background:#fff;color:#000}
#connect:hover{background:#e2e8f0}
#disconnect{background:#2563eb;color:#fff;display:none}
#disconnect:hover{background:#1d4ed8}
button:disabled{opacity:.4;cursor:default}
#timer{font-size:11px;color:#64748b;min-width:52px;text-align:right}
.cv{display:block;width:100%;height:auto;background:#fff}
</style></head><body>
<div class="wrap">
  <div class="head">
    <div class="title mono">__MODEL_NAME__</div>
    <div class="status"><div class="dot" id="dot"></div>
      <span class="stlabel mono" id="stlabel">DISCONNECTED</span></div>
  </div>
  <div class="card" id="promptcard">
    <div class="lb mono">テキストプロンプト</div>
    <div class="nt">会話開始前にモデルへ渡す話題の指示。対応しているのはプリセットの15話題のみ。
      大文字英字・全角数字は語彙に無いので使わない。空欄なら条件づけ無しで動く。</div>
    <select id="preset"><option value="">プリセット（学習済み15話題）</option></select>
    <textarea id="ptext"></textarea>
  </div>
  <div class="frame">
    <div class="bar">
      <button id="connect">接続（マイク許可）</button>
      <button id="disconnect">切断</button>
      <span id="timer" class="mono">0:00</span>
    </div>
    <canvas id="cv" class="cv" width="1920" height="1080"></canvas>
  </div>
</div>
<script>
const $=i=>document.getElementById(i);
const N=500;
let ws=null,actx=null,proc=null,src=null,stream=null,playAt=0,running=false;
let aiAnalyser=null,humanAnalyser=null;
let aiHist=[],huHist=[],aiDisp=new Array(N).fill(0),huDisp=new Array(N).fill(0);
let tokens=[],micDur=0,playedDur=0,ctxStart=0,t0=null,demoMode=false;

fetch('/api/prompt').then(r=>r.json()).then(d=>{
  const saved=localStorage.getItem('topic_prompt');
  $('ptext').value=saved!==null?saved:d.prompt;
  for(const p of d.presets){const o=document.createElement('option');
    o.value=p;o.textContent=p.split('の話から始めて')[0];$('preset').appendChild(o);}
});
$('preset').onchange=()=>{if($('preset').value){$('ptext').value=$('preset').value;
  localStorage.setItem('topic_prompt',$('preset').value);}};
$('ptext').oninput=()=>localStorage.setItem('topic_prompt',$('ptext').value);

function amp(an){
  if(!an)return 0;
  const len=Math.min(an.fftSize||2048,512);
  const d=new Uint8Array(len);
  an.getByteTimeDomainData(d);
  let s=0,c=0;const st=Math.max(1,Math.floor(len/128));
  for(let i=0;i<len;i+=st){const v=(d[i]-128)/128;s+=v*v;c++;}
  return Math.min(Math.max(Math.sqrt(s/c),0),1);
}
function smooth(a,w){
  const h=Math.floor(w/2),out=new Array(a.length);
  for(let i=0;i<a.length;i++){let s=0,c=0;
    for(let j=Math.max(0,i-h);j<=Math.min(a.length-1,i+h);j++){s+=a[j];c++;}
    out[i]=s/c;}
  return out;
}
function live(){
  const lt=t0===null?0:Math.max(0,Date.now()/1000-t0);
  const ld=Math.max(lt,1);
  return [lt,ld];
}
setInterval(()=>{
  if(t0===null||demoMode)return;
  aiHist.push(amp(aiAnalyser)); if(aiHist.length>N)aiHist.shift();
  let e=aiHist.slice(); while(e.length<N)e.unshift(0); aiDisp=smooth(e,5);
  huHist.push(amp(humanAnalyser)); if(huHist.length>N)huHist.shift();
  e=huHist.slice(); while(e.length<N)e.unshift(0); huDisp=smooth(e,5);
},1000/30);

function draw(){
  const cv=$('cv'),c=cv.getContext('2d'),W=cv.width,H=cv.height;
  const sx=W/1920,sy=H/1080,s=Math.min(sx,sy);
  c.fillStyle="#FFFFFF";c.fillRect(0,0,W,H);
  const centerX=Math.round(W/2);
  if(t0===null){
    c.textAlign="center";
    c.fillStyle="#8DBAE8";c.font=`bold ${Math.round(64*s)}px system-ui,sans-serif`;
    c.fillText("__MODEL_NAME__",centerX,H/2-20*sy);
    c.fillStyle="#555555";c.font=`${Math.round(28*s)}px system-ui,sans-serif`;
    c.fillText("プロンプトを設定して「接続」を押してください",centerX,H/2+40*sy);
    c.textAlign="left";
    requestAnimationFrame(draw);return;
  }
  const [liveTimeSec,liveDurationSec]=live();
  c.textAlign="center";
  c.fillStyle="#8DBAE8";c.font=`bold ${Math.round(64*s)}px system-ui,sans-serif`;
  c.fillText("__MODEL_NAME__",centerX,Math.round(110*sy));
  const topMargin=Math.round(220*sy),bottomMargin=Math.round(80*sy);
  const availableHeight=H-topMargin-bottomMargin;
  const rowHeight=availableHeight/2;
  const aiCenterY=Math.round(topMargin+rowHeight/2);
  const humanCenterY=Math.round(topMargin+rowHeight+rowHeight/2);
  const leftX=Math.round(W*0.05),rightX=Math.round(W*0.95);
  const waveformWidth=rightX-leftX;
  const t=liveDurationSec>0?Math.min(Math.max(liveTimeSec/liveDurationSec,0),1):0;
  const cursorX=Math.round(leftX+waveformWidth*t);

  const drawEnvelope=(env,centerY,colorBase,alphaPast)=>{
    if(!env.length)return;
    const n=env.length,stepX=waveformWidth/(n-1);
    const hasData=env.some(v=>v>0.01);
    if(hasData){
      c.beginPath();let started=false;
      for(let i=0;i<n;i++){const x=leftX+i*stepX;
        const a=Math.max(env[i],0)*(rowHeight/2)*0.9;
        if(!started){c.moveTo(x,centerY-a);started=true;}else c.lineTo(x,centerY-a);}
      for(let i=n-1;i>=0;i--){const x=leftX+i*stepX;
        const a=Math.max(env[i],0)*(rowHeight/2)*0.9;c.lineTo(x,centerY+a);}
      c.closePath();
      const alphaHex=Math.round(alphaPast*255).toString(16).padStart(2,"0");
      c.fillStyle=`${colorBase}${alphaHex}`;c.fill();
      c.strokeStyle=colorBase;c.lineWidth=1;c.stroke();
    }
    c.strokeStyle="#DDDDDD";c.lineWidth=1;
    c.beginPath();c.moveTo(leftX,centerY);c.lineTo(rightX,centerY);c.stroke();
  };

  const labelFontSize=Math.round(32*s);
  c.textAlign="left";c.textBaseline="middle";
  c.fillStyle="#A78DC9";c.font=`${labelFontSize}px system-ui,sans-serif`;
  c.fillText("AI",Math.round(Math.max(10,leftX-80*sx)),aiCenterY);
  c.fillStyle="#F5A0B4";
  c.fillText("Human",Math.round(Math.max(10,leftX-120*sx)),humanCenterY);

  drawEnvelope(aiDisp,aiCenterY,"#A78DC9",0.85);

  if(tokens.length>0){
    const shown=[];
    for(const tk of tokens){if(tk.time<=t)shown.push(tk);else break;}
    if(shown.length>0){
      const textFontSize=Math.max(22,Math.round(48*s));
      const textY=Math.round(aiCenterY+rowHeight/2+20*sy);
      const curIndex=shown[shown.length-1].index;
      c.textAlign="left";c.textBaseline="top";
      const lineHeight=Math.round(56*s);
      let y=textY;
      c.font=`normal ${textFontSize}px system-ui,sans-serif`;
      const widths=shown.map(tk=>c.measureText(tk.tk).width);
      let currentX=cursorX;
      for(let i=shown.length-1;i>=0;i--){
        const tk=shown[i],tw=widths[i];
        c.font=(tk.index===curIndex)
          ?`bold ${textFontSize}px system-ui,sans-serif`
          :`normal ${textFontSize}px system-ui,sans-serif`;
        c.fillStyle="#333333";
        if(currentX-tw<leftX+10){
          y+=lineHeight;currentX=cursorX;
          if(y>humanCenterY-rowHeight/2-10)break;
        }
        currentX-=tw;
        c.fillText(tk.tk,Math.round(currentX),y);
      }
    }
  }

  drawEnvelope(huDisp,humanCenterY,"#F5A0B4",0.85);

  c.strokeStyle="#7FD9B3";c.lineWidth=Math.max(2,Math.round(3*s));
  c.beginPath();
  c.moveTo(cursorX+0.5,Math.round(topMargin-10));
  c.lineTo(cursorX+0.5,Math.round(H-bottomMargin+10));
  c.stroke();

  const m=Math.floor(liveTimeSec/60),sec=Math.floor(liveTimeSec%60);
  $('timer').textContent=m+":"+String(sec).padStart(2,"0");
  c.textBaseline="alphabetic";
  requestAnimationFrame(draw);
}
requestAnimationFrame(draw);

if(new URLSearchParams(location.search).get('demo')){
  demoMode=true;t0=Date.now()/1000-32;micDur=33;playedDur=33;
  const ae=[],he=[];
  for(let i=0;i<N;i++){const tt=i/N*17;
    ae.push(Math.sin(tt*1.1)>0.2?0.10+0.07*Math.abs(Math.sin(tt*7)):0.004);
    he.push(Math.sin(tt*0.9+2.2)>0.45?0.09+0.06*Math.abs(Math.sin(tt*6)):0.003);}
  aiDisp=smooth(ae,5);huDisp=smooth(he,5);
  const demo="こんにちは何か旅行の予定はありますか?いいですね温泉は好きですか?";
  [...demo].forEach((ch,i)=>tokens.push({tk:ch,time:0.3+i/demo.length*0.65,index:i}));
  $('dot').classList.add('on');$('stlabel').textContent="CONNECTED (DEMO)";
}

$('connect').onclick=async()=>{
  try{
    actx=new AudioContext({sampleRate:24000});await actx.resume();
    stream=await navigator.mediaDevices.getUserMedia({audio:{channelCount:1,
      echoCancellation:true,noiseSuppression:true,autoGainControl:true}});
    aiAnalyser=actx.createAnalyser();aiAnalyser.fftSize=2048;
    humanAnalyser=actx.createAnalyser();humanAnalyser.fftSize=2048;
    aiAnalyser.connect(actx.destination);
    const q="?text_prompt="+encodeURIComponent($('ptext').value.trim());
    ws=new WebSocket((location.protocol==='https:'?'wss://':'ws://')+location.host+'/ws'+q);
    ws.binaryType='arraybuffer';
    ws.onopen=()=>{running=true;t0=Date.now()/1000;ctxStart=actx.currentTime;playAt=actx.currentTime;
      aiHist=[];huHist=[];aiDisp=new Array(N).fill(0);huDisp=new Array(N).fill(0);
      tokens=[];micDur=0;playedDur=0;
      $('dot').classList.add('on');$('stlabel').textContent="CONNECTED";
      $('connect').style.display='none';$('disconnect').style.display='';};
    ws.onclose=stop; ws.onerror=stop;
    ws.onmessage=ev=>{
      if(typeof ev.data==='string'){const m=JSON.parse(ev.data);
        if(m.t==='text'){const [lt,ld]=live();
          tokens.push({tk:m.v,time:Math.min(Math.max(lt/ld,0),1),index:tokens.length});}
        return;}
      const pcm=new Float32Array(ev.data);
      const b=actx.createBuffer(1,pcm.length,24000);b.copyToChannel(pcm,0);
      const sn=actx.createBufferSource();sn.buffer=b;sn.connect(aiAnalyser);
      const now=actx.currentTime;if(playAt<now)playAt=now+0.08;
      sn.start(playAt);playAt+=b.duration;};
    src=actx.createMediaStreamSource(stream);
    src.connect(humanAnalyser);
    proc=actx.createScriptProcessor(2048,1,1);
    proc.onaudioprocess=e=>{const d=e.inputBuffer.getChannelData(0);
      if(running&&ws.readyState===1){ws.send(new Float32Array(d).buffer);micDur+=d.length/24000;}};
    src.connect(proc);proc.connect(actx.destination);
  }catch(err){alert('エラー: '+err);stop();}
};
function stop(){running=false;
  try{proc&&proc.disconnect();src&&src.disconnect();
      stream&&stream.getTracks().forEach(t=>t.stop());ws&&ws.close();}catch(e){}
  $('dot').classList.remove('on');$('stlabel').textContent="DISCONNECTED";
  $('connect').style.display='';$('disconnect').style.display='none';}
$('disconnect').onclick=stop;
</script></body></html>
"""


class WaveServer:
    def __init__(self, mimi, text_tokenizer, lm, device,
                 prefix_npz, default_prompt, prompts=None, prompt_mode="fixed"):
        self.mimi = mimi
        self.tok = text_tokenizer
        self.lm_gen = LMGen(lm)
        self.device = device
        self.frame_size = int(self.mimi.sample_rate / self.mimi.frame_rate)
        self.lock = asyncio.Lock()

        z = np.load(prefix_npz)
        self.silence, self.sine = z["silence"], z["sine"]
        self.n_streams, self.n_main = lm.num_codebooks, lm.dep_q
        self.n_user = lm.num_codebooks - lm.dep_q - 1
        self.text_pad = lm.text_padding_token_id
        self.delim, self.pause = 5, 6
        self.prompt = default_prompt
        self.prompts = prompts or []
        self.prompt_mode = prompt_mode
        self._rr = 0

        self.mimi.streaming_forever(1)
        self.lm_gen.streaming_forever(1)

    def warmup(self):
        for _ in range(4):
            chunk = torch.zeros(1, 1, self.frame_size, dtype=torch.float32, device=self.device)
            codes = self.mimi.encode(chunk)
            for c in range(codes.shape[-1]):
                tokens = self.lm_gen.step(codes[:, :, c:c + 1])
                if tokens is None:
                    continue
                _ = self.mimi.decode(tokens[:, 1:])
        torch.cuda.synchronize()

    def pick_prompt(self, request):

        client_prompt = request.query.get("text_prompt")
        if client_prompt is not None:
            return " ".join(client_prompt.split()), "client"
        seed = request.query.get("prompt_seed")
        if seed and self.prompts:
            h = int(hashlib.sha256(seed.encode("utf-8")).hexdigest(), 16)
            return self.prompts[h % len(self.prompts)], f"seed:{seed[:12]}"
        if self.prompts and self.prompt_mode == "random":
            return random.choice(self.prompts), "server/random"
        if self.prompts and self.prompt_mode == "roundrobin":
            p = self.prompts[self._rr % len(self.prompts)]
            self._rr += 1
            return p, "server/roundrobin"
        return self.prompt, "default"

    def prefill(self, prompt):
        ids = self.tok.encode(prompt)
        pre = build_prefix(ids, self.silence, self.sine, self.n_streams,
                           self.n_main, self.text_pad, self.delim, self.pause)
        st = self.lm_gen._streaming_state
        CT = st.cache.shape[2]
        with torch.no_grad():
            for t in range(pre.shape[1]):
                u = torch.from_numpy(pre[1 + self.n_main:, t]).view(1, self.n_user, 1).to(self.device)
                self.lm_gen.step(u)
                pos = st.offset % CT
                st.cache[:, 0, pos] = int(pre[0, t])
                st.cache[:, 1:self.n_main + 1, pos] = torch.from_numpy(
                    pre[1:1 + self.n_main, t]).view(1, self.n_main).to(self.device)
        return pre.shape[1]

    async def page(self, _):
        return web.Response(text=PAGE.replace("__MODEL_NAME__", MODEL_NAME),
                            content_type="text/html")

    async def api_prompt_get(self, _):
        return web.json_response({"prompt": self.prompt, "presets": TOPICAL_PROMPTS})

    async def api_prompt_post(self, request):
        d = await request.json()
        p = (d.get("prompt") or "").strip()
        if p != self.prompt:
            self.prompt = p
            log("info", f"prompt updated: {p}")
        return web.json_response({"prompt": self.prompt})

    async def handle_ws(self, request):
        ws = web.WebSocketResponse(max_msg_size=0)
        await ws.prepare(request)
        log("info", "accepted connection")
        async with self.lock:
            self.mimi.reset_streaming()
            self.lm_gen.reset_streaming()
            prompt, source = self.pick_prompt(request)
            if prompt.strip():
                n = await asyncio.get_running_loop().run_in_executor(None, self.prefill, prompt)
                log("info", f"prefilled {n} frames ({source}): {prompt}")
            else:
                log("info", f"prefill skipped ({source}: empty prompt)")
            buf = np.zeros(0, dtype=np.float32)
            try:
                async for m in ws:
                    if m.type != WSMsgType.BINARY:
                        if m.type in (WSMsgType.CLOSED, WSMsgType.ERROR):
                            break
                        continue
                    buf = np.concatenate([buf, np.frombuffer(m.data, dtype=np.float32)])
                    while len(buf) >= self.frame_size:
                        chunk, buf = buf[:self.frame_size], buf[self.frame_size:]
                        with torch.no_grad():
                            x = torch.from_numpy(chunk.copy()).to(self.device)[None, None]
                            codes = self.mimi.encode(x)
                            for c in range(codes.shape[-1]):
                                tk = self.lm_gen.step(codes[:, :, c:c + 1])
                                if tk is None:
                                    continue
                                pcm = self.mimi.decode(tk[:, 1:]).cpu()[0, 0].numpy()
                                await ws.send_bytes(pcm.astype(np.float32).tobytes())
                                tt = int(tk[0, 0, 0])
                                if tt not in (0, 3) and tt < 32000:
                                    piece = self.tok.id_to_piece(tt).replace("▁", " ")
                                    await ws.send_str(json.dumps({"t": "text", "v": piece}))
            finally:
                log("info", "connection closed")
        return ws


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", default=8998, type=int)
    parser.add_argument("--tokenizer", type=str)
    parser.add_argument("--moshi-weight", type=str)
    parser.add_argument("--mimi-weight", type=str)
    parser.add_argument("--prefix-tokens-npz", type=str)
    parser.add_argument("--hf-repo", type=str, default="llm-jp/llm-jp-moshi-v1.1-topic-prompted")
    parser.add_argument("--default-prompt", type=str, default=DEFAULT_PROMPT)
    parser.add_argument("--prompt", action="append", default=[])
    parser.add_argument("--prompt-file", type=str, default=None)
    parser.add_argument("--prompt-mode", choices=["fixed", "random", "roundrobin"], default="fixed")
    parser.add_argument("--device", type=str, default="cuda")
    args = parser.parse_args()

    torch.manual_seed(42424242)
    log("info", "loading mimi")
    if args.mimi_weight is None:
        args.mimi_weight = hf_hub_download(args.hf_repo, loaders.MIMI_NAME)
    mimi = loaders.get_mimi(args.mimi_weight, args.device)
    if args.tokenizer is None:
        args.tokenizer = hf_hub_download(args.hf_repo, loaders.TEXT_TOKENIZER_NAME)
    text_tokenizer = sentencepiece.SentencePieceProcessor(args.tokenizer)
    log("info", "loading moshi")
    if args.moshi_weight is None:
        args.moshi_weight = hf_hub_download(args.hf_repo, loaders.MOSHI_NAME)
    lm = loaders.get_moshi_lm(args.moshi_weight, device=args.device)
    if args.prefix_tokens_npz is None:
        args.prefix_tokens_npz = hf_hub_download(args.hf_repo, "prefix_tokens.npz")

    from pathlib import Path
    prompts = [" ".join(p.split()) for p in args.prompt]
    if args.prompt_file:
        prompts += [" ".join(l.split()) for l in Path(args.prompt_file).read_text().splitlines() if l.strip()]

    state = WaveServer(mimi, text_tokenizer, lm, args.device,
                       args.prefix_tokens_npz, args.default_prompt,
                       prompts=prompts, prompt_mode=args.prompt_mode)
    log("info", "warming up the model")
    state.warmup()
    app = web.Application()
    app.router.add_get("/", state.page)
    app.router.add_get("/ws", state.handle_ws)
    app.router.add_get("/api/prompt", state.api_prompt_get)
    app.router.add_post("/api/prompt", state.api_prompt_post)
    log("info", f"Access the Web UI at http://{args.host}:{args.port}")
    web.run_app(app, host=args.host, port=args.port)


if __name__ == "__main__":
    with torch.no_grad():
        main()
