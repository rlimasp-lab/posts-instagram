# Atualização diária de preços do Placar do Desconto

Site: https://placardodesconto.com (Hostinger publica sozinha cada push no ramo `placar-site`).

Arquivos:
- `tools/catalogo.json`: catálogo completo (produtos, links de afiliado, ids MLB e ASIN, último preço, `ok`).
- `data.json`: o que o site lê. Gerado pelo `atualiza.py`; não editar à mão.
- `tools/coleta_ml.js` e `tools/coleta_amazon.js`: coletores para rodar no Chrome do Rodrigo (javascript_tool).
- `tools/atualiza.py`: aplica os resultados e gera o `data.json`.

Passo a passo:
1. `python3 tools/atualiza.py ids ml` e cole a saída no lugar de `__IDS__` em `coleta_ml.js`.
2. Rode o script numa aba em https://www.mercadolivre.com.br e leia `window.__COLETA` até sair do null (cerca de 1 a 2 minutos).
3. Salve o JSON em um arquivo e rode `python3 tools/atualiza.py aplica ml ARQUIVO`.
4. Repita 1 a 3 com `am`, `coleta_amazon.js` e uma aba em https://www.amazon.com.br.
5. `python3 tools/atualiza.py fecha AAAA-MM-DD`, commit e push no ramo `placar-site`.

Regras do `atualiza.py`: oferta sem preço some do site no dia (volta quando tiver preço de novo);
variação acima de 35% é ignorada como provável erro de leitura e aparece no resumo.

## Produtos novos a partir das buscas do site

O site registra cada busca (sem IP e sem cookies) em `buscas.php`, que grava fora da pasta pública.
`https://placardodesconto.com/buscas.php?top` devolve os termos sem resultado mais buscados nos últimos 14 dias (só os buscados 2 vezes ou mais).

Para cada termo novo (confira `python3 tools/atualiza.py tratados`):
1. Escolha UM produto que represente bem a busca: novo, de loja oficial ou vendedor bem avaliado, sem "recondicionado", "caixa aberta" ou "usado".
2. Mercado Livre: pegue o id `MLB...` da URL `/p/MLB...`, o preço da página e o código da foto (`123456-MLA123456789_112026`). Gere o link de afiliado em https://www.mercadolivre.com.br/afiliados/linkbuilder (conta liro1164283 já logada no Chrome) e use o link `https://meli.la/...` que ele devolver.
3. Amazon: procure o MESMO modelo (mesma voltagem e capacidade). Se não tiver certeza de que é o mesmo produto, deixe a Amazon de fora. Informe só o ASIN; o script monta o link com a tag.
4. Monte um arquivo e rode `python3 tools/atualiza.py adiciona ARQUIVO`:
```json
{"categories": [{"id": "airfryer", "label": "Air fryers", "spec": "Capacidade"}],
 "items": [{"cat": "airfryer", "name": "Air Fryer Mondial 4 L AFN-40", "brand": "Mondial", "spec": "4 L",
   "img": "123456-MLA123456789_112026", "origem": "busca: air fryer",
   "offers": {"ml": {"price": 299, "orig": 399, "link": "https://meli.la/XXXX", "mlb": "MLB123456"},
              "am": {"price": 289, "orig": null, "asin": "B0XXXXXXXX"}}}]}
```
`categories` só é necessário quando a categoria ainda não existe.
5. Marque o termo: `python3 tools/atualiza.py tratado "air fryer" "incluido: Air Fryer Mondial 4 L"` (ou o motivo de não incluir).
