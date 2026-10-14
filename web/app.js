const $=id=>document.getElementById(id),esc=v=>String(v??"—").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[c]));
const money=v=>typeof v==="number"?new Intl.NumberFormat("id-ID",{style:"currency",currency:"USD",maximumFractionDigits:0}).format(v):"—";
const num=(v,d=1)=>typeof v==="number"?v.toFixed(d):"—";
const set=(id,v)=>{const e=$(id);if(e)e.textContent=v};
const pct=v=>typeof v==="number"?Math.max(0,Math.min(1,v))*100:0;
function resize(c){const r=c.getBoundingClientRect(),d=Math.min(devicePixelRatio||1,3),width=Math.max(1,Math.round(r.width*d)),height=Math.max(1,Math.round(r.height*d));if(c.width!==width||c.height!==height){c.width=width;c.height=height}return[c.getContext("2d"),r.width,r.height,d]}
function radar(t){const c=$("radar"),[x,w,h,d]=resize(c);x.clearRect(0,0,c.width,c.height);x.save();x.scale(d,d);const cx=w/2,cy=h/2,r=Math.min(w,h)*.42,a=t*.0005;for(let i=1;i<5;i++){x.beginPath();x.arc(cx,cy,r*i/4,0,7);x.strokeStyle="rgba(0,255,154,.13)";x.stroke()}x.save();x.translate(cx,cy);x.rotate(a);x.beginPath();x.moveTo(0,0);x.lineTo(r,0);x.lineTo(r,.15*r);x.closePath();x.fillStyle="rgba(0,255,154,.12)";x.fill();x.restore();x.beginPath();x.arc(cx,cy,6+2*Math.sin(t/300),0,7);x.fillStyle="#9dffdb";x.shadowBlur=25;x.shadowColor="#00ff9a";x.fill();x.restore()}
function chart(t){const c=$("flow-canvas"),[x,w,h,d]=resize(c);x.clearRect(0,0,c.width,c.height);x.save();x.scale(d,d);for(let i=0;i<5;i++){x.beginPath();x.moveTo(0,i*h/4);x.lineTo(w,i*h/4);x.strokeStyle="#ffffff0a";x.stroke()}const o=window.__data?.opportunities?.[0]||window.__data||{},wallets=window.__data?.sources?.watched_wallets||{},buys=o.onchain_buy_txns,sells=o.onchain_sell_txns;const valid=wallets.status==="COLLECTED"&&typeof buys==="number"&&typeof sells==="number";if(valid){const max=Math.max(buys,sells,1),left=12,right=w-12,barW=right-left;x.font="800 9px ui-monospace";x.textAlign="left";x.fillStyle="#00ff9a";x.fillText("BUY TXNS",left,Math.max(14,h*.30));x.fillStyle="#ef526f";x.fillText("SELL TXNS",left,Math.max(14,h*.64));x.fillStyle="#00ff9a55";x.fillRect(left,h*.34,barW*(buys/max),12);x.fillStyle="#00ff9a";x.fillRect(left,h*.34,Math.max(buys?2:0,barW*(buys/max)),12);x.fillStyle="#ef526f55";x.fillRect(left,h*.68,barW*(sells/max),12);x.fillStyle="#ef526f";x.fillRect(left,h*.68,Math.max(sells?2:0,barW*(sells/max)),12);x.fillStyle="#65758a";x.textAlign="right";x.fillText("RECENT HISTORY · COUNTS ONLY",right,h-5)}else{x.font="800 9px ui-monospace";x.fillStyle="#65758a";x.textAlign="center";x.fillText("REAL BUY/SELL FLOW PENDING",w/2,h/2-5);x.font="8px ui-monospace";x.fillText("NO SYNTHETIC VOLUME OR 5-MINUTE SERIES",w/2,h/2+12)}x.restore()}
function network(t){
 const c=$("network-canvas");if(!c)return;const [x,w,h,d]=resize(c);x.clearRect(0,0,c.width,c.height);x.save();x.scale(d,d);
 const o=window.__data?.opportunities?.[0]||window.__data||{},graph=o.wallet_graph||window.__data?.wallet_graph;
 const nodes=Array.isArray(graph?.nodes)?graph.nodes:[],edges=Array.isArray(graph?.edges)?graph.edges:[];
 const key=n=>String(n?.id??n?.address??""),byId=new Map(nodes.map(n=>[key(n),n]).filter(([id])=>id));
 const cx=w/2,cy=h*.47,r=Math.min(w*.39,h*.34);
 if(nodes.length&&edges.length){
   const positions=new Map(),phase=t*.000012;
   nodes.forEach((node,i)=>{const angle=(i/Math.max(1,nodes.length))*Math.PI*2+phase;const ring=i%4===0?.58:i%3===0?.82:1;positions.set(key(node),{x:cx+Math.cos(angle)*r*ring,y:cy+Math.sin(angle)*r*ring*.72})});
   // Fine orbital rings and a restrained radar sweep frame the evidence-backed graph.
   for(let ring=1;ring<=3;ring++){x.beginPath();x.ellipse(cx,cy,r*ring/3,r*ring/4,phase*.3,0,Math.PI*2);x.strokeStyle="#55d8ff"+(ring===3?"18":"12");x.lineWidth=1;x.stroke()}
   edges.forEach((edge,i)=>{
     const source=String(edge.source??edge.from??""),target=String(edge.target??edge.to??""),a=positions.get(source),b=positions.get(target);
     if(!a||!b||!byId.has(source)||!byId.has(target))return;
     const confirmed=edge.evidence_status==="CONFIRMED_EVIDENCE";
     x.beginPath();x.moveTo(a.x,a.y);const mx=(a.x+b.x)/2+(cy-(a.y+b.y)/2)*.12,my=(a.y+b.y)/2+(cx-(a.x+b.x)/2)*.12;x.quadraticCurveTo(mx,my,b.x,b.y);
     x.strokeStyle=confirmed?"#00ff9a88":"#f6b73c66";x.lineWidth=confirmed?1.5:1;x.stroke();
     // Moving pulse is attached only to a reported graph edge, never invented as a wallet event.
     const p=((t*.00012+i*.173)%1),px=(1-p)*(1-p)*a.x+2*(1-p)*p*mx+p*p*b.x,py=(1-p)*(1-p)*a.y+2*(1-p)*p*my+p*p*b.y;
     x.beginPath();x.arc(px,py,2,0,Math.PI*2);x.fillStyle=confirmed?"#c8ffeb":"#ffd98a";x.shadowBlur=8;x.shadowColor=x.fillStyle;x.fill();x.shadowBlur=0;
   });
   nodes.forEach((node,i)=>{const p=positions.get(key(node));if(!p)return;const confirmed=node.evidence_status==="CONFIRMED_EVIDENCE",rad=confirmed?5.5:4.5;
     x.beginPath();x.arc(p.x,p.y,rad+Math.sin(t*.003+i)*.65,0,Math.PI*2);x.fillStyle=confirmed?"#00ff9a":"#f6b73c";x.shadowBlur=confirmed?16:8;x.shadowColor=x.fillStyle;x.fill();x.shadowBlur=0;x.strokeStyle="#d8fff0aa";x.lineWidth=1;x.stroke();
     if(node.label||node.address||node.id){x.font="8px ui-monospace";x.fillStyle="#9aafbd";x.textAlign=p.x>cx?"left":"right";x.fillText(String(node.label??node.address??node.id).slice(0,10),p.x+(p.x>cx?8:-8),p.y-7)}
   });
   x.font="800 8px ui-monospace";x.fillStyle="#8da7b6";x.textAlign="center";x.fillText(nodes.length+" REPORTED NODES · "+edges.length+" REPORTED RELATIONS",w/2,h-7);
   x.font="7px ui-monospace";x.fillStyle="#5d7c8b";x.fillText("GREEN = CONFIRMED EVIDENCE · AMBER = UNVERIFIED",w/2,12);
 }else{
   // Visual-only scanning animation while verified graph data is absent; no wallet nodes or links are asserted.
   for(let ring=1;ring<=4;ring++){x.beginPath();x.ellipse(cx,cy,r*ring/4,r*ring/3,t*.00008*(ring%2?1:-1),0,Math.PI*2);x.strokeStyle="rgba(55,216,255,"+(0.16/ring)+")";x.stroke()}
   const sweep=(t*.00035)%(Math.PI*2);x.beginPath();x.moveTo(cx,cy);x.arc(cx,cy,r,sweep-.25,sweep);x.closePath();x.fillStyle="#00ff9a0d";x.fill();
   for(let i=0;i<18;i++){const a=t*.00018+i*Math.PI*2/18,rr=r*(.38+.42*(.5+.5*Math.sin(t*.00065+i*1.7))),px=cx+Math.cos(a)*rr,py=cy+Math.sin(a)*rr*.68;
     x.beginPath();x.moveTo(cx,cy);x.lineTo(px,py);x.strokeStyle="rgba(0,255,154,.09)";x.stroke();x.beginPath();x.arc(px,py,1.8+Math.sin(t*.003+i)*.45,0,Math.PI*2);x.fillStyle=i%4===0?"#55d8ff":"#00ff9a";x.shadowBlur=9;x.shadowColor=x.fillStyle;x.fill();x.shadowBlur=0;
   }
   x.beginPath();x.arc(cx,cy,14+Math.sin(t*.003)*2,0,Math.PI*2);x.strokeStyle="#00ff9a77";x.stroke();x.beginPath();x.arc(cx,cy,3,0,Math.PI*2);x.fillStyle="#caffed";x.fill();
   x.font="800 9px ui-monospace";x.fillStyle="#b4c6d3";x.textAlign="center";x.fillText("SMART MONEY GRAPH · AWAITING EVIDENCE",w/2,cy-5);
   x.font="8px ui-monospace";x.fillStyle="#71869a";x.fillText("DECORATIVE SCAN ONLY · NO VERIFIED WALLET SIGNALS",w/2,cy+13);
 }
 x.restore();
}

