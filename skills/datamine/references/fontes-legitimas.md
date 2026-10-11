# Fontes legítimas: o que conferir antes de extrair

Muitas vezes a resposta já está pronta numa wiki, num patch note, em código liberado pelo dono ou
num projeto de exemplo da engine. Essas fontes são mais rápidas, trazem nomes e comentários reais e
evitam a zona cinzenta de decompilar e decifrar.

## Sumário

1. Ordem de busca
2. Como marcar o status
3. Wikis da comunidade
4. Dados oficiais e patch notes
5. Código liberado
6. Decompilações comunitárias
7. Projetos de exemplo das engines
8. Livros, palestras e análises
9. Clonar para aprender: o formato do 20 Games Challenge
10. Normas da comunidade

## 1. Ordem de busca

Procure nesta ordem e pare quando achar o que precisa:

1. wiki da comunidade com tabelas de dados;
2. dados oficiais e patch notes;
3. código liberado pelo próprio dono;
4. projeto de decompilação comunitário (clássicos de console);
5. projeto de exemplo da engine, para a parte técnica;
6. livros, palestras e análises, para a intenção de design;
7. medir jogando.

Só depois disso extraia dos arquivos (SKILL.md, "Passo 2 — Extrair").

## 2. Como marcar o status

- Número de wiki, patch note ou dica do jogo: `inferido` até conferir no arquivo (`confirmado`) ou
  jogando (`medido-jogando`). Anote página, versão do jogo e data em `estudo/<jogo>/DIARIO.md`.
- Código liberado da mesma versão do jogo, com o corpo lido: `confirmado`.
- Dica do jogo (*tooltip*) não é fórmula: costuma arredondar e simplificar.

## 3. Wikis da comunidade

- Muitas wikis publicam tabelas completas de itens, XP, drop e dano, em geral tiradas por
  datamining (leitura dos dados nos arquivos do jogo) e conferidas por jogadores. A Stardew Valley
  Wiki, por exemplo, traz o XP acumulado de cada nível de habilidade, de 100 no nível 1 a 15000 no
  nível 10.
- Jogadores citam como referência as wikis de RimWorld, Disco Elysium, Old School RuneScape e as da
  Fextralife.
- Confira a versão do jogo e a data da página: wiki desatualizada é comum.
- Nem toda tabela tem fórmula. A de Stardew não se encaixa em nenhuma curva única, sinal de que foi
  ajustada à mão: reaproveite a forma, não os números.

## 4. Dados oficiais e patch notes

- Patch notes (notas de cada atualização) costumam trazer o valor antes e depois ("de 50 para 45")
  e às vezes o motivo, que mostra a intenção do designer. Lembre que o valor base muda de versão
  para versão.
- Alguns estúdios publicam dados de mecânica, guias oficiais ou blogs de desenvolvimento. Um
  desenvolvedor defende que publicar dados oficiais tira dos jogadores a necessidade de extraí-los.
- Se o jogo tem ferramenta oficial de mod (editor ou SDK), comece por ela: ela abre os dados do
  jeito que o estúdio permite.

## 5. Código liberado

| Projeto | O que tem | Condição |
|---|---|---|
| Quake (github.com/id-Software/Quake) | código do motor e do jogo (winquake, glquake, quakeworld) | GPL; o README avisa: "All of the Quake data files remain copyrighted" |
| Doom | código liberado pela id em 1997 | os dados do jogo continuam protegidos |
| Prince of Persia, Apple II (github.com/jmechner/Prince-of-Persia-Apple-II) | código original recuperado (publicado em 2012) e um documento técnico de 1989 | disponível para estudo, sem licença de código aberto; a franquia é da Ubisoft |
| Wikipedia, "List of commercial video games with available source code" | dezenas de jogos comerciais | arte e dados muitas vezes têm licença diferente da do código |

- Código liberado tem comentários e nomes reais: mostra a intenção, coisa que código decompilado
  nunca mostra.
- Ler é livre. Copiar trecho de código GPL para o seu jogo obriga o seu jogo a seguir a GPL, o que
  inclui distribuir o código-fonte. Para jogo fechado, estude e reescreva.

## 6. Decompilações comunitárias

- Super Mario 64 (github.com/n64decomp/sm64) e Ocarina of Time (github.com/zeldaret/oot) têm o
  código reconstruído a partir do jogo, com nomes e documentação feitos pela comunidade. Nenhum dos
  dois inclui assets, e para montar o jogo é preciso ter a própria cópia.
- São boas para ler a lógica de clássicos (física de pulo, câmera, inimigos) com nomes legíveis.
- O código reconstruído reproduz o original: trate-o como código do dono do jogo. Estude e
  reescreva; não copie para o seu jogo.
- Nem todo projeto assim é tolerado: as decompilações re3 e reVC, de GTA, receberam pedido de
  remoção (DMCA) em 2021 e foram processadas pela Take-Two; o caso terminou em acordo em 2023.

## 7. Projetos de exemplo das engines

| Engine | Projeto | Licença | Bom para estudar |
|---|---|---|---|
| Godot | demos oficiais (github.com/godotengine/godot-demo-projects) | MIT: pode reaproveitar mantendo o aviso de licença | demos 2D e 3D por tema, várias jogáveis no navegador |
| Unity | Boss Room (github.com/Unity-Technologies/com.unity.multiplayer.samples.coop) | Unity Companion License (verificado em 2026-10-11) | RPG cooperativo feito como amostra de rede: habilidades, latência, RPC; Unity 6000.0 LTS (verificado em 2026-10-11) |
| Unreal | Lyra Starter Game, no Fab | termos da página do item no Fab | sistema de habilidades (Gameplay Ability System), plugins modulares, multiplayer |

