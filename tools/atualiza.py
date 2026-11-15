"""Atualiza os precos do Placar do Desconto.

Uso:
  python3 tools/atualiza.py ids ml|am      -> imprime a lista [indice, id] para colar no coletor
  python3 tools/atualiza.py aplica ml ARQ  -> aplica o resultado do coletor (JSON [[i, preco, de], ...])
  python3 tools/atualiza.py fecha AAAA-MM-DD -> grava a data e gera o resumo
  python3 tools/atualiza.py adiciona ARQ     -> inclui produtos novos (ver formato em tools/LEIA-ME.md)
  python3 tools/atualiza.py tratado "termo" "nota" -> marca um termo buscado como ja analisado
  python3 tools/atualiza.py tratados         -> lista os termos ja analisados

O catalogo completo fica em tools/catalogo.json (todos os links, mesmo de ofertas fora do ar).
O site le data.json, que so traz ofertas com preco valido na ultima coleta.
"""
import json, sys, os, re, unicodedata
TRAT = None
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAT = os.path.join(BASE, 'tools', 'catalogo.json')
SITE = os.path.join(BASE, 'data.json')
KEY = {'ml': 'mlb', 'am': 'asin'}
TRAT = os.path.join(BASE, 'tools', 'termos_tratados.json')
AMZ_TAG = 'lima0a0-20'

def slug(t):
    t = unicodedata.normalize('NFKD', t).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '-', t).strip('-')[:60]

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
elif cmd == 'adiciona':
    novo = json.load(open(sys.argv[2], encoding='utf-8'))
    for c in novo.get('categories', []):
        assert {'id', 'label', 'spec'} <= set(c), 'categoria precisa de id, label e spec'
        if not any(x['id'] == c['id'] for x in cat['categories']):
            cat['categories'].append({'id': c['id'], 'label': c['label'], 'spec': c['spec']})
            print('categoria nova:', c['label'])
    ids = {it['id'] for it in cat['items']}
    cats = {c['id'] for c in cat['categories']}
    mlbs = {it['offers'].get('ml', {}).get('mlb') for it in cat['items']}
    for it in novo.get('items', []):
        assert it['cat'] in cats, 'categoria inexistente: ' + it['cat']
        assert re.fullmatch(r'\d{6}-ML[A-Z]\d+_\d+', it['img']), 'img deve ser o codigo da foto do Mercado Livre'
        of = it['offers']
        assert of, 'produto sem oferta'
        if 'ml' in of:
            assert re.fullmatch(r'https://meli\.la/\w+', of['ml']['link']), 'link ML deve ser meli.la gerado na conta de afiliado'
            assert re.fullmatch(r'MLB\d+', of['ml']['mlb'])
            if of['ml']['mlb'] in mlbs:
                print('JA EXISTE, ignorado:', it['name']); continue
        if 'am' in of:
            assert re.fullmatch(r'[A-Z0-9]{10}', of['am']['asin'])
            of['am']['link'] = f"https://www.amazon.com.br/dp/{of['am']['asin']}?tag={AMZ_TAG}"
        for v in of.values():
            v['price'] = round(v['price']); v['orig'] = round(v['orig']) if v.get('orig') and v['orig'] > v['price'] else None; v['ok'] = True
        base = slug(it['name']); k, n = base, 2
        while k in ids: k = f'{base}-{n}'; n += 1
        ids.add(k)
        cat['items'].append({'cat': it['cat'], 'name': it['name'][:80], 'brand': it.get('brand', 'Outras'), 'spec': it.get('spec', ''), 'img': it['img'], 'offers': of, 'id': k, 'origem': it.get('origem', '')})
        print('incluido:', it['name'][:60], '| lojas:', ', '.join(of))
    save(CAT, cat)
    publica(cat)
elif cmd == 'tratado':
    t = json.load(open(TRAT, encoding='utf-8')) if os.path.exists(TRAT) else {}
    t[sys.argv[2].strip().lower()] = sys.argv[3] if len(sys.argv) > 3 else ''
    save(TRAT, t)
elif cmd == 'tratados':
    print(json.dumps(json.load(open(TRAT, encoding='utf-8')) if os.path.exists(TRAT) else {}, ensure_ascii=False, indent=1))
elif cmd == 'fecha':
    cat['updated'] = sys.argv[2]
    save(CAT, cat)
    publica(cat)
    n = sum(1 for it in cat['items'] for v in it['offers'].values() if v.get('ok', True) and v.get('price'))
    print(f'data {sys.argv[2]}: {n} ofertas no ar')