let selectedTimeframe="minute", candleToken="", candleRequest=0, lastCandles=[];
const priceMoney=v=>typeof v==="number"?new Intl.NumberFormat("en-US",{style:"currency",currency:"USD",maximumFractionDigits:v<1?8:4}).format(v):"—";
function drawCandles(){
 const c=$("price-canvas");if(!c)return;const [ctx,w,h,d]=resize(c);ctx.clearRect(0,0,c.width,c.height);ctx.save();ctx.scale(d,d);
 const pad={l:9,r:61,t:13,b:37},cw=Math.max(1,w-pad.l-pad.r),ch=Math.max(1,h-pad.t-pad.b);
 // Institutional terminal grid, with restrained axis guides.
 for(let i=0;i<5;i++){const y=pad.t+ch*i/4;ctx.beginPath();ctx.moveTo(pad.l,y);ctx.lineTo(w-pad.r,y);ctx.strokeStyle=i===4?"#55d8ff20":"#ffffff0d";ctx.lineWidth=1;ctx.stroke()}
 if(!lastCandles.length){ctx.fillStyle="#71869a";ctx.textAlign="center";ctx.font="10px ui-monospace";ctx.fillText("REAL OHLCV CANDLES UNAVAILABLE",w/2,h/2-3);ctx.font="8px ui-monospace";ctx.fillText("Waiting for a verified pool + source response",w/2,h/2+14);ctx.restore();return}
 const min=Math.min(...lastCandles.map(v=>v.low)),max=Math.max(...lastCandles.map(v=>v.high)),span=max-min||Math.max(max*.02,1e-8),y=v=>pad.t+(max-v)/span*ch;
 const step=cw/lastCandles.length,bodyW=Math.max(2,Math.min(9,step*.64));
 // Real reported volume is drawn as subdued histogram bars beneath the price field.
 const maxVolume=Math.max(0,...lastCandles.map(v=>Number.isFinite(v.volume)?v.volume:0));
 const volumeBase=h-19,volumeH=24;
 lastCandles.forEach((v,i)=>{
   const px=pad.l+step*(i+.5),up=v.close>=v.open,colour=up?"#00e89a":"#ef526f";
   if(maxVolume>0&&Number.isFinite(v.volume)&&v.volume>=0){const bh=Math.max(v.volume>0?1:0,(v.volume/maxVolume)*volumeH);ctx.fillStyle=up?"#00e89a30":"#ef526f30";ctx.fillRect(px-bodyW/2,volumeBase-bh,bodyW,bh)}
   ctx.beginPath();ctx.moveTo(px,y(v.high));ctx.lineTo(px,y(v.low));ctx.strokeStyle=colour;ctx.lineWidth=1;ctx.stroke();
   const top=y(Math.max(v.open,v.close)),bottom=y(Math.min(v.open,v.close)),bh=Math.max(1,bottom-top);
   ctx.fillStyle=colour;ctx.shadowBlur=bh>2?5:0;ctx.shadowColor=colour;ctx.fillRect(px-bodyW/2,top,bodyW,bh);ctx.shadowBlur=0;
   if(bh>3){ctx.fillStyle=up?"#baffdf":"#ffd4dc";ctx.fillRect(px-bodyW/2,top,bodyW,1)}
 });
 const last=lastCandles[lastCandles.length-1],ly=y(last.close);
 ctx.setLineDash([4,3]);ctx.beginPath();ctx.moveTo(pad.l,ly);ctx.lineTo(w-pad.r+3,ly);ctx.strokeStyle="#b5d2e0aa";ctx.stroke();ctx.setLineDash([]);
 const lastUp=last.close>=last.open;ctx.fillStyle=lastUp?"#00e89a":"#ef526f";ctx.shadowBlur=12;ctx.shadowColor=ctx.fillStyle;ctx.fillRect(w-pad.r+3,ly-8,pad.r-5,16);ctx.shadowBlur=0;
 ctx.fillStyle="#04100c";ctx.font="bold 8px ui-monospace";ctx.textAlign="center";ctx.fillText(priceMoney(last.close),w-pad.r/2,ly+3);
 ctx.fillStyle="#71869a";ctx.font="8px ui-monospace";ctx.textAlign="left";ctx.fillText(new Date(lastCandles[0].time*1000).toLocaleTimeString([], {hour:"2-digit",minute:"2-digit"}),pad.l,h-5);
 ctx.textAlign="right";ctx.fillText(new Date(last.time*1000).toLocaleTimeString([], {hour:"2-digit",minute:"2-digit"}),w-pad.r,h-5);
 ctx.textAlign="left";ctx.fillStyle="#536d7c";ctx.fillText("VOL",pad.l,volumeBase-7);
 ctx.restore();
}
async function loadCandles(force=false){
 const token=window.__selectedToken||window.__data?.opportunities?.[0]?.token;if(!token){lastCandles=[];set("candle-status","OHLCV: NO TOKEN");drawCandles();return}
 if(!force&&token===candleToken&&window.__candlesBusy)return;
 candleToken=token;const requestId=++candleRequest;window.__candlesBusy=true;set("price-token",(window.__data?.opportunities?.find(item=>item.token===token)?.symbol||"TOKEN")+" · "+selectedTimeframe.toUpperCase());set("candle-status","OHLCV: FETCHING REAL POOL DATA");
 try{const r=await fetch("/candles?token="+encodeURIComponent(token)+"&timeframe="+encodeURIComponent(selectedTimeframe)+"&t="+Date.now(),{cache:"no-store"});if(!r.ok)throw Error("HTTP "+r.status);const payload=await r.json();if(requestId!==candleRequest)return;
 lastCandles=payload.status==="CONNECTED"&&Array.isArray(payload.candles)?payload.candles.filter(v=>[v.time,v.open,v.high,v.low,v.close,v.volume].every(Number.isFinite)):[];
 set("candle-status",payload.status==="CONNECTED"?"OHLCV: CONNECTED · "+lastCandles.length+" CANDLES":"OHLCV: "+payload.status);
 set("candle-source",payload.pair_address?"POOL "+payload.pair_address.slice(0,5)+"…"+payload.pair_address.slice(-5)+" · GECKOTERMINAL":"GECKOTERMINAL · VERIFIED POOL REQUIRED");
 if(lastCandles.length){const first=lastCandles[0],last=lastCandles[lastCandles.length-1],change=first.close?((last.close-first.open)/first.open*100):0;set("price-last",priceMoney(last.close));set("price-change",(change>=0?"+":"")+change.toFixed(2)+"% · "+(change>=0?"UP":"DOWN"));set("candle-range",lastCandles.length+" bars · "+new Date(last.time*1000).toLocaleString());}
 else{set("price-last","—");set("price-change","NO VERIFIED CANDLES");set("candle-range","No fabricated OHLCV");}
 drawCandles();
 }catch(e){if(requestId===candleRequest){lastCandles=[];set("candle-status","OHLCV: SOURCE UNAVAILABLE");set("price-last","—");set("price-change","RETRYING AUTOMATICALLY");set("candle-range","Chart will not invent values");drawCandles()}}
 finally{if(requestId===candleRequest)window.__candlesBusy=false}
}
document.querySelectorAll("[data-timeframe]").forEach(button=>button.addEventListener("click",()=>{selectedTimeframe=button.dataset.timeframe;document.querySelectorAll("[data-timeframe]").forEach(item=>item.classList.toggle("active",item===button));loadCandles(true)}));

