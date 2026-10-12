# Auditoria de README: prioridades, checklist e relatório

## Prioridades

- **P0**: falha de função. O README engana, não informa ou quebra. Bloqueia a publicação: corrija antes de entregar.
- **P1**: degrada compreensão ou confiança. Corrija quando o usuário concordar; explique o motivo em uma linha.
- **P2**: polimento. Sugira, não insista.

Os limiares numéricos (até 5 badges, ~15 linhas de início rápido, 80 a 300 linhas) são decisões de design desta skill, não normas validadas. Apresente como heurística.

## Como rodar

```bash
python scripts/auditar_readme.py README.md --tipo app
python scripts/auditar_readme.py README.md --tipo cli --json
```

`--tipo`: `app`, `jogo`, `mod`, `cli`, `biblioteca`, `api`, `awesome`, `extensao`. Liga as checagens que dependem do tipo (prova visual, licença em lista awesome). Código de saída 1 se houver P0.

## O que o script checa

| Prioridade | Código | Verificação |
|---|---|---|
| P0 | `sem-definicao` | Há frase de definição perto do topo |
| P0 | `sem-caminho-para-obter`, `obter-tarde` | Existe seção de instalação/download/início rápido, antes da metade do arquivo |
| P0 | `placeholder` | Sem TODO, "em breve", `OWNER/REPO`, `NomeDoApp`, `[badge ...]` |
| P0 | `imagem-quebrado`, `link-quebrado`, `caixa-errada` | Arquivos locais existem, com a caixa exata |
| P0 | `sem-licenca` | LICENSE na raiz (exceto lista awesome) |
| P0 | `segredo` | Token, chave privada ou valor atribuído a `password`/`token`/`api_key` |
| P1 | `sem-prova-visual` | App, jogo, mod ou extensão com imagem/vídeo antes da instalação |
| P1 | `alt-vazio`, `alt-generico` | Texto alternativo útil |
| P1 | `muralha-de-badges`, `badge-duplicado`, `badge-rota-aposentada` | Até 8 badges, sem duplicata, rota válida |
| P1 | `apoio-antes-do-download` | Apoio depois de definição e download |
| P1 | `html-removido`, `html-atributo-removido`, `video-bruto` | HTML que o GitHub remove |
| P1 | `ancora-quebrada`, `link-nao-descritivo` | Âncoras válidas, links descritivos |
| P1 | `varios-h1`, `sem-h1`, `nivel-pulado` | Hierarquia de títulos |
| P1 | `inicio-rapido-longo` | Primeiro bloco do início rápido com até 20 linhas |
| P1 | `sem-contribuicao-nem-suporte`, `licenca-nao-citada` | Como contribuir/pedir ajuda; licença citada |
| P1 | `seletor-de-idiomas`, `paridade-traducao` | Seletor idêntico e mesma estrutura de títulos entre `README.md` e `README.<tag>.md` |
| P1 | `caminho-local`, `email`, `definicao-longa`, `muito-curto`, `mermaid-*` | Dados pessoais; definição ≤160; tamanho; Mermaid válido |
| P2 | `muitos-badges`, `emoji-*`, `shortcode-emoji` | Até 5 badges; sem emoji decorativo |
| P2 | `adjetivo-vazio`, `cara-de-ia`, `travessao` | Texto sem marketing nem tique de IA |
| P2 | `contagem-fixa`, `versao-fixa`, `fragmento-gh-depreciado` | Nada que envelhece; `<picture>` no lugar de `#gh-*` |
| P2 | `muito-longo`, `sem-toc`, `sem-demo`, `sem-status` | Tamanho, sumário, demo de CLI, status |
| P2 | `conteudo-de-mantenedor` | Runbook de release, secrets do CI, estrutura do repositório fora do README do usuário |
| P2 | `fato-repetido`, `bloco-repetido` | Um lar por fato: nada dito ou colado duas vezes |
| P2 | `licenca-restritiva-no-fim`, `paridade-traducao-conteudo` | Licença copyleft/restritiva avisada no topo; blocos/tabelas/imagens iguais entre traduções |

## O que o script NÃO vê (revisão humana, sua)

Faça esta leitura **depois** do script e **antes** de entregar:

