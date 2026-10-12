# Descoberta (SEO de GitHub): ser encontrado e converter

Base: pesquisa de 2026-10-12 com testes reais na API de busca do GitHub, leitura da documentação oficial (GitHub, Google, registros de pacotes) e estudos empíricos. Cada regra diz o nível de evidência: **[DOC]** documentado, **[TESTE]** observado em teste real, **[ESTUDO]**, **[INFERÊNCIA]** dedução a partir dos itens citados, **[OPINIÃO]** sem fonte primária.

## O que muda a abordagem

Três fatos que a maioria dos guias de "GitHub SEO" ignora:

1. **A busca padrão do GitHub olha nome, descrição (About) e topics.** O README só entra com `in:readme` [DOC + TESTE, 6 termos]. Texto que só existe no README é invisível para quem busca do jeito normal.
2. **O único sinal de ranking documentado são estrelas** [DOC]. O "best match" é descrito só como "múltiplos fatores combinados", sem pesos. No teste, nome idêntico ao termo sobe mais, só-README fica na metade de baixo, e estrelas correlacionam com posição melhor mesmo dentro da mesma classe de correspondência [TESTE, correlação].
3. **Não existe estudo que ligue texto de README, número de topics ou nome ao ranking** (no GitHub ou no Google). O que se pode afirmar é *onde* cada texto aparece.

Por isso esta skill otimiza duas coisas, e só promete essas:

- **Elegibilidade**: ser casado pelos campos certos (nome, About, topics) com as palavras que o público usa.
- **Conversão**: quem chega entende em segundos e instala (README, preview, download).

Nunca prometa posição, Trending, estrelas nem "mais tráfego".

## Frase canônica

Escreva **uma** frase (a mesma da definição do README: o que é, para quem, plataforma) e derive as variantes por superfície:

| Superfície | Variante | Limite |
|---|---|---|
| README, primeira frase | Frase canônica completa | até ~120 caracteres (heurística) |
| About do repositório | Começa pelo termo que a pessoa buscaria + benefício | ≤ 350 (visto em teste, **não documentado**); ideal ≤ 160 para não cortar em cartão e resultado [OPINIÃO] |
| PyPI `description`, Scoop `description`, crates.io `description` | Uma linha, texto simples | crates.io: texto simples, sem Markdown |
| Docker Hub (descrição curta) | Uma ou duas frases | 100 caracteres [DOC] |
| Homebrew `desc` | Sem artigo inicial, sem o nome da fórmula, sem ponto final | 80 caracteres [DOC, regra do `brew audit`] |
| winget `ShortDescription`, Chocolatey `description` | Diga o que o instalador faz, não adjetivos | Chocolatey: ≥ 30 e ≤ 4000 |

## Checklist por superfície

### Nome do repositório [TESTE + DOC]
- Curto e memorável (recomendação do GitHub). Com o termo-alvo em kebab-case se couber (`markdown-editor`).
- A busca casa nome por infixo (`pomodoro` acha `openpomodoro-cli`) e nome idêntico ao termo domina o topo. Nome genérico (`app`, `project`) compete com milhares de homônimos.
- Renomear mantém estrelas e links (redireciona), mas quebra Pages de projeto e Actions hospedadas, e **não reutilize o nome antigo**. Escolha o nome certo antes de divulgar.

### About (descrição) [DOC + TESTE]
- Tem papel triplo: campo de busca, `og:description` / `<title>` / meta description do Google, e linha nas listas.
- **Sem About, o GitHub usa texto genérico** ("Contribute to owner/repo development by creating an account on GitHub.") mesmo com README excelente. About vazio é P1.
- Comece pelo termo que a pessoa buscaria e o benefício; deve fazer sentido sem o README. Sem emoji nem aviso temporário (entram no título).
- Descrição casa por palavra inteira, com acento, caixa e plural normalizados: escrever "gestão" também é achado por "gestao". Não abrevie esperando prefixo.
- Fork herda o About do original: reescreva.

