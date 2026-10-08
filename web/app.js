const demo=[{symbol:"WAITING",decision:"🟡 WATCH",reason:"Backend snapshot belum terhubung; tidak menampilkan data palsu."}];
const $=id=>document.getElementById(id);
const money=v=>typeof v==="number"?new Intl.NumberFormat("id-ID",{style:"currency",currency:"USD",maximumFractionDigits:0}).format(v):"—";
function render(items){
  $("opportunities").innerHTML=items.map(x=>{
    const decision=x.decision||"🟡 WATCH";
    const cls=String(decision).includes("BUY")?"buy":String(decision).includes("BLOCK")?"blocked":"watch";
    return `<article class="card"><h3>${x.symbol||x.token||"UNKNOWN"}</h3><strong class="${cls}">${decision}</strong><p class="muted">${x.reason||"No decision reason supplied."}</p></article>`;
  }).join("");
}
function setSnapshot(d){
  const o=(d.opportunities&&d.opportunities[0])||d;
  $("v5m").textContent=money(o.volume_5m_usd);
  $("v1h").textContent=money(o.volume_1h_usd);
  $("txns").textContent=typeof o.txn_count_5m==="number"?(o.txn_count_5m/5).toFixed(1):"—";
  $("flow").textContent=typeof o.buy_volume_usd==="number"&&typeof o.sell_volume_usd==="number"?`${money(o.buy_volume_usd)} / ${money(o.sell_volume_usd)}`:"—";
  $("smart").textContent=o.smart_money_status||"—";
  $("dev").textContent=o.dev_status||"—";
  $("cluster").textContent=o.cluster_status||"—";
  $("exit").textContent=o.exitability??"—";
  $("manip").textContent=o.manipulation_status??"—";
  $("evidence").textContent=d.validation_status? `Validation: ${d.validation_status}`:"Snapshot received; field-level evidence depends on backend payload.";
  $("raw").textContent=JSON.stringify(d,null,2);
  render(d.opportunities||[o]);
}
async function refresh(){
  try{
    const r=await fetch("/snapshot",{cache:"no-store"});
    if(!r.ok)throw new Error("HTTP "+r.status);
    const d=await r.json();
    $("connection").textContent="● SNAPSHOT CONNECTED";
    setSnapshot(d);
  }catch(e){
    $("connection").textContent="● SNAPSHOT UNAVAILABLE";
    $("evidence").textContent="Backend belum tersedia. UI tidak mengarang market data.";
    $("raw").textContent=String(e);
    render(demo);
  }
}
$("refresh").addEventListener("click",refresh); render(demo); refresh();