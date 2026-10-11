# Missões, diálogos e mapas: onde achar e como documentar

## Sumário
1. Onde ficam missões e diálogos
2. Onde ficam as posições do mundo
3. Coordenadas: local, mundo e eixos
4. Ficha de missão
5. Pontos de mapa
6. Catálogo: "o que faz" e "onde consigo"

## 1. Onde ficam missões e diálogos

Procure primeiro por tabelas e pastas com nomes como Quest, Mission, Objective, Task, Journal,
Dialogue, Conversation, Story, Event, Flag, Switch, Trigger, e pelas chaves de localização dos
títulos das missões (o texto que aparece no diário leva ao ID da missão).

| Engine | Onde costuma estar |
|---|---|
| Unity | ScriptableObjects de missão; JSON/CSV em StreamingAssets; plugins de diálogo como Ink (história compilada em JSON), Yarn Spinner, Pixel Crushers Dialogue System (banco de diálogos e missões num asset) e Naninovel (scripts de texto). A lógica de condição fica no código (C# ou pseudo-C no IL2CPP). |
| Unreal | DataTables de missões e diálogos; Blueprints com a lógica (bytecode no .uasset, visível no FModel); assets de diálogo de plugins; gatilhos posicionados nos mapas `.umap`. |
| Godot | Recursos `.tres`, cenas `.tscn` e GDScript recuperados pelo GDRE; plugins de diálogo com arquivos próprios (ex.: Dialogic, Dialogue Manager). |
| RPG Maker MV/MZ | `data/MapXXX.json`: cada evento tem `x`, `y` (em tiles) e páginas com `conditions` (switch, variável, item, ator) e `list` de comandos. Códigos úteis: 101/401 mostrar texto, 102/402 escolhas, 111 condição, 121 switch, 122 variável, 125 ouro, 126 item, 201 teleporte, 301 batalha. Nomes de switches e variáveis em `data/System.json`; nomes dos mapas em `data/MapInfos.json`; eventos globais em `data/CommonEvents.json`. |
| Ren'Py | Scripts `.rpy` (ou `.rpyc` decompilados): `label`, `menu`, `jump`, `call`, `if` e as variáveis com `$`. A rota de cada final sai das condições. |
| GameMaker | Salas (rooms) com instâncias e posições; lógica em GML (build VM) exportada pelo UndertaleModTool. |

Missão costuma ser uma máquina de estados: estado inicial, objetivos, condições para avançar
(flag, item, morte de inimigo, entrar numa área), estados de falha e recompensas. Documente as
condições exatas, não a impressão que o texto do diário passa.

## 2. Onde ficam as posições do mundo

| Engine | Onde |
|---|---|
| Unity | Cenas (exportadas pelo AssetRipper como `.unity`, texto YAML): cada GameObject tem um Transform com `m_LocalPosition`, `m_LocalRotation`, `m_LocalScale` e `m_Father` (o pai). Também podem estar em tabelas de spawn. |
| Unreal | Mapas `.umap` no FModel: cada ator tem um componente raiz com `RelativeLocation`, `RelativeRotation` e `RelativeScale3D`. Mundos grandes no UE5 (World Partition) ficam divididos em células em pastas geradas; percorra todas. |
| Godot | Cenas `.tscn` em texto: `position` (2D) ou `transform` (3D) de cada nó, com o caminho do pai. |
| RPG Maker | `x`, `y` dos eventos em tiles (48 px por tile no MV e no MZ). |
| GameMaker | `x`, `y` das instâncias de cada sala, em pixels. |

## 3. Coordenadas: local, mundo e eixos

- A posição gravada costuma ser **local** (relativa ao pai). A posição no mundo é a composição de
  todos os pais: posição, rotação e escala. Somar só as posições só funciona se nenhum pai tiver
  rotação ou escala; confira antes.
- Eixos: Unity tem Y para cima (mapa visto de cima usa X e Z). Unreal tem Z para cima e unidades
  em centímetros (mapa usa X e Y). Godot 3D tem Y para cima; 2D tem Y para baixo, como Game Maker
  e RPG Maker.
- Para sobrepor ao minimapa do jogo, ache a textura do mapa e os limites que o jogo usa para
  convertê-la (costumam estar numa tabela ou no componente de minimapa). Sem isso, gere o mapa só
  com os pontos e diga que a escala é aproximada.
- Confira com dois ou três pontos conhecidos (um NPC famoso, o ponto de partida) antes de
  confiar no mapa inteiro.

## 4. Ficha de missão (`missoes/<id>-<nome>.md`)
```
# <Nome> (<id>) — versão <x.y.z>
Objetivo: <em uma frase>
Pré-requisitos: <nível, flags, missões anteriores, item>
Passos:
  1. <o que fazer> — onde: <região, coordenada, NPC> — avança quando: <condição exata>
  2. ...
Escolhas e consequências: <opção → flag → efeito>
Falha: <o que faz falhar e se dá para repetir>
Recompensas: <itens, XP, ouro, desbloqueios>
Fonte: <arquivo, evento ou método>
Status: confirmado | inferido | localizado-não-expandido | medido-jogando
```

## 5. Pontos de mapa (`mapas/<região>.csv`)
Colunas: `x,y,categoria,nome,descricao` (mais `z` se ajudar). Categorias sugeridas: npc, loja,
bau, inimigo, chefe, recurso, portal, missao, segredo. `x` e `y` já no plano do mapa visto de cima.
Gere o HTML com `scripts/mapa.py`: tem zoom, arrastar, filtro por categoria e busca por nome.

## 6. Catálogo: "o que faz" e "onde consigo"
- **O que faz**: siga o ID do item ou habilidade até a tabela de efeitos e resolva cada efeito em
  números. Descrições com marcadores (`{0}`, `%1`, `[Damage]`) são modelos: preencha com os valores
  da tabela para ter o texto exato que o jogo mostraria.
- **Onde consigo**: procure o ID nas tabelas de drop (com peso e chance), lojas (preço, condição
  para aparecer), recompensas de missão, receitas de criação e pontos fixos no mapa (baús).
  Escreva todas as fontes, não só a primeira.