### Topics [DOC + TESTE]
- Até **20**, minúsculas, números e hífens, até **50** caracteres.
- **Atômicos**: `machine` não casa `machine-learning`. Use o topic exato que as pessoas usam e confira em `github.com/topics/<x>`.
- 5 a 10 precisos (linguagem, domínio, tipo, plataforma, tecnologia) [INFERÊNCIA: não há evidência de que 20 seja melhor que 8, e muitos parecem spam].
- Sem topics, o repositório não aparece em `topic:` nem na página do topic, e só o nome o casa.
- Página curada de topic exige PR em `github/explore` e rejeita autopromoção: **não ofereça isso como tática** para projeto próprio.
- Nenhum efeito de ranking documentado nem detectado. O ganho comprovado é entrar em `topic:`, `in:topics` e na página do topic.

### Website (campo do About) [DOC]
Link para a documentação, o site ou, na falta, a página de Releases (`.../releases/latest`). Campo vazio é oportunidade perdida, não erro.

### Social preview [DOC + TESTE]
- PNG, JPG ou GIF **< 1 MB**, 1280×640 recomendado (mínimo 640×320), fundo sólido; só de repositório público; configurado manualmente em Settings (não há API).
- Sem imagem, o GitHub gera um cartão automático 1200×600 com nome e descrição: já é decente. A imagem própria compensa quando o cartão automático ficaria genérico.
- A skill **não gera a imagem**: entregue a especificação e o texto (nome, frase, 1 palavra de plataforma).

### README como fonte de busca externa [DOC Google + INFERÊNCIA]
- O Google monta o `<title>` a partir do nome e do About e o snippet principalmente do conteúdo da página (o README renderizado). Não há fonte que ligue primeira frase ou densidade de palavras a posição.
- Regra honesta: primeira frase com o nome e a tarefa na linguagem do usuário ("TaskPane é uma lista de tarefas para Windows"), uma vez, sem lista de palavras. Palavras de plataforma e formato que a pessoa busca ("Windows 10/11", "portátil", "instalador", "winget") em texto normal.
- Headings com palavras reais de uso ("Instalação no Windows", "Como funciona"); alt descritivo e nome de arquivo legível (`windows-installer.png`, não `image1.png`).
- "Alternativa a X" só se for verdade e com comparação factual. Repetição artificial de palavras é spam para o Google.
- README com mais de 500 KiB é truncado.

### Comunidade (Community Standards) [DOC + TESTE]
É um checklist de arquivos (README, descrição, LICENSE, CODE_OF_CONDUCT, CONTRIBUTING, templates), cerca de 1/7 por item. **Não mede qualidade nem entra comprovadamente em ranking.** Útil como higiene. `CONTRIBUTING.md` gera aba própria e link na sidebar; LICENSE precisa ser simples para ser detectada.

### Armadilhas verificadas [TESTE]
Em ordem de impacto: (1) o termo não está em nome, About nem topics; (2) sem topics; (3) nome genérico; (4) About vago; (5) fork (escondido por padrão na busca: ~12% dos resultados de `pomodoro`, ~65% de `jquery`); (6) README gigante. Repositório arquivado continua aparecendo na busca padrão.

## Fora do GitHub

### Google [DOC + TESTE em 5 páginas]
- `<title>` = `GitHub - owner/repo: <About>`; as tags `og:*` e `twitter:*` vêm do nome e do About, não do README.
- O `robots.txt` do GitHub não bloqueia `/<owner>/<repo>`; não achei `noindex` em fork, repositório novo nem com 0 estrelas. Não confirmei política oficial.
- Árvores de diretório (`/tree/`), `raw`, `blame` e listagens com `?tab=` não são rastreadas; a página raiz com o README renderizado é a que vale.
- Você não controla `<head>`, canonical nem sitemap numa página de repositório. **GitHub Pages** só vale se o projeto precisa de site próprio (docs longas, páginas por tema): `jekyll-seo-tag` e `jekyll-sitemap`, e `robots.txt`/`sitemap.xml` à mão porque o Pages não cria.
- Página nova tem poucos links entrantes: links de registros de pacotes, listas e posts ajudam [INFERÊNCIA].