1. **A definição é clara?** Leia só as 3 primeiras linhas: alguém que nunca viu o projeto entende o que é e para quem?
2. **Cada promessa tem rastro no repositório?** Comando, flag, funcionalidade, requisito, versão, "portátil", "offline", "sem telemetria". Cruze com o registro de fatos.
3. **O início rápido funciona de um clone limpo?** Se for seguro, rode os comandos; senão, confira contra manifesto e scripts.
4. **Os nomes de asset batem** com o release publicado ou com o workflow?
5. **O About, a `description` do manifesto e a definição** dizem a mesma coisa?
6. **O tom é de gente**: frases diretas, termos da interface exatos, sem adjetivo de marketing?
7. **Nada exposto** sem o usuário querer: e-mail, caminho, chave Pix, nome real.
8. **Se há tradução**, ela está em sincronia com o original e soa natural (não traduzês)?
9. **Públicos misturados**: há conteúdo de mantenedor entre o de usuário? **Enquadramento de uma ferramenta só** depois que o projeto passou a suportar várias? (confira contra o código: o texto antigo pode estar errado.)
10. **Defasagem**: versões, nomes de arquivo e links batem com `git log` e com os arquivos de hoje?
11. **O README é citado em testes ou CI?** (`readme_citado_em_testes_ou_ci` do descobridor.) Se sim, a mudança precisa ajustar o teste, com justificativa.
12. **Preferência do autor**: o que é enfeite do autor e não problema? Pergunte antes de cortar (P0 não é preferência).

Pré-voo completo para README existente: `references/melhorar-readme-existente.md`.

## Relatório de auditoria (modo "só auditar")

Entregue, nesta ordem:

1. **Veredito em uma linha**: "Pronto para publicar" / "Precisa de correções antes de publicar" (se houver P0) / "Bom, com ajustes".
2. **P0 → P1 → P2** em tabela (linha, problema, correção). Para P0 e P1, ofereça aplicar a correção.
3. **O que você leu e não conseguiu checar** (ex.: não rodei o comando; não vi o release).
4. **Próximo passo**: uma ação (corrigir os P0; ou regenerar com `better-readme criar`).

Não reescreva o README no modo auditar sem pedido. Quando o usuário pedir para aplicar as correções (modo melhorar), entregue o resultado como **lista de decisões** (moveu, removeu e por quê, reescreveu, manteve por preferência sua, testes alterados, pendências): modelo em `references/melhorar-readme-existente.md`.

## O que é boa prática (não regra): como apresentar

Para estes itens, ofereça como sugestão, explique em uma linha **por que**, aceite recusa e **nunca** afirme efeito sobre estrelas, adoção ou contribuição (nenhum estudo mostra causalidade; o único estudo de popularidade é correlacional):

| Item | Situação das fontes |
|---|---|
| Número de badges | Mediana 4 nos READMEs lidos; "até 5 por linha" é opinião de um blog |
| Emoji | Opinião, contestada na própria thread; funcional é tolerado |
| Falta de screenshot = projeto imaturo | Não confirmado em verificação: um comentarista só |
| Diagrama melhora compreensão | Sem estudo; 0 de 38 READMEs lidos usam Mermaid |
| Posição e tom do apoio | Sem estudo; prática de projetos grandes é fim do arquivo |
| Acessibilidade em README | Sem estudo; vale por ser norma e guia |
| README traduzido aumenta alcance | Sem fonte |
| "Entender em 30 segundos" | Formulação de skill de terceiros; critério interno, não norma |
| Tamanho ideal (80 a 300 linhas) | Heurística do corpus, sem medição |
| Padrão de portátil (zip + pasta `data` + nome sem versão + checksums) | Veio de PR aberto e issue; VS Code corrobora a ideia |
| Qualidade de README gerado por IA | Sem benchmark; por isso registro de fatos e validação mecânica |

## Conflitos entre fontes e como esta skill os resolve

| Conflito | Resolução |
|---|---|
| Instalação antes ou depois do uso | Trivial: junte num "Início rápido". Cara: demo antes. App de usuário final: download antes de tudo |
| README curto (GitHub, Google) × "longo é melhor que curto" (makeareadme) | O README tem tudo para o **primeiro sucesso**; referência e explicação vão para `docs/` |
| Licença no fim (standard-readme) × no topo (Art of README) | Badge ou linha no topo, LICENSE na raiz, seção curta no fim; lista awesome não tem seção |
| Background primeiro (standard-readme) × screenshot primeiro (apps) | Biblioteca: "Por que existe" curto antes da instalação. App: screenshot e download antes |
| Badges: lista de curadoria valoriza × projetos grandes usam poucos | 3 a 5 que respondem a perguntas reais |
| Emoji: "nunca" × funcional | Sem decorativo; funcional só com a palavra ao lado |
| Local do FUNDING.yml | Sempre `.github/FUNDING.yml`; só chaves documentadas |
| Nome do README traduzido (`README.pt-BR.md` × `readme_i18n/...`) | Projeto novo: padrão da standard-readme, na raiz |
| Caminho de imagem (relativo × absoluto) | Relativo por padrão; absoluto se o README também sai em PyPI/npm |
| Tema claro/escuro | `<picture>`; `#gh-*` só em README antigo |
| Posição do apoio (topo × fim) | Fim, depois de definição, download e contribuir |
| README grande sem download (Rufus, Notepad++) × download visível | Projeto novo sem site precisa de download visível; os grandes têm marca e site |
