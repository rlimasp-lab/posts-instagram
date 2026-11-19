// Roda em segundo plano. Depois leia o resultado com: window.__COLETA (null enquanto roda).
// Rodar numa aba aberta em https://www.mercadolivre.com.br (javascript_tool).
// Substitua IDS pela lista [indice, "MLB..."] gerada por: python3 tools/atualiza.py ids ml
const IDS = __IDS__;
const num = s => s ? parseFloat(s.replace(/\./g,'').replace(',','.')) : null;
window.__COLETA = null;
(async () => {
const out = [];
for (const [i, id] of IDS) {
  try {
    const h = await (await fetch('/p/' + id, {credentials: 'include'})).text();
    const d = new DOMParser().parseFromString(h, 'text/html');
    const q = s => ((d.querySelector(s) || {}).textContent || '').trim();
    const pr = sel => { const f = num(q(sel + ' .andes-money-amount__fraction')); const c = q(sel + ' .andes-money-amount__cents'); return f === null ? null : (c ? f + parseInt(c, 10) / 100 : f); };
    const p = pr('.ui-pdp-price__second-line');
    const o = pr('.ui-pdp-price__original-value');
    const off = /indispon|pausad|esgotad/i.test(q('.ui-pdp-stock-information, .ui-pdp-message, .ui-vpp-highlighted-specs__unavailable'));
    out.push([i, off ? null : p, o]);
  } catch (e) { out.push([i, null, null]); }
  await new Promise(r => setTimeout(r, 500));
}
window.__COLETA = JSON.stringify(out);
})();
'iniciado: consulte window.__COLETA em ~1 minuto';
