"""Atualiza os precos do Placar do Desconto.

Uso:
  python3 tools/atualiza.py ids ml|am      -> imprime a lista [indice, id] para colar no coletor
  python3 tools/atualiza.py aplica ml ARQ  -> aplica o resultado do coletor (JSON [[i, preco, de], ...])
  python3 tools/atualiza.py fecha AAAA-MM-DD -> grava a data e gera o resumo

O catalogo completo fica em tools/catalogo.json (todos os links, mesmo de ofertas fora do ar).
O site le data.json, que so traz ofertas com preco valido na ultima coleta.
"""
import json, sys, os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAT = os.path.join(BASE, 'tools', 'catalogo.json')
SITE = os.path.join(BASE, 'data.json')
KEY = {'ml': 'mlb', 'am': 'asin'}

def load(p): return json.load(open(p, encoding='utf-8'))
def save(p, d): json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

def publica(cat):
    site = json.loads(json.dumps(cat))
    for it in site['items']:
        it['offers'] = {k: v for k, v in it['offers'].items() if v.get('ok', True) and v.get('price')}
    save(SITE, site)

cmd = sys.argv[1]
cat = load(CAT)
if cmd == 'ids':
    st = sys.argv[2]
    print(json.dumps([[i, it['offers'][st][KEY[st]]] for i, it in enumerate(cat['items']) if st in it['offers']]))
elif cmd == 'aplica':
    st, arq = sys.argv[2], sys.argv[3]
    res = json.load(open(arq))
    log = []
    for i, p, o in res:
        off = cat['items'][i]['offers'][st]
        nome = cat['items'][i]['name'][:45]
        if not p or p < 50:
            off['ok'] = False
            log.append(f'SEM PRECO  {st} {nome}')
            continue
        p = round(p); o = round(o) if o and o > p else None
        old = off.get('price')
        if old and abs(p - old) / old > 0.35:
            # variacao grande demais: provavel erro de leitura, mantem o anterior
            off['ok'] = True
            log.append(f'IGNORADO   {st} {nome}: {old} -> {p} (variacao > 35%)')
            continue
        if old and p != old:
            log.append(f'{"CAIU  " if p < old else "SUBIU "}     {st} {nome}: {old} -> {p}')
        off.update(price=p, orig=o, ok=True)
    save(CAT, cat)
    publica(cat)
    print('\n'.join(log) or 'sem mudancas')
elif cmd == 'fecha':
    cat['updated'] = sys.argv[2]
    save(CAT, cat)
    publica(cat)
    n = sum(1 for it in cat['items'] for v in it['offers'].values() if v.get('ok', True) and v.get('price'))
    print(f'data {sys.argv[2]}: {n} ofertas no ar')