function render(d){window.__data=d;set("last-update","UPDATED "+new Date(d.observed_at||Date.now()).toLocaleTimeString());set("hero-label",d.discovery?.display_mode==="FILTERED_FALLBACK"?"FILTERED CANDIDATE · NOT ENTRY-READY":d.discovery?.display_mode==="QUALIFIED"?"RADAR CANDIDATE · WAIT FOR FULL EVIDENCE":"SCANNING SOLANA");const o=d.opportunities?.[0]||d;const dex=d.sources?.dexscreener||{};set("connection","DEX: "+(dex.status||"UNKNOWN"));const rpc=d.sources?.solana_rpc||{};set("rpc-connection","RPC: "+(rpc.status||"UNKNOWN")+(rpc.slot!=null?" · SLOT "+rpc.slot:""));const dexDot=$("connection")?.previousElementSibling;if(dexDot)dexDot.style.background=dex.status==="CONNECTED"?"#00ff9a":"#ef526f";const rpcDot=$("rpc-connection")?.previousElementSibling;if(rpcDot)rpcDot.style.background=rpc.status==="CONNECTED"?"#00ff9a":rpc.status==="NOT_CONFIGURED"?"#f6b73c":"#ef526f";set("flow-title",rpc.status==="CONNECTED"?"CONNECTED":rpc.status==="UNAVAILABLE"?"UNAVAILABLE":rpc.status==="NOT_CONFIGURED"?"NOT CONFIGURED":"UNKNOWN");const wallets=d.sources?.watched_wallets||{};set("flow-source-badge",wallets.status==="COLLECTED"?"RECENT WALLET HISTORY · COUNTS ONLY":wallets.status==="UNAVAILABLE"?"WALLET RPC UNAVAILABLE":"REAL BUY/SELL FLOW PENDING");set("tracked-wallets",wallets.status==="COLLECTED"?(wallets.collected_count+" / "+wallets.configured_count+" HISTORY READ"):wallets.status==="UNAVAILABLE"?"RPC / HISTORY ERROR":"NOT CONFIGURED");set("wallet-direction-counts",typeof o.tracked_wallet_buyers==="number"&&typeof o.tracked_wallet_sellers==="number"?(o.tracked_wallet_buyers+" / "+o.tracked_wallet_sellers):"— / —");const sigs=Array.isArray(o.onchain_signatures)?o.onchain_signatures.filter(s=>typeof s==="string"&&/^[1-9A-HJ-NP-Za-km-z]{32,100}$/.test(s)).slice(0,5):[];const evidence=$("onchain-evidence");evidence.innerHTML=sigs.length?'<div class="row"><span>VERIFIABLE TRANSACTION SIGNATURES</span><b>'+sigs.length+' FOUND</b></div>'+sigs.map(s=>'<div class="row"><span>'+esc(s.slice(0,8)+'…'+s.slice(-6))+'</span><a class="green" target="_blank" rel="noopener noreferrer" href="https://explorer.solana.com/tx/'+encodeURIComponent(s)+'?cluster=mainnet-beta">OPEN EXPLORER ↗</a></div>').join(""):'<div class="row"><span>TRANSACTION EVIDENCE</span><b>'+(wallets.status==="COLLECTED"?"NO MATCHING SWAPS IN RECENT HISTORY":"WAITING FOR WATCHED WALLET DATA")+'</b></div>';set("smart",wallets.status==="COLLECTED"?"WALLET ACTIVITY OBSERVED · NOT RANKED":wallets.status==="UNAVAILABLE"?"WALLET DATA UNAVAILABLE":"NOT EVALUATED");set("hero-token",o.symbol||o.token||"WAITING FOR MARKET");set("hero-reason",o.reason||d.error||"Real market snapshot received.");if(!window.__lastChartToken||window.__lastChartToken!==o.token){window.__lastChartToken=o.token;loadCandles(true)}set("hero-decision",o.decision||"WAIT");set("hero-evidence",o.evidence_status||"RADAR ONLY");set("hero-score",num(o.edge_score,2));set("score-state",o.edge_score!=null?"EVIDENCE SCORE":"WAITING FOR EVIDENCE");set("hero-mc",money(o.market_cap_usd));set("hero-liq",money(o.liquidity_usd));set("hero-v5m",money(o.volume_5m_usd));set("hero-v1h",money(o.volume_1h_usd));set("mission-capital",d.mission?.capital!=null?money(d.mission.capital):"NOT SET");set("hero-tx",num(o.txns_per_minute));set("v5m",money(o.volume_5m_usd));set("v1h",money(o.volume_1h_usd));set("txns",num(o.txns_per_minute));set("buy-value",typeof o.onchain_buy_txns==="number"?String(o.onchain_buy_txns):"—");set("sell-value",typeof o.onchain_sell_txns==="number"?String(o.onchain_sell_txns):"—");set("buy-sell-ratio",typeof o.onchain_buy_txns==="number"&&typeof o.onchain_sell_txns==="number"?(o.onchain_sell_txns===0?(o.onchain_buy_txns>0?"∞":"—"):(o.onchain_buy_txns/o.onchain_sell_txns).toFixed(2)+"x"):"—");set("edge-score",num(o.edge_score,2));set("edge-status",o.edge_decision||"WAIT");set("edge-flow",o.flow_score??"—");set("edge-wallet",o.wallet_support??"—");set("edge-narrative",o.narrative_score??"—");set("edge-dev",o.dev_risk_score??"—");["edge-flow-bar","edge-wallet-bar","edge-narrative-bar"].forEach((id,i)=>$(id).style.setProperty("--w",pct([o.flow_score,o.wallet_support,o.narrative_score][i])+"%"));if(typeof o.dev_risk_score==="number")$("edge-dev-bar").style.setProperty("--w",pct(1-o.dev_risk_score)+"%");set("decision",o.decision||"WAIT");set("decision-reason",o.reason||"Full evidence pipeline required.");const vetoFields=[["veto-liquidity","liquidity_check_status"],["veto-honeypot","honeypot_status"],["veto-freeze","freeze_authority_status"],["veto-sync","synchronized_sell_status"],["veto-evidence","evidence_quality_status"],["veto-position","position_risk_status"]];for(const [id,field] of vetoFields){const value=o[field];set(id,typeof value==="string"&&value.trim()?value:"NOT EVALUATED");}const evidenceVeto=$("veto-evidence");if(evidenceVeto&&!o.evidence_quality_status)evidenceVeto.textContent="INSUFFICIENT EVIDENCE";const missionCapital=d.mission?.capital;const missionProgress=$("mission-progress");if(missionProgress){const progress=typeof missionCapital==="number"&&typeof d.mission?.target_capital==="number"&&d.mission.target_capital>0?Math.max(0,Math.min(100,missionCapital/d.mission.target_capital*100)):null;missionProgress.style.width=(progress===null?0:progress)+"%";}const decisionKey=String(o.decision||"WAIT").replaceAll("_"," ").replace("🟡 ","");document.querySelectorAll(".decision-grid div").forEach(el=>el.classList.toggle("active",el.textContent.trim()===decisionKey));set("smart",o.smart_money_status||"NOT EVALUATED");set("independent",o.independent_clusters??"—");set("cluster-count",o.cluster_count??"—");set("smart-count",o.smart_money_count??"—");set("wallet-reliability",o.wallet_reliability??"—");set("dev",o.dev_status||"NOT EVALUATED");set("cluster",o.cluster_status||"NOT EVALUATED");set("coordination",o.coordination_status||"NOT EVALUATED");set("manip",o.manipulation_status||"NOT EVALUATED");set("devsell",o.dev_sell_risk??"—");set("threat-score",o.manipulation_score!=null?num(o.manipulation_score,2):"—");set("liquidity",money(o.liquidity_usd));set("exit",o.exitability||"NOT EVALUATED");set("exit-badge",o.exitability||"NOT EVALUATED");set("price-impact",o.price_impact_pct!=null?num(o.price_impact_pct,2)+"%":"—");set("slippage",o.slippage_bps!=null?num(o.slippage_bps,0)+" bps":"—");const list=Array.isArray(d.opportunities)?d.opportunities:[];
$("opportunities").innerHTML=list.length?list.slice(0,10).map(x=>'<div class="token-card"><div style="display:flex;justify-content:space-between;gap:5px"><b>'+esc(x.symbol||x.token||"UNKNOWN")+'</b><b class="amber">'+esc(x.decision||"WAIT")+'</b></div><div class="candidate-visual" aria-label="Animated scanner visual only, not market-price data"><svg viewBox="0 0 220 32" preserveAspectRatio="none" aria-hidden="true"><path class="wave-secondary" d="M0 17 L14 17 L21 13 L29 22 L38 17 L52 17 L61 8 L70 23 L82 17 L96 17 L105 12 L113 19 L126 17 L140 17 L149 5 L158 25 L169 17 L184 17 L193 12 L202 19 L220 17"/><path class="wave" d="M0 19 L12 19 L19 14 L26 23 L35 19 L48 19 L57 10 L65 24 L77 19 L91 19 L100 14 L109 21 L120 19 L135 19 L144 7 L153 26 L165 19 L179 19 L188 13 L198 21 L209 19 L220 19"/></svg><span class="scan-state">SCANNING</span><small>ANIMATED RADAR VISUAL · NOT PRICE DATA</small><div class="scan-bars" aria-hidden="true"><i style="--bar-height:10px"></i><i style="--bar-height:23px"></i><i style="--bar-height:15px"></i><i style="--bar-height:27px"></i><i style="--bar-height:12px"></i><i style="--bar-height:20px"></i><i style="--bar-height:8px"></i></div></div><small>'+esc(x.name||"Solana candidate")+'</small><small>MC '+money(x.market_cap_usd)+' · LIQ '+money(x.liquidity_usd)+'</small><small>VOL 5M '+money(x.volume_5m_usd)+' · VOL 1H '+money(x.volume_1h_usd)+'</small><small>BUY/SELL 5M '+(x.buy_txns_5m??"—")+'/'+(x.sell_txns_5m??"—")+' · PAIR AGE '+(typeof x.age_seconds==="number"?(x.age_seconds/60).toFixed(1)+"m":"—")+'</small><small>EVIDENCE '+esc(x.evidence_status||"RADAR_ONLY")+'</small><small>RADAR '+esc(x.radar_eligibility||"NOT EVALUATED")+'</small><small>FILTER REASONS '+esc((Array.isArray(x.radar_filter_reasons)?x.radar_filter_reasons:[]).join(" · ")||"NONE")+'</small></div>').join(""):'<div class="token-card"><b>NO LIVE CANDIDATES RETURNED</b><div class="candidate-visual" aria-label="Animated scanner visual only, not market-price data"><svg viewBox="0 0 220 32" preserveAspectRatio="none" aria-hidden="true"><path class="wave-secondary" d="M0 17 L14 17 L21 13 L29 22 L38 17 L52 17 L61 8 L70 23 L82 17 L96 17 L105 12 L113 19 L126 17 L140 17 L149 5 L158 25 L169 17 L184 17 L193 12 L202 19 L220 17"/><path class="wave" d="M0 19 L12 19 L19 14 L26 23 L35 19 L48 19 L57 10 L65 24 L77 19 L91 19 L100 14 L109 21 L120 19 L135 19 L144 7 L153 26 L165 19 L179 19 L188 13 L198 21 L209 19 L220 19"/></svg><span class="scan-state">SCANNING</span><small>ANIMATED RADAR VISUAL · NOT PRICE DATA</small><div class="scan-bars" aria-hidden="true"><i style="--bar-height:10px"></i><i style="--bar-height:23px"></i><i style="--bar-height:15px"></i><i style="--bar-height:27px"></i><i style="--bar-height:12px"></i><i style="--bar-height:20px"></i><i style="--bar-height:8px"></i></div></div><small>DEX is reachable, but discovery returned no matching Solana token pairs. No synthetic candidates are shown.</small><small>DISCOVERED '+esc(d.discovery?.discovered_candidate_count??0)+' · QUALIFYING '+esc(d.discovery?.qualifying_candidate_count??0)+'</small><small>Refresh later or inspect the live DEX discovery response.</small></div>';const selector=$("price-token-select");if(selector){const previous=window.__selectedToken||selector.value;selector.innerHTML=list.map(item=>'<option value="'+esc(item.token)+'">'+esc(item.symbol||item.name||item.token)+' · '+esc((item.token||"").slice(0,5))+'…</option>').join("");if(list.some(item=>item.token===previous)){selector.value=previous;window.__selectedToken=previous}else{window.__selectedToken=list[0]?.token||"";selector.value=window.__selectedToken}if(!selector.dataset.bound){selector.addEventListener("change",()=>{window.__selectedToken=selector.value;loadCandles(true)});selector.dataset.bound="1"}}
}
async function refresh(){try{const r=await fetch("/snapshot?ui=28&t="+Date.now(),{cache:"no-store"});if(!r.ok)throw Error(r.status);render(await r.json())}catch(e){set("connection","DEX: SNAPSHOT UNAVAILABLE");set("rpc-connection","RPC: UNKNOWN");set("hero-reason","Backend snapshot belum tersedia. Tidak ada data market palsu.");}}
$("refresh").onclick=refresh;
/* UI27 workspace router: each destination gets its own page and context. */
(function initWorkspace(){
 const host=document.createElement("main");host.id="workspace-pages";
 const shell=document.querySelector("#app");
 const header=shell.querySelector("header");
 const oldGrid=shell.querySelector(".grid");
 const hero=shell.querySelector(".command-hero");
 const price=document.getElementById("price-terminal");
 const radar=document.getElementById("radar-section");
 const edge=document.getElementById("edge-section");
 const flow=document.getElementById("flow-section");
 const wallets=document.getElementById("wallets-section");
 const risk=document.getElementById("risk-section");
 const matrix=document.getElementById("roadmap-matrix");
 const mission=document.getElementById("mission-section");
 const devSection=Array.from(oldGrid.querySelectorAll("section")).find(s=>/DEV DNA & MANIPULATION/.test(s.innerText||""));
 const exitSection=Array.from(oldGrid.querySelectorAll("section")).find(s=>s!==radar&&s!==edge&&s!==flow&&s!==wallets&&s!==risk&&s!==devSection&&/EXITABILITY|LIQUIDITY LADDER/.test(s.innerText||""));
 const footer=shell.querySelector(".footer-note");
 const makePage=(key,title,subtitle,tag)=>{
  const p=document.createElement("section");p.className="workspace-page";p.id="page-"+key;p.dataset.page=key;
  const heading=document.createElement("div");heading.className="page-heading";
  heading.innerHTML='<div><div class="eyebrow">MEMECOIN HUNTER / WORKSPACE</div><h2>'+title+'</h2><p>'+subtitle+'</p></div><span class="page-tag">'+tag+'</span>';
  p.appendChild(heading);host.appendChild(p);return p;
 };
 const page={
  radar:makePage("radar","Market Radar","Discovery ringkas untuk menemukan kandidat; keputusan tetap menunggu bukti yang cukup.","01 / DISCOVERY"),
  tokens:makePage("tokens","Token Terminal","Pilih kandidat dan periksa OHLCV nyata dari pool yang terverifikasi. Tidak ada candle buatan.","02 / MARKET DATA"),
  flow:makePage("flow","On-chain Flow","Riwayat transaksi dan arus wallet yang benar-benar teramati; hitungan bukan volume uang.","03 / FLOW"),
  wallets:makePage("wallets","Wallet Intelligence","Smart Money, wallet terpantau, cluster, dan relasi hanya jika evidence tersedia.","04 / WALLET GRAPH"),
  more:makePage("more","Intelligence Workspaces","Masuk ke ruang analisis khusus. Setiap modul memiliki halaman terpisah.","WORKSPACES")
 };
 const edgePage=makePage("edge","Edge Analysis","Komponen penilaian peluang dan kualitas evidence; bukan jaminan profit.","05 / EDGE");
 const riskPage=makePage("risk","Risk Control","Veto risiko, proteksi, dan exitability. Live execution tetap terkunci.","06 / RISK");
 const capitalPage=makePage("capital","Capital & Validation","Paper trading, jurnal, misi modal, dan validasi strategi. Hasil belum boleh diasumsikan.","07 / CAPITAL");
 const systemsPage=makePage("systems","Research Modules","Cakupan roadmap dan status riset. Kartu ini bukan klaim bahwa engine sudah aktif.","08 / ROADMAP");
 shell.insertBefore(host,footer);
 if(hero)page.radar.appendChild(hero);if(radar)page.radar.appendChild(radar);
 if(price)page.tokens.appendChild(price);
 const flowWrap=document.createElement("div");flowWrap.className="grid";if(flow){flowWrap.appendChild(flow);page.flow.appendChild(flowWrap);}
 const edgeWrap=document.createElement("div");edgeWrap.className="grid";if(edge){edgeWrap.appendChild(edge);edgePage.appendChild(edgeWrap);}
 const walletWrap=document.createElement("div");walletWrap.className="grid";if(wallets){walletWrap.appendChild(wallets);page.wallets.appendChild(walletWrap);}
 const riskWrap=document.createElement("div");riskWrap.className="grid";if(risk){riskWrap.appendChild(risk);riskPage.appendChild(riskWrap);}
 if(exitSection){const ew=document.createElement("div");ew.className="grid";ew.appendChild(exitSection);riskPage.appendChild(ew);}
 if(mission)capitalPage.appendChild(mission);
 if(matrix)systemsPage.appendChild(matrix);
 if(devSection)systemsPage.appendChild(devSection);
 const links=[
  ["EDGE ANALYSIS","Asymmetric Edge, flow/wallet/narrative components.","↗","edge"],
  ["RISK CONTROL","Risk veto, liquidity, exitability and protection.","⛨","risk"],
  ["CAPITAL & VALIDATION","Paper journal, capital mission and validation gate.","◈","capital"],
  ["RESEARCH MODULES","Roadmap coverage and evidence status.","⌘","systems"]
 ];
 const moreGrid=document.createElement("div");moreGrid.className="more-grid";
 links.forEach(([title,desc,icon,key])=>{const b=document.createElement("button");b.type="button";b.className="more-link";b.innerHTML='<span class="more-icon">'+icon+'</span><b>'+title+'</b><small>'+desc+'</small>';b.addEventListener("click",()=>go(key));moreGrid.appendChild(b)});
 page.more.appendChild(moreGrid);
 // The old flat grid is emptied only after all existing modules are safely relocated.
 if(oldGrid){Array.from(oldGrid.children).forEach(node=>{if(node!==devSection&&node!==exitSection)node.remove()});if(oldGrid.children.length===0)oldGrid.remove();}
 const nav=document.getElementById("workspace-nav");
 function go(key){
  const target=document.getElementById("page-"+key);if(!target)return;
  document.querySelectorAll(".workspace-page").forEach(p=>p.classList.toggle("is-active",p===target));
  nav.querySelectorAll("button[data-page]").forEach(b=>b.classList.toggle("active",b.dataset.page===key || (key!=="radar"&&key!=="tokens"&&key!=="flow"&&key!=="wallets"&&b.dataset.page==="more")));
  const crumb=document.getElementById("page-breadcrumb");if(crumb)crumb.textContent=target.querySelector("h2")?.textContent?.toUpperCase()||key.toUpperCase();
  history.replaceState(null,"","#"+key);
  window.scrollTo({top:0,behavior:"smooth"});
  if(key==="tokens"&&typeof drawCandles==="function")setTimeout(()=>window.dispatchEvent(new Event("resize")),60);
 }
 nav.querySelectorAll("button[data-page]").forEach(b=>b.addEventListener("click",()=>go(b.dataset.page)));
 window.addEventListener("hashchange",()=>{const key=location.hash.slice(1);if(document.getElementById("page-"+key))go(key)});
 const initial=location.hash.slice(1);go(document.getElementById("page-"+initial)?initial:"radar");
 window.__mhNavigate=go;
})();
let tick=0;function loop(t){radar(t);chart(t);network(t);requestAnimationFrame(loop)}requestAnimationFrame(loop);refresh();setInterval(refresh,12000);setInterval(()=>loadCandles(true),30000);window.onresize=()=>{drawCandles()};
