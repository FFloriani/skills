# Como escrever as partes do README

Nenhuma fonte normativa prescreve a redação da proposta de valor; o que segue vem de padrões repetidos em 36 READMEs reais, do Write the Docs, do Google e da standard-readme, e do que a comunidade reclama. É boa prática, não regra.

## Frase de definição

Fórmula: **`<Nome> é <categoria> para <quem ou onde> que <resultado concreto>, <diferencial verificável>.`** Até 120 caracteres.

- Igual ao campo About do repositório e à `description` do manifesto (package.json, pyproject, Cargo.toml). Se estiverem diferentes, proponha alinhar.
- Em linguagem de quem vai usar: app de usuário final não fala de "framework" nem "arquitetura".
- Sem adjetivo que o leitor não pode verificar.
- Com o **termo que o público realmente busca** (tarefa + plataforma, na língua dele), uma vez, no começo: é o que o About e a busca vão usar. Pergunte ao usuário 2 ou 3 buscas; não empilhe palavras (`references/descoberta-e-seo.md`).

| Ruim | Bom |
|---|---|
| Um poderoso e incrível gerenciador revolucionário de tarefas. | Lista de tarefas para Windows que abre com um atalho e guarda tudo em um arquivo local, sem conta nem nuvem. |
| Biblioteca moderna e robusta para lidar com datas. | Biblioteca Python para somar, subtrair e formatar datas em fuso horário sem `pytz`. |
| Ferramenta CLI blazing fast. | CLI em Rust que procura texto em pastas grandes; em 4 GB de código leva 1,2 s (ver benchmark). |

Número só entra com a fonte (benchmark reproduzível, link). Sem fonte, fica de fora.

## Por que existe (3 a 5 linhas)

É o conteúdo que mais falta nos READMEs reais (propósito e status). Quatro linhas, todas opcionais, nesta ordem:

```markdown
## Por que existe
- **Dor:** <o que incomoda quem faz isso hoje>
- **O que falta nas alternativas:** <fato verificável; cite pelo nome só se o autor conhece e confirmou>
- **O que muda aqui:** <resultado, com número se houver>
- **O que NÃO faz:** <limite honesto>
```

O limite honesto ("não sincroniza entre aparelhos", "só Windows") aumenta a confiança e evita issue. Se o usuário não sabe responder "o que falta nas alternativas", omita; não invente comparação.

## Funcionalidades

- Escreva por **benefício**: `<capacidade> → <resultado para o usuário>`. "Exporta para PDF" é capacidade; "entrega o relatório pronto para enviar ao cliente" é benefício.
- 4 a 8 itens. Cada um deve ter rastro no código (comando, rota, tela, flag). Sem rastro, não entra.
- Muitas funcionalidades: tabela com ícone (opcional), nome, o que faz. App visual: uma imagem por recurso principal, não por recurso.
- Nunca "e muito mais". Liste ou corte.
- Roadmap só com itens que o autor confirmou; marque o que não existe ainda como "planejado".

## Início rápido

- Até cerca de 15 linhas, copiável, que **funciona** de um clone limpo (confira contra o manifesto, scripts e workflows).
- Mostre a **saída esperada**: é como o leitor sabe que deu certo.
- Pré-requisitos com versão mínima (`Python 3.10+`, `Node 20+`, `.NET 8`).
- Instalação trivial e uso mínimo no mesmo bloco; instalação cara, demo primeiro.
- Do caso simples ao complexo; o resto vai para `docs/`.

## Instalação

- Um bloco de código por gerenciador/SO; comandos exatos, sem `...`.
- Binário pré-compilado primeiro quando existir; "compilar do código" depois, em seção própria.
- Só cite winget, scoop, choco, brew, npm, pip, cargo se o pacote **existe** (confira no manifesto ou no registro). Prometer comando que não funciona é pior do que omitir.

## Comparação com alternativas (opcional)

Tabela de 3 a 5 linhas com critérios verificáveis (licença, plataformas, offline, preço), não adjetivos. Só se o autor conhece as alternativas. É a seção que o público de comunidade mais respeita, e a que mais envelhece: datar.

## Solução de problemas (opcional)

3 a 5 erros reais, cada um com a mensagem exata, a causa e a correção. Fonte: issues, logs e código de tratamento de erro do repositório. Sem issue nem erro conhecido, omita.

## Status, contribuir, licença

- **Status** em uma linha: ativo, em manutenção, experimental ou arquivado. Evita expectativa errada.
- **Contribuir**: onde abrir issue, se aceita PR, link para CONTRIBUTING.md se existir. Se não aceita contribuição, diga.
- **Licença**: nome SPDX e link para o arquivo LICENSE. Sem LICENSE, avise (é P0): sem licença, por padrão, ninguém pode legalmente reutilizar o código.

## Estilo

- Frases curtas, voz ativa, segunda pessoa direta nos passos ("Baixe", "Abra"), terceira na descrição.
- Termos da interface com o nome exato do botão ou menu, como aparece na tela.
- Um nome para cada coisa; não alterne "projeto", "ferramenta", "app", "plugin".
- Sem emoji decorativo. Emoji só funcional (✓ ✗ numa tabela de compatibilidade) e sempre com a palavra ao lado.
- Sem adjetivo de marketing: poderoso, incrível, revolucionário, robusto, perfeito, blazing fast, seamless, game-changer.
- Sem "fácil", "simples", "rápido" sem número ao lado ("3 passos", "abre em 1 s").
- Sem cara de IA: mergulhe, desbloqueie, potencialize, jornada, "seja você iniciante ou avançado", "no mundo acelerado de hoje", excesso de travessões, listas de três adjetivos.
- Sem contagem que envelhece: estrelas, downloads, versão escrita à mão. Use badge dinâmico.
- Sem segredo, e-mail ou caminho local do autor sem que ele tenha pedido.

## Idioma

Pergunte. Padrões:

- Público só brasileiro: README.md em português.
- Público internacional: README.md em inglês + `README.pt-BR.md` (a standard-readme reserva `README.md` ao inglês quando há mais de um idioma).
- Seletor de idiomas no topo de **todos** os arquivos; comandos, código e URLs ficam literais; traduza títulos de seção e alt de imagem.

Detalhes e marca de sincronização: `references/download-apoio-idiomas.md`.

## Antes e depois (modelo do que melhorar ao reescrever um README ruim)

Antes:

> 🚀 **O app mais poderoso e incrível para gerenciar suas tarefas!** Mergulhe numa jornada de produtividade com um design robusto. Clique [aqui](docs/guia.md) para saber mais.

Depois:

> # TaskPane
> Lista de tarefas para Windows que abre com um atalho e guarda tudo em um arquivo local, sem conta nem nuvem.
>
> [Baixar](#baixar) · [Guia de uso](docs/guia.md) · [Reportar problema](../../issues)

O que mudou: definição verificável no lugar de adjetivos, navegação com links descritivos, nada de emoji decorativo, caminho para obter visível.
