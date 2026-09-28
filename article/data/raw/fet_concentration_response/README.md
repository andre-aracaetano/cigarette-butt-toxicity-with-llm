# FET — curvas de concentração–resposta

## Fonte consolidada

`dataset_todos_fet.xlsx` é uma cópia de trabalho do arquivo localizado em:

`github/cigarette-butt-toxicity-with-llm/bancos de dados/dataset_todos_fet.xlsx`

O arquivo contém abas BCT e BST com concentração, mortalidade, eclosão em 72 e
96 hpf, total de ovos, datas, indicação de remoção e observações.

## Problema nos notebooks antigos

Os notebooks em `LC50_EC50/` procuram um arquivo ausente chamado
`resultados_FET.xlsx`. Além disso, os filtros não são consistentes:

- LC50 remove linhas com `remove == 1` e depois elimina linhas por índice;
- EC50 usa critérios diferentes para BCT e BST;
- alguns ensaios marcados como `bad` não têm necessariamente `remove == 1`;
- um gráfico BST foi salvo com nome BCT.

Antes do ajuste definitivo, estabelecer uma regra baseada em critérios
experimentais e datas, nunca em índices de linha.

