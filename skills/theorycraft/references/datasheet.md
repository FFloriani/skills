# Datasheet: formato e convenções

## Por que banco e não só planilha
Build cruza tabelas (item, afixo, habilidade, atributo, inimigo) e roda fórmulas. Um banco SQLite
faz consulta e junção de verdade, aguenta milhões de linhas e é um arquivo só. A planilha é uma
vista gerada dele para consultar e filtrar. As fórmulas moram na calculadora (`calc.py`), testada.

## Estrutura
```
theorycraft/<jogo>/<versão>/
  README.md        versão, data, cobertura, como consultar
  inventario.csv   todos os arquivos e o status de cada um
  dados/           tabelas extraídas, CSV ou JSON, com o nome original
  jogo.sqlite      banco montado por scripts/montar_banco.py
  esquema.md       o que é cada tabela e coluna, e como se ligam
  mecanicas/       uma ficha por sistema
  builds/          uma ficha por build analisada
  planilha.xlsx    opcional (scripts/exportar_planilha.py)
theorycraft/<jogo>/calc.py      calculadora (copiada de scripts/calc_modelo.py)
theorycraft/<jogo>/DIARIO.md    fatos confirmados com fonte e status
```

## Convenções
- **Versão em tudo**: pasta, README, cabeçalho de cada ficha. Número sem versão não serve.
- **Nomes originais**: mantenha o nome do arquivo e da coluna como o jogo usa; traduza só nas views.
- **IDs e nomes**: as tabelas de localização viram tabelas no banco; crie views que juntem ID e
  nome legível (ex.: `CREATE VIEW itens_legiveis AS SELECT i.*, l.texto AS nome FROM itens i
  LEFT JOIN loc_pt l ON l.chave = i.nome_id`).
- **Unidades**: anote em `esquema.md` se o valor é fração (0.15) ou ponto percentual (15), por
  segundo ou por quadro, e o que significa cada enum.
- **Fonte**: a tabela `_fontes` diz de qual arquivo veio cada tabela; cite-a nas fichas.

## Cobertura
O README do datasheet traz o resultado de `scripts/cobertura.py`: quantos arquivos relevantes
foram extraídos, quantos foram descartados (com motivo) e quantos falharam (com o que foi tentado).
Sem esse relatório não dá para afirmar que o datasheet está completo.

## Ficha de mecânica (`mecanicas/<sistema>.md`)
```
# <Sistema> — versão <x.y.z>
Regra: <em palavras>
Fórmula: <notação matemática>
Ordem: <passos na ordem do código>
Arredondamento e limites: <...>
Fonte: <arquivo e método ou endereço / tabela e coluna>
Status: confirmado | inferido | localizado-não-expandido | medido-jogando
Testes: <casos na calc.py que cobrem esta fórmula>
```

## Ficha de build (`builds/<nome>.md`)
Objetivo, premissas, itens e pontos, números (DPS, vida efetiva, breakpoints), comparação com as
alternativas, pesos de atributo e o que ainda é incerto.

## Consultar
- **Planilha**: `python scripts/exportar_planilha.py jogo.sqlite --saida planilha.xlsx`
  (precisa de `pip install openpyxl`; sem ele sai um CSV por tabela, que abre no Excel ou no
  Google Sheets).
- **Navegador**: `pip install datasette` e `datasette jogo.sqlite` abre o banco numa página local,
  com filtro, busca e SQL. É a forma mais confortável de explorar milhares de linhas.
- **Patch novo**: monte o banco da versão nova e rode `scripts/diff_versoes.py`.
