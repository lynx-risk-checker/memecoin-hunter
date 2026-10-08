const CACHE_NAME="memecoin-hunter-v9";
const APP_SHELL=["/","/index.html?v=ui9","/styles.css?v=ui9","/app.js?v=ui9","/manifest.webmanifest?v=ui9"];

self.addEventListener("install",event=>{
  event.waitUntil(caches.open(CACHE_NAME).then(cache=>cache.addAll(APP_SHELL)).then(()=>self.skipWaiting()));
});

self.addEventListener("activate",event=>{
  event.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(key=>key!==CACHE_NAME).map(key=>caches.delete(key)))).then(()=>self.clients.claim()));
});

self.addEventListener("fetch",event=>{
  if(event.request.method!=="GET")return;
  const url=new URL(event.request.url);
  if(url.pathname==="/snapshot")return;
  if(url.pathname==="/sw.js"){
    event.respondWith(fetch(event.request,{cache:"no-store"}));
    return;
  }
  const appPath=["/","/index.html","/styles.css","/app.js","/manifest.webmanifest"].includes(url.pathname);
  if(appPath){
    event.respondWith(fetch(event.request,{cache:"no-store"}).then(r=>{
      const copy=r.clone();
      caches.open(CACHE_NAME).then(c=>c.put(event.request,copy));
      return r;
    }).catch(()=>caches.match(event.request)));
    return;
  }
  event.respondWith(caches.match(event.request).then(c=>c||fetch(event.request)));
});