# Pesquisa de fora: quem, com o quê e onde gravar

## Onde gravar

Escolha a pasta da entrega antes de pesquisar, para os pesquisadores gravarem direto nela.

1. **A pasta-mãe** é onde o projeto já guarda pesquisa e documentos. Para achar, veja `docs/`, `pesquisa/`, o que o `.gitignore` deixa fora do git e o que o CLAUDE.md ou o README do projeto mandam. Se o projeto tem uma pasta de pesquisa fora do git, é ela. Sem nada disso: `docs/`.
2. **Dentro dela, sempre o mesmo caminho**, para o próximo plano achar o anterior:
   - projeto inteiro: `melhoria/AAAA-MM-DD/`;
   - com foco: `melhoria/<foco>/AAAA-MM-DD/`.

Na pasta, sempre os mesmos nomes:

| Arquivo | O que tem |
|---|---|
| `plano.md` | O plano (etapa 5), começando pelo item para fazer primeiro |
| `comparacao.md` | Uma tabela por função (etapa 4) |
| `projeto.md` | A ficha, as funções com o estado, a pilha e os pontos fracos (etapa 1) |
| `bruto/` | Um arquivo por pesquisador ou por assunto, com link e data em cada achado. O nome diz o que tem: `parecidos.md`, `quem-usa.md`, `teste-<o que testou>.md` |

Se já existe um plano de outra data nesse caminho, leia antes de pesquisar. O `plano.md` novo abre com "O que mudou desde [data]": o que foi feito, o que caiu e o que é novo.

## Quem pesquisa o quê

| Modo | Pesquisadores |
|---|---|
| rápido | Você mesmo, sem subagente |
| normal | Até 3 subagentes em paralelo: (1) parecidos e repositórios; (2) quem usa; (3) técnicas, bibliotecas e barreiras |
| fundo | Um subagente por tipo de fonte da etapa 2 (os 6), todos na mesma mensagem |

Sem ferramenta de subagente, pesquise você mesmo, na ordem da etapa 2.

**No rápido:**

- uma busca curta para listar os parecidos, e ficam os 3 mais próximos do foco. Se o projeto tem funções bem diferentes, pode ser um parecido por função;
- de cada um, as issues mais comentadas e as mais recentes sobre a função;
- o arquivo em que ele resolve a função, lido direto, sem clonar;
- reclamações fora do GitHub (Reddit, vídeo, loja) ficam de fora: diga isso na entrega.

**No normal e no fundo**, todo pesquisador recebe:

- a ficha do projeto e a lista das funções com os pontos fracos, da etapa 1;
- o foco, se houver;
- a pergunta dele, puxada pelas funções ("quem faz X melhor, e como?"), não "pesquise o mercado";
- as regras da etapa 3, copiadas inteiras;
- o arquivo onde gravar, em `bruto/`;
- "devolva um resumo de 5 a 10 linhas; o resto fica no arquivo".

A comparação e o plano (etapas 4 e 5) são seus, não dos pesquisadores: só você leu o código do projeto.

## Ferramentas

Use o que estiver instalado. Sem nenhuma destas, busca web, leitura de página e `gh` dão conta.

**Pesquisa profunda (ex.: o MCP Trawl).** Serve para achar os parecidos e para ouvir quem usa: alcança Reddit, Hacker News, X, YouTube, fóruns e GitHub, que a busca web comum lê mal ou não lê. Para issues e código, o `gh` é mais direto.
- No rápido e no normal, consultas avulsas por ela.
- No fundo, a parte de "quem usa" vira uma pesquisa completa dela, com o relatório gravado em `bruto/`.
- Siga as regras da própria ferramenta. Não ligue por conta própria opção que ela deixa desligada.

**Skill deep-research.** Ela é um coordenador inteiro: dispara os próprios pesquisadores e escreve um relatório. Por isso entra só no modo fundo, e para uma pergunta aberta só: o panorama dos parecidos (quem existe, para quem, preço, se é mantido). No rápido e no normal ela repetiria o trabalho dos seus pesquisadores.
- Dispare primeiro os seus pesquisadores, em segundo plano. Depois chame a skill.
- Ela grava `research_notes/` e `reports/` na pasta em que roda. Ao terminar, mova as duas para dentro de `bruto/`. Não deixe nada na raiz do projeto.
- O relatório dela é matéria-prima: cada achado passa pelas regras da etapa 3 como qualquer outro.

**Busca de skills (ex.: /skillsmp-search).** Só quando o projeto é ele mesmo uma skill, um plugin, um servidor MCP ou outra ferramenta de agente: aí os parecidos moram nos diretórios de skills e de MCPs.
- Só a busca e a leitura na pasta isolada da própria skill de busca. Nada se instala nesta tarefa.
- A busca pode ter cota por dia na conta do dono: faça poucas consultas e diga quantas fez.

**GitHub (`gh`).** Para issues, PRs e versões dos parecidos de código aberto:
- `gh search issues --repo <dono/repo> "<termo>" --sort comments`: o que mais se repete e há quanto tempo está aberto;
- `gh release list -R <dono/repo>`: o que mudou e quando;
- `gh api repos/<dono/repo>/contents/<caminho>`: um arquivo só, sem clonar;
- para ler mais código, um clone raso (`git clone --depth 1`) numa pasta de rascunho fora do projeto, uma pasta nova por repositório.

Leia o corpo das issues que entram no plano. As outras contam só como título.

**Teste barato.** Numa pasta de rascunho fora do projeto, com um dado real do projeto. Instalar a biblioteca ali dentro pode. Nada entra no projeto e nada se instala no sistema. O comando e o que saiu vão para `bruto/`. Um bom teste barato: montar um caso com o defeito que um parecido já teve e rodar o projeto contra ele.

## Fontes de quem usa, por tipo de projeto

| Projeto | Onde estão as reclamações, os pedidos e os elogios |
|---|---|
| App de PC | Histórico de versões; Reddit da área; comentários de tutoriais no YouTube; issues do GitHub dos abertos; avaliações da Microsoft Store e do alternativeTo |
| Site ou serviço | Página de preço; G2, Capterra e Trustpilot; Reddit; Product Hunt |
| Ferramenta de programador, MCP ou skill | Issues e discussões do GitHub; Hacker News; Reddit; Stack Overflow; diretórios de skills e de MCPs |
| Jogo no Roblox | Página do jogo (curtidas, visitas, atualizações); comentários de vídeos de gameplay; Reddit; DevForum do Roblox; wikis dos jogadores |
| Jogo de PC | Avaliações da Steam, negativas e mistas primeiro; Reddit do jogo; comentários no YouTube; wikis |

Discord fica de fora quando o agente não tem acesso: registre como lacuna.

Frases de caça:

- `"<produto> problems"`, `"<produto> not working"`, `"<produto> bug"`
- `"switching from <produto> to"`, `"<produto> alternative"`, `"<produto> vs <produto>"`
- `"I wish <produto> could"`, `"frustrated with <categoria>"`

Cada citação vira uma linha: fonte, data, frase curta, produto, tema. Depois conte por tema ("X de Y fontes") e dê a certeza: alta com 3 ou mais fontes que falaram sem ninguém perguntar, média com 2, baixa com 1.