Lyra: no Fab, `Add to My Library`; depois, no Epic Games Launcher, vá em
`Unreal Engine › Library › Fab Library` e use `Create Project`. A amostra só aparece se a versão
compatível da engine estiver instalada.

## 8. Livros, palestras e análises

- *Game Programming Patterns* (Robert Nystrom), grátis em gameprogrammingpatterns.com: padrões que
  o autor encontrou ao abrir o código de jogos reais na EA.
- GDC Classic Game Postmortems: os criadores de Pac-Man, Doom, Prince of Persia, Maniac Mansion e
  Another World contam como fizeram. Essas palestras ficaram grátis no GDC Vault em 2011; se
  continuam grátis hoje não foi conferido.
- Game Maker's Toolkit (Mark Brown, YouTube): análises de como mecânicas e fases funcionam.
- Raph Koster, "How I analyze a game" (Game Developer, 2014): deixe de lado a própria experiência,
  olhe as mecânicas centrais e pergunte o que o designer queria.
- MIT CMS.301: descreva 6 a 8 mecânicas de forma abstrata o bastante para reaproveitar em outro jogo.

## 9. Clonar para aprender: o formato do 20 Games Challenge

O 20 Games Challenge (20_games_challenge.gitlab.io) compara clonar jogos a copiar uma obra-prima
numa aula de arte: é treino deliberado dos fundamentos.

- Meta: aprender em até 20 jogos e terminar pelo menos 10, começando por Pong.
- Cada jogo da lista traz objetivos de aprendizado, uma Definition of Done (a lista do que precisa
  funcionar para o jogo contar como terminado), metas extras e notas de complexidade e escopo.
- Pong, por exemplo: Definition of Done com arena, raquetes, bola, pontuação e placar; metas extras
  com adversário controlado pelo computador que erra às vezes, menu e sons.
- Se até Pong for grande demais, divida mais: uma mecânica por vez. Em Flappy Bird, primeiro a bola
  que cai e pula, depois o fundo que rola, depois os canos.
- Use o mesmo formato em "Passo 5 — Protótipo de uma mecânica" do SKILL.md.

## 10. Normas da comunidade

- O conhecimento circula, os arquivos do jogo não. A id separou motor e dados no Doom (arquivos WAD)
  para que mods circulassem sem os dados originais; as decompilações não distribuem assets; o Quake
  liberou o código, não os dados.
- Muitas comunidades de datamining deixam discutir achados, mas proíbem postar arquivos extraídos.
  O r/ffxiv, por exemplo, proíbe postar músicas extraídas, a pedido do diretor de som do jogo.
- Vazamento de conteúdo ainda não lançado tem etiqueta própria (aviso de spoiler, tópico separado).
  Estudar um jogo lançado que você comprou é outro caso.
- Publique análises, gráficos, tabelas recalculadas e o seu código. Não publique arquivos, músicas,
  modelos nem texturas do jogo.
- Modding é caminho de carreira: na CD Projekt Red, metade da equipe de quests da sequência de
  Cyberpunk veio do modding, e Counter-Strike, Dota e DayZ começaram como mods.

## Fontes

[Stardew Valley Wiki: Skills](https://stardewvalleywiki.com/Skills) ·
[id-Software/Quake](https://github.com/id-Software/Quake) ·
[Prince of Persia](https://github.com/jmechner/Prince-of-Persia-Apple-II) ·
[lista da Wikipedia](https://en.wikipedia.org/wiki/List_of_commercial_video_games_with_available_source_code) ·
[n64decomp/sm64](https://github.com/n64decomp/sm64) ·
[zeldaret/oot](https://github.com/zeldaret/oot) ·
[re3/reVC](https://torrentfreak.com/take-two-dismisses-claims-against-lead-defendants-in-gta-mods-lawsuit-230405) ·
[demos do Godot](https://github.com/godotengine/godot-demo-projects) ·
[Boss Room](https://github.com/Unity-Technologies/com.unity.multiplayer.samples.coop) ·
[Lyra](https://dev.epicgames.com/documentation/en-us/unreal-engine/lyra-sample-game-in-unreal-engine) ·
[Game Programming Patterns](https://gameprogrammingpatterns.com/) ·
[GDC Classic Postmortems](https://www.gamedeveloper.com/business/gdc-vault-debuts-classic-postmortem-videos-gdc-2011-lectures) ·
[Raph Koster](https://www.gamedeveloper.com/design/how-i-analyze-a-game) ·
[MIT CMS.301](https://ocw.mit.edu/courses/cms-301-introduction-to-game-design-methods-spring-2016/resources/mitcms_301s16_assigment2) ·
[20 Games Challenge](https://20_games_challenge.gitlab.io/challenge/) ·
[datamining e dados oficiais (YouTube)](https://www.youtube.com/watch?v=ErTIurGxGv4) ·
[modding (Wikipedia)](https://en.wikipedia.org/wiki/Video_game_modding) ·
[CD Projekt Red (TechRadar)](https://www.techradar.com/gaming/consoles-pc/half-of-the-quest-team-for-cyberpunk-2-are-former-modders-says-cd-projekt-red-lead)
