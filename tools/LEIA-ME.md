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