### Busca e assistentes de IA
- Rastreadores de IA têm grupo próprio no `robots.txt` do GitHub, sem `Disallow: /` [TESTE]. Assistentes que buscam na web por pedido do usuário **provavelmente** consultam README e página [INFERÊNCIA, não comprovado].
- **`llms.txt`**: o Google diz que não é necessário e não há prova de consumo por provedores. Um repositório não serve `/llms.txt` na raiz do domínio. **Não gere** para repositório comum.
- **`AGENTS.md`** é para agentes de código que contribuem no repositório (build, testes, estilo), não para descoberta. No máximo uma linha no README se aceitar contribuição.
- O que ajuda a ser bem resumido é o que ajuda humanos: definição explícita ("X é um <tipo> que <faz>, para <público>, em <plataforma>"), nome consistente, títulos que dizem o conteúdo, requisitos e licença em seções nomeadas, afirmações verificáveis [INFERÊNCIA]. Não infle o README "para IA".

### Registros de pacotes e vitrines [DOC]
Cada um cria uma página própria que linka de volta ao repositório e tem busca interna.

| Registro | Campos que alimentam a busca | Limites e regras |
|---|---|---|
| npm | `description`, `keywords`, README, título | "minimal boost" que rebaixa spam e pacote totalmente novo; novo pode levar até 2 semanas para aparecer |
| PyPI | `description` (uma linha), `keywords`, `classifiers`, README (`text/markdown`) | sem limite documentado; validar com `twine check dist/*` |
| crates.io | `description` (texto simples), `keywords`, `categories` | 5 keywords (≤ 20 caracteres, ASCII), 5 categorias que batam com `category_slugs` |
| NuGet | `description`, `tags`, `readme` (Markdown) | descrição e tags até 4000; ícone ≤ 1 MB, 128×128 |
| winget | `PackageName`, `ShortDescription`, `Tags`, `Moniker` | `PackageName` e `Publisher` devem bater com o Adicionar/Remover Programas; a doc é inconsistente sobre quais campos a busca usa |
| Scoop | nome do manifesto e executáveis (`bin`) | a descrição não é critério de busca (por leitura do código; conferir) |
| Chocolatey | `title`, `description`, `tags` | `title` = nome do app; descrição entre 30 e 4000; tag sem vírgula e sem "Chocolatey" |
| VS Code Marketplace | `keywords`, `categories`, `displayName` | até 30 keywords; categorias fixas |
| Docker Hub | descrição curta, categorias | 100 caracteres; até 3 categorias |
| Homebrew | `desc`, `homepage` | `desc` ≤ 80 caracteres, regras do `brew audit` |

Use o vocabulário de uso (tarefa, plataforma, formato) e **não** coloque tag sem relação com o projeto (o npm rebaixa spam).

## Divulgação e engajamento (sem prometer)

### Expectativa realista
- Crescimento de estrelas é majoritariamente **lento** (58% a 66% dos repositórios populares estudados); picos virais são 1,6% a 2,3% [ESTUDO: Borges 2016, Borges e Valente 2018].
- A imensa maioria dos repositórios tem pouquíssimas estrelas (cauda de lei de potência). Os percentuais antigos (80% sem estrela, dados até 2014) **não** valem para 2026: diga "poucas estrelas é o normal", sem número.
- Estrela mede atenção, não adoção: em survey (n=791), 52,5% estrelam por apreço e 51,1% como bookmark [ESTUDO].
- Todas as amostras de promoção selecionam projetos que já eram populares ou citados: **não provam** que divulgar gera estrelas para projeto novo.

### Canais e as regras de cada um [DOC]
| Canal | O que vale | O que é proibido |
|---|---|---|
| Show HN | Algo que se constrói e que as pessoas podem **experimentar**, sem cadastro; título "Show HN: <nome> - <o que faz>"; autor presente para responder | Pedir voto ou comentário a amigos; página de captação; blog, lista ou newsletter |
| Hacker News (geral) | Fonte original, título sem caixa alta nem exclamação | Pedir upvote; usar principalmente para promoção; texto gerado |
| Product Hunt | Lançar a cada iteração significativa; pedir que visitem e comentem | Conta de empresa; pedir upvote diretamente |
| Listas `awesome-*` | Ler o `contributing.md` **daquela lista**; cada uma define formato e critérios | Submeter sem ler; PR gerado por IA nas listas que proíbem |
| Reddit | Regras são por subreddit; leia antes | Não consegui ler as regras oficiais; fonte secundária |
| Hacktoberfest 2026 | — | Em 2026 PRs deixaram de contar para recompensas: não dependa |

