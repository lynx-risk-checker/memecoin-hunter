const $=id=>document.getElementById(id);
const esc=v=>String(v??"—").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[c]));
const money=v=>typeof v==="number"?new Intl.NumberFormat("id-ID",{style:"currency",currency:"USD",maximumFractionDigits:0}).format(v):"—";
const num=(v,d=1)=>typeof v==="number"?v.toFixed(d):"—";
let lastData=null, pulse=0, events=0;

function decisionClass(v){const s=String(v||"");return s.includes("BUY")&&!s.includes("BLOCK")?"buy":s.includes("BLOCK")||s.includes("REJECT")?"blocked":"watch"}
function setText(id,v){const e=$(id);if(e)e.textContent=v}
function bar(id,v){const e=$(id);if(!e)return;e.style.setProperty("--w",typeof v==="number"?Math.max(0,Math.min(1,v))*100+"%":"0%")}
function resizeCanvas(c){const r=c.getBoundingClientRect(),d=Math.min(devicePixelRatio||1,3),w=Math.max(1,Math.floor(r.width*d)),h=Math.max(1,Math.floor(r.height*d));if(c.width!==w||c.height!==h){c.width=w;c.height=h}return[c.getContext("2d"),w/d,h/d,d]}
function glowText(ctx,text,x,y,size,color,align="center"){ctx.save();ctx.font=`800 ${size}px ui-monospace,SFMono-Regular,Menlo,monospace`;ctx.textAlign=align;ctx.shadowBlur=18;ctx.shadowColor=color;ctx.fillStyle=color;ctx.fillText(text,x,y);ctx.restore()}
function drawRadar(t){
 const c=$("radar-canvas");if(!c)return;const[ctx,w,h,d]=resizeCanvas(c);ctx.clearRect(0,0,c.width,c.height);ctx.save();ctx.scale(d,d);
 const cx=w/2,cy=h/2,r=Math.min(w,h)*.43,scan=(t*.00055)%(Math.PI*2);
 for(let i=1;i<=5;i++){ctx.beginPath();ctx.arc(cx,cy,r*i/5,0,Math.PI*2);ctx.strokeStyle=`rgba(72,231,160,${.06+i*.012})`;ctx.lineWidth=1;ctx.stroke()}
 for(let i=0;i<12;i++){const a=i*Math.PI/6;ctx.beginPath();ctx.moveTo(cx,cy);ctx.lineTo(cx+Math.cos(a)*r,cy+Math.sin(a)*r);ctx.strokeStyle="rgba(82,126,160,.10)";ctx.stroke()}
 const beam=ctx.createRadialGradient(cx,cy,0,cx,cy,r);beam.addColorStop(0,"rgba(65,235,167,.18)");beam.addColorStop(.7,"rgba(65,235,167,.05)");beam.addColorStop(1,"rgba(65,235,167,0)");ctx.fillStyle=beam;ctx.fillRect(0,0,w,h);
 ctx.save();ctx.translate(cx,cy);ctx.rotate(scan);ctx.beginPath();ctx.moveTo(0,0);ctx.lineTo(r,0);ctx.lineTo(r,Math.PI/18*r);ctx.closePath();ctx.fillStyle="rgba(70,240,170,.12)";ctx.fill();ctx.restore();
 ctx.beginPath();ctx.arc(cx,cy,8+2*Math.sin(t/350),0,Math.PI*2);ctx.fillStyle="#9affd4";ctx.shadowBlur=24;ctx.shadowColor="#4fe6a0";ctx.fill();ctx.restore()
}
function drawFlow(t){
 const c=$("flow-canvas");if(!c)return;const[ctx,w,h,d]=resizeCanvas(c);ctx.clearRect(0,0,c.width,c.height);ctx.save();ctx.scale(d,d);
 for(let y=0;y<5;y++){ctx.beginPath();ctx.moveTo(0,y*h/4);ctx.lineTo(w,y*h/4);ctx.strokeStyle="rgba(95,117,143,.10)";ctx.stroke()}
 for(let x=0;x<7;x++){ctx.beginPath();ctx.moveTo(x*w/6,0);ctx.lineTo(x*w/6,h);ctx.strokeStyle="rgba(95,117,143,.06)";ctx.stroke()}
 const o=lastData?.opportunities?.[0]||lastData||{},buy=typeof o.buy_txns_5m==="number"?o.buy_txns_5m:null,sell=typeof o.sell_txns_5m==="number"?o.sell_txns_5m:null,total=(buy||0)+(sell||0);
 if(total>0){const by=buy/total,sy=sell/total;ctx.fillStyle="rgba(70,231,160,.16)";ctx.fillRect(12,h-34,(w-24)*by,12);ctx.fillStyle="rgba(239,100,123,.14)";ctx.fillRect(12,h-18,(w-24)*sy,8);ctx.fillStyle="#718298";ctx.font="700 8px ui-monospace";ctx.fillText("DEXSCREENER 5M BUY / SELL TXNS",12,12)}
 const sx=((t*.00008)%1)*w;ctx.fillStyle="rgba(76,232,164,.16)";ctx.fillRect(sx,0,1,h);ctx.shadowBlur=18;ctx.shadowColor="#52e7a0";ctx.fillStyle="#52e7a0";ctx.fillRect(sx,0,1,h);ctx.shadowBlur=0;
 if(!lastData){glowText(ctx,"WAITING FOR REAL FLOW SERIES",w/2,h/2,8,"#64748b")}
 else if(typeof o.buy_txns_5m!=="number"&&typeof o.sell_txns_5m!=="number"){glowText(ctx,"BUY / SELL COUNTS UNAVAILABLE",w/2,h/2,9,"#64748b")}
 ctx.restore()
}
function drawNetwork(t){
 const c=$("network-canvas");if(!c)return;const[ctx,w,h,d]=resizeCanvas(c);ctx.clearRect(0,0,c.width,c.height);ctx.save();ctx.scale(d,d);
 const evidence=lastData?.opportunities?.[0]||lastData||{},ind=Number(evidence.independent_clusters||0),count=Number(evidence.smart_money_count||0);
 for(let i=0;i<9;i++){const y=(i+1)*h/10;ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(w,y);ctx.strokeStyle="rgba(72,105,135,.06)";ctx.stroke()}
 for(let i=0;i<11;i++){const x=(i+1)*w/12;ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,h);ctx.strokeStyle="rgba(72,105,135,.05)";ctx.stroke()}
 const scan=(t*.00007)%1*w;ctx.fillStyle="rgba(72,231,160,.10)";ctx.fillRect(scan,0,1,h);
 if(ind>0||count>0){
   const n=Math.min(18,Math.max(ind,count,2)),nodes=[];
   for(let i=0;i<n;i++){const a=i/n*Math.PI*2+t*.000025*(i%2?1:-1),rad=Math.min(w,h)*(.18+.035*(i%4));nodes.push({x:w/2+Math.cos(a)*rad,y:h/2+Math.sin(a)*rad,r:i%4===0?5:3})}
   nodes.forEach((a,i)=>nodes.slice(i+1).filter((_,j)=>(i+j)%5===0).forEach(b=>{ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);ctx.strokeStyle="rgba(76,231,160,.16)";ctx.stroke()}));
   nodes.forEach((n,i)=>{ctx.beginPath();ctx.arc(n.x,n.y,n.r+2*Math.sin(t/450+i),0,Math.PI*2);ctx.fillStyle=i===0?"#b2ffe0":"#69a7bb";ctx.shadowBlur=14;ctx.shadowColor="#4fe6a0";ctx.fill()});
 }else{glowText(ctx,"ON-CHAIN WALLET EVIDENCE PENDING",w/2,h/2,8,"#5e6e82")}
 ctx.restore()
}
function drawThreat(t){
 const c=$("threat-canvas");if(!c)return;const[ctx,w,h,d]=resizeCanvas(c);ctx.clearRect(0,0,c.width,c.height);ctx.save();ctx.scale(d,d);const cx=w/2,cy=h/2,r=Math.min(w,h)*.38;
 for(let i=1;i<=5;i++){ctx.beginPath();ctx.arc(cx,cy,r*i/5,0,Math.PI*2);ctx.strokeStyle="rgba(180,105,125,.10)";ctx.stroke()}
 const a=(t*.00045)%(Math.PI*2);ctx.save();ctx.translate(cx,cy);ctx.rotate(a);ctx.beginPath();ctx.moveTo(0,0);ctx.lineTo(r,0);ctx.strokeStyle="rgba(239,100,123,.55)";ctx.shadowBlur=18;ctx.shadowColor="#ef647b";ctx.stroke();ctx.restore();
 const score=Number((lastData?.opportunities?.[0]||lastData||{}).manipulation_score);if(Number.isFinite(score))glowText(ctx,score.toFixed(2),cx,cy+5,24,score>=.7?"#ef647b":"#f0c55d");
 ctx.restore()
}
function render(items){$("opportunities").innerHTML=items.map(x=>{const d=x.decision||"🟡 WATCH";return `<article class="radar"><div class="radar-top"><div><div class="token">${esc(x.symbol||x.token||"UNKNOWN")}</div><span class="muted">${esc(x.name||"Token candidate")}</span></div><strong class="decision ${decisionClass(d)}">${esc(d)}</strong></div><p class="muted">${esc(x.reason||"Evidence pipeline awaiting evaluation.")}</p><div class="radar-meta"><div><span>MC</span><b>${money(x.market_cap_usd)}</b></div><div><span>LIQ</span><b>${money(x.liquidity_usd)}</b></div><div><span>AGE</span><b>${typeof x.age_seconds==="number"?(x.age_seconds/60).toFixed(1)+"m":"—"}</b></div><div><span>VOL 5M</span><b>${money(x.volume_5m_usd)}</b></div><div><span>TX/MIN</span><b>${typeof x.txns_per_minute==="number"?x.txns_per_minute.toFixed(1):"—"}</b></div><div><span>EVIDENCE</span><b>${esc(x.evidence_status||"RADAR ONLY")}</b></div></div></article>`}).join("")}
function setSnapshot(d){
 lastData=d;events++;setText("audit-count",events);const o=(d.opportunities&&d.opportunities[0])||d,decision=o.decision||"🟡 WATCH";
 setText("connection","● MARKET DATA CONNECTED");setText("hero-token",o.symbol||o.token||"WAITING FOR MARKET");setText("hero-reason",o.reason||"Scanning real Solana market data. No synthetic signals.");
 setText("hero-decision",decision.replace(/^.*?(BUY ALLOWED|BUY BLOCKED|WATCH|WAIT|REJECT).*$/,"$1"));setText("hero-evidence",o.evidence_status||"RADAR ONLY");setText("hero-score",num(o.edge_score,2));setText("core-score",num(o.edge_score,2));setText("score-state",o.edge_score!=null?"EVIDENCE SCORE":"WAITING FOR EVIDENCE");
 setText("hero-mc",money(o.market_cap_usd));setText("hero-liq",money(o.liquidity_usd));setText("hero-v5m",money(o.volume_5m_usd));setText("hero-tx",num(o.txns_per_minute));setText("v5m",money(o.volume_5m_usd));setText("v1h",money(o.volume_1h_usd));setText("txns",num(o.txns_per_minute));
 const buy=o.buy_txns_5m,sell=o.sell_txns_5m;setText("buy-value",typeof buy==="number"?String(buy):"—");setText("sell-value",typeof sell==="number"?String(sell):"—");setText("buy-sell-ratio",typeof buy==="number"&&typeof sell==="number"?(sell===0?(buy>0?"∞":"—"):(buy/sell).toFixed(2)+"x"):"—");setText("flow-title",o.evidence_status||"Radar snapshot");setText("velocity-value",o.txns_per_minute!=null?num(o.txns_per_minute):"—");
 bar("v5m-bar",o.volume_5m_usd!=null?Math.min(1,o.volume_5m_usd/100000):null);bar("v1h-bar",o.volume_1h_usd!=null?Math.min(1,o.volume_1h_usd/1000000):null);bar("ratio-bar",typeof buy==="number"&&typeof sell==="number"?Math.min(1,buy/(buy+sell||1)):null);
 setText("buyers",o.buyers??"—");setText("sellers",o.sellers??"—");setText("unique-wallets",o.unique_wallets??"—");setText("smart",o.smart_money_status||"NOT EVALUATED");setText("smart-detail",o.smart_money_status||"NOT EVALUATED");setText("dev",o.dev_status||"NOT EVALUATED");setText("cluster",o.cluster_status||"NOT EVALUATED");setText("coordination",o.coordination_status||"NOT EVALUATED");setText("coordination2",o.coordination_status||"NOT EVALUATED");
 setText("independent",o.independent_clusters??"—");setText("cluster-count",o.cluster_count??o.independent_clusters??"—");setText("smart-count",o.smart_money_count??"—");setText("wallet-reliability",o.wallet_reliability??"—");setText("manip",o.manipulation_status||"NOT EVALUATED");setText("liquidity",money(o.liquidity_usd));setText("exit",o.exitability||"NOT EVALUATED");setText("devsell",o.dev_sell_risk??"—");setText("exit-badge",o.exitability||"NOT EVALUATED");setText("threat-score",o.manipulation_score!=null?num(o.manipulation_score,2):"—");
 setText("price-impact",o.price_impact_pct!=null?num(o.price_impact_pct,2)+"%":"—");setText("slippage",o.slippage_bps!=null?num(o.slippage_bps,0)+" bps":"—");setText("position-size",o.position_usd!=null?money(o.position_usd):"—");
 setText("edge-status",o.edge_decision||"WAIT");setText("edge-score",num(o.edge_score,2));setText("edge-verdict",o.edge_decision||"WAIT FOR EVIDENCE");setText("edge-reason",o.edge_reason||"Every trade must pass evidence + risk veto.");
 setText("edge-flow",o.flow_score??"—");setText("edge-wallet",o.wallet_support??"—");setText("edge-narrative",o.narrative_score??"—");setText("edge-dev",o.dev_risk_score??"—");bar("edge-flow-bar",o.flow_score);bar("edge-wallet-bar",o.wallet_support);bar("edge-narrative-bar",o.narrative_score);bar("edge-dev-bar",typeof o.dev_risk_score==="number"?1-o.dev_risk_score:null);
 setText("ev",o.expected_value??"—");setText("decision",decision);$("decision").className="big-decision "+decisionClass(decision);setText("decision-reason",o.reason||"Full evidence pipeline required.");setText("evidence",d.validation_status?"Validation: "+d.validation_status+" • "+(o.evidence_status||"RADAR_ONLY"):"Real snapshot received; field-level evidence depends on backend payload.");
 $("raw").textContent=JSON.stringify(d,null,2);render(d.opportunities||[o]);
}
async function refresh(){try{const r=await fetch("/snapshot?ui=5&t="+Date.now(),{cache:"no-store"});if(!r.ok)throw new Error("HTTP "+r.status);setSnapshot(await r.json())}catch(e){setText("connection","● SNAPSHOT UNAVAILABLE");setText("hero-token","WAITING FOR MARKET");setText("hero-reason","Backend belum tersedia. UI tidak mengarang market data.");render([{symbol:"WAITING",decision:"🟡 WATCH",reason:"Backend snapshot belum tersedia."}])}}
function animate(t){pulse=t;drawRadar(t);drawFlow(t);drawNetwork(t);drawThreat(t);requestAnimationFrame(animate)}
$("refresh").addEventListener("click",refresh);$("toggle-raw").addEventListener("click",()=>{$("raw").hidden=!$("raw").hidden});requestAnimationFrame(animate);refresh();setInterval(refresh,12000);window.addEventListener("resize",()=>{const t=performance.now();drawRadar(t);drawFlow(t);drawNetwork(t);drawThreat(t)});
