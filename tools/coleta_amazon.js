// Roda em segundo plano. Depois leia o resultado com: window.__COLETA (null enquanto roda).
// Rodar numa aba aberta em https://www.amazon.com.br (javascript_tool).
// Substitua IDS pela lista [indice, "ASIN"] gerada por: python3 tools/atualiza.py ids am
const IDS = __IDS__;
const num = s => s ? parseFloat(s.replace(/[^\d,]/g,'').replace(',','.')) : null;
window.__COLETA = null;
(async () => {
const out = [];
for (const [i, a] of IDS) {
  try {
    const h = await (await fetch('/dp/' + a, {credentials: 'include'})).text();
    const d = new DOMParser().parseFromString(h, 'text/html');
    const q = s => ((d.querySelector(s) || {}).textContent || '').trim();
    const p = num(q('#corePrice_feature_div .a-price:not(.a-text-price) .a-offscreen') || q('.priceToPay .a-offscreen') || q('#corePriceDisplay_desktop_feature_div .a-offscreen'));
    const o = num(q('.basisPrice .a-offscreen') || q('#corePriceDisplay_desktop_feature_div .a-text-price .a-offscreen'));
    const off = /indispon|não disponível/i.test(q('#availability'));
    out.push([i, off ? null : p, o]);
  } catch (e) { out.push([i, null, null]); }
  await new Promise(r => setTimeout(r, 600));
}
window.__COLETA = JSON.stringify(out);
})();
'iniciado: consulte window.__COLETA em ~1 minuto';