Evidência de eficácia: correlação entre post no HN e estrelas em projetos já populares (mediana 74 para 138 estrelas em 3 dias na amostra de 2019, e 3 em cada 4 posts com 12 upvotes ou menos); estudo quase-causal de Twitter (ICSE 2022) acha efeito em estrelas e pequeno em contribuidores [ESTUDO]. Divulgar é **exposição**, não garantia.

### O que sustenta a conversa
Em qualquer canal, o que o visitante encontra é o repositório: README com definição clara, instalação testada, release com download e licença. Prepare isso **antes** de postar.

### Contribuição [DOC + ESTUDO]
- Label `good first issue` é documentada e alimenta páginas de descoberta de tarefas, mas **quase metade nunca é resolvida por novatos** (Tan et al., FSE 2020). O ganho vem de issue bem escrita (escopo, contexto, onde mexer).
- `CONTRIBUTING.md` típico não cobre "como escolher uma tarefa" e "como falar com a comunidade", as barreiras mais citadas (84% omitem ≥ 2 de 6 barreiras, Fronchetti, FSE 2023). Cubra as duas.
- Responder rápido a quem chega é a barreira social mais frequente na literatura (correlacional). Templates de issue/PR: higiene de triagem, sem prometer ganho.

### Estrelas falsas e "star this repo"
- **Nunca** sugerir compra, troca (star-for-star), grupo de troca, bot, nem sorteio ou benefício condicionado a estrelar. A política de uso aceitável do GitHub proíbe "rank abuse" e "inauthentic interactions"; o estudo de He et al. (ICSE 2026) achou 18.617 repositórios com campanha, e o GitHub apagou 90,42% deles; o efeito da estrela falsa dura menos de 2 meses e é cerca de 5x menor que o da real [ESTUDO].
- Pedir estrela de forma simples e honesta ("se foi útil, uma estrela ajuda outras pessoas a achar") não aparece em nenhuma regra lida; **não há estudo de efeito**. Trate como opcional e de baixo peso; clareza do README pesa mais.
- Pedir upvote em HN ou Product Hunt é proibido por essas plataformas.

### Medir
Insights → Traffic (push access): clones, visitantes dos últimos 14 dias, sites de referência (exclui buscadores e o próprio GitHub) e conteúdo popular.

## Pacote de descoberta (o que a skill entrega)

1. **About** pronto (frase canônica adaptada, ≤ 160 caracteres se possível, termo principal no começo).
2. **Topics**: 5 a 10, com a lista candidata do `descobrir_fatos.py` confirmada (existem e são usados).
3. **Website**: sugestão (docs, site ou Releases).
4. **Social preview**: especificação 1280×640 < 1 MB + texto da imagem; o usuário sobe em Settings.
5. **Descrições por registro** (as que se aplicam ao projeto), derivadas da frase canônica, respeitando os limites.
6. **Plano de lançamento honesto** (checklist, sem prometer resultado): release com download e notas; README testado de clone limpo; 2 ou 3 issues `good first issue` bem escritas se aceitar contribuição; `CONTRIBUTING.md` cobrindo as duas barreiras; post "Show HN" ou em comunidade relevante, seguindo as regras do canal, sem pedir voto; responder perguntas.
7. Metadados **entregues como texto**, nunca aplicados sem pedido (regra 8 do `SKILL.md`).

Para repositório já publicado, rode `scripts/auditar_descoberta.py`.

## O que não está provado

| Afirmação comum | Situação |
|---|---|
| Mais topics melhoram o ranking | Não documentado nem detectado |
| Palavras-chave no README sobem posição (GitHub ou Google) | Sem fonte; README só entra na busca do GitHub com `in:readme` |
| Releases, Sponsors, Discussions ou commits frequentes sobem o ranking | Nenhum documento declara |
| Trending depende de X | Fórmula atual não publicada (só post de 2013); teorias da comunidade são especulação |
| `llms.txt` ajuda a ser citado por IA | Google diz que não é necessário; sem prova de consumo |
| Community profile 100% aumenta visibilidade | É checklist de arquivos; sem prova de efeito |
| "Star this repo" aumenta estrelas | Sem estudo |
| Limite de 350 caracteres do About | Visto em teste, não documentado |
| Arquivar derruba da busca | Falso na busca padrão (arquivados aparecem) |
