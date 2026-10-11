# Outras engines e arquivos de dados

Detalhe da linha "`.pck`, `data.win`, `.rpa`/`.rpyc`, `www/js` + `data/`, `app.asar`, `.love`" do
Passo 1 do SKILL.md, mais arquivos de configuração genéricos. Tudo segue a seção "Escopo e limites"
do SKILL.md: copie o que for estudar para `estudo/<jogo>/copia/`, use só modos de leitura e
exportação, mande toda saída para `estudo/<jogo>/` e nunca grave na pasta do jogo.

Nas engines desta página, quase sempre o código volta inteiro (bytecode ou texto puro): ler o corpo
de uma função dá status `confirmado`. A exceção é o GameMaker YYC.

## Sumário

1. Primeiro olhar: os bytes do começo do arquivo
2. Godot
3. GameMaker
4. Ren'Py
5. RPG Maker MV/MZ
6. Electron, NW.js e HTML5
7. LÖVE
8. Configurações e dados genéricos
9. Fontes

## 1. Primeiro olhar: os bytes do começo do arquivo

A extensão engana; os primeiros bytes (a "assinatura") dizem o formato. Veja numa cópia:

```
python -c "import sys; print(open(sys.argv[1], 'rb').read(16))" "estudo/<jogo>/copia/<arquivo>"
```

| Começa com | Formato |
|---|---|
| `PK\x03\x04` | zip (`.love`, `package.nw` e muitos formatos próprios) |
| `GDPC` | pacote do Godot (`.pck`) |
| `AKPK` | pacote de som do Wwise (também `.pck`, mas é áudio, não Godot) |
| `FORM` | `data.win` do GameMaker |
| `RPA-3.0`, `RPA-2.0` | arquivo `.rpa` do Ren'Py |
| `RPGMV` | imagem ou som cifrado do RPG Maker |
| `SQLite format 3` | banco SQLite |
| `UnityFS` | bundle da Unity: siga a linha da Unity no Passo 1 do SKILL.md |
| `\x1bLJ` | bytecode do LuaJIT |
| `\x1bLua` | bytecode do Lua |

## 2. Godot

**Reconhecer**
- `<Jogo>.pck` ao lado do `<Jogo>.exe`, começando com `GDPC`; ou nenhum `.pck` e um `.exe` grande
  (o pacote vai embutido no executável).
- Pasta `data_<Jogo>_...` com DLLs ao lado do `.exe`: jogo Godot escrito em C#.

**Ferramenta padrão:** GDRE Tools 2.7.4 (verificado em 2026-10-11), lançada em 2026-10-11, MIT.
Há também a 2.8.0-beta.1 (verificado em 2026-10-11). Lê Godot 2, 3 e 4.
- Interface: menu **RE Tools** > **Recover project...**, ou arraste o `.pck`/`.exe` da cópia para a
  janela. Escolha `estudo/<jogo>/projeto/` como destino.
- Linha de comando:
  `gdre_tools --headless --recover=estudo/<jogo>/copia/<Jogo>.pck --output=estudo/<jogo>/projeto`.
  Passe sempre `--output`; sem ele, a ferramenta escolhe o destino sozinha.

**O que vem:** recuperação completa do projeto. Scripts GDScript decompilados, o `project.godot`,
recursos convertidos de volta ao formato original de importação e ao formato de texto, e as
configurações de plugins. `--translation-hint` ajuda a recuperar traduções. Em jogo C#, a DLL é
detectada sozinha (ou informe `--csharp-assembly=<caminho>`) e também abre no ILSpy.
Abra o projeto recuperado no editor do Godot da mesma versão do jogo: dá para rodar cenas,
inspecionar nós e ler no Inspector os valores exportados, que viram números `confirmado`.

**O que se perde:** comentários e formatação podem não voltar quando os scripts foram exportados
compilados; scripts exportados como texto voltam como estavam.

**Armadilhas**
- Revisão de bytecode do GDScript diferente da esperada: `--force-bytecode-version` ou
  `--load-custom-bytecode`. Erro de checksum: `--ignore-checksum-errors` ou `--skip-checksum-check`.
- `.pck` cifrado precisa da chave: 64 caracteres hexadecimais, passada com `--key=`. Ela fica no
  executável do próprio jogo. Decifrar a cópia para leitura está no escopo; avise uma vez, como pede
  "Escopo e limites" no SKILL.md. Projetos cifrados só abrem direito a partir da 2.7.4.
- O projeto recuperado é o jogo inteiro. Fica em `estudo/`, fora de qualquer repositório público
  (atenção a quem versiona o estudo no GitHub).

**Não use (grava arquivos):** `--pck-create`, `--pck-patch`, `--patch-file`, `--embed` e `--key`
junto deles (que cifra). Nunca grave um `.pck` de volta no jogo.

## 3. GameMaker

**Reconhecer:** `data.win` ao lado do `.exe` (começa com `FORM`), muitas vezes com `options.ini` e
`audiogroup1.dat`. Duas formas de build:
- **VM**: o GML (linguagem do GameMaker) vira bytecode dentro do `data.win`. O código volta.
- **YYC** (YoYo Compiler): o GML vira código nativo dentro do `.exe`. Só os assets voltam.

**Ferramenta padrão:** UndertaleModTool (UTMT) 0.9.2.0 (verificado em 2026-10-11), lançado em
2026-08-23, GPL-3.0; já lê os betas do GameMaker 2026.1.
- **File** > **Open** > `estudo/<jogo>/copia/data.win`.
- Lista **Code**: entradas como `gml_Script_<nome>` e `gml_Object_<objeto>_<Evento>_<n>` (ex.:
  `gml_Object_obj_player_Step_0` é o evento Step do objeto `obj_player`, que roda a cada frame).
  Clique para ver o GML decompilado.
- Exportar em lote: **Scripts** > **Resource Exporters** > `ExportAllCode.csx` (pede uma pasta:
  escolha `estudo/<jogo>/gml/`), `ExportAllSprites.csx`, `ExportAllSounds.csx`,
  `ExportAllStringsJSON.csx`, `ExportAllRoomsToPNG.csx`.

**O que vem:** em VM, GML decompilado, objetos com seus eventos, salas (rooms), sprites, sons e
textos. Em YYC, só os assets; o `ExportAllCode.csx` avisa "The opened game uses YYC: no code is
available." Aí a lógica fica `inferido` ou `medido-jogando`.

**O que se perde:** comentários; `#macro` e `enum` viram números soltos, porque o compilador troca o
nome pelo valor. O decompilador ainda falha em alguns recursos de GML.

**Armadilhas**
- Número solto no código pode ser um valor de enum; não trate como "número mágico" do designer.
- GML de versão nova (ex.: template strings `$"{x}"`) pede UTMT atualizado.

**Não use (grava arquivos):** **File** > **Save** (sobrescreve o `data.win`), editar ou compilar
código, scripts de **Resource Importers** e scripts que alteram dados. Ao fechar, não salve.

## 4. Ren'Py

**Reconhecer:** pastas `game/`, `renpy/` e `lib/`; arquivos `.rpa` (pacote), `.rpyc`/`.rpymc`
(scripts compilados). Às vezes os `.rpy` (fonte) já vêm junto: leia direto. Traduções ficam em
`game/tl/<idioma>/`. Versão: `lib/py3-...` costuma indicar Ren'Py 8; `lib/py2-...` ou
`lib/windows-i686`, Ren'Py 7 ou 6.

**Ferramentas padrão**
- `.rpa` → unrpa 2.3.0 (verificado em 2026-10-11), release de 2019, GPL-3.0, Python 3.7+. Só extrai,
  e lê RPA-1.0 a RPA-4.0 e variantes.
  `py -3 -m pip install unrpa`, depois
  `unrpa -mp estudo/<jogo>/extraido estudo/<jogo>/copia/game/archive.rpa`.
  Alternativa: rpatool (repositório arquivado em 2022), só com `-l` (listar) e `-x` (extrair).
- `.rpyc` → unrpyc 2.0.4 (verificado em 2026-10-11) para Ren'Py 8 até 6.18, com Python 3.9+; para
  Ren'Py 7 e 6, unrpyc 1.3.2 (verificado em 2026-10-11), com Python 2.7.
  `python <pasta-do-unrpyc>/unrpyc.py estudo/<jogo>/extraido`. Ele grava cada `.rpy` ao lado do
  `.rpyc`; por isso roda sobre a pasta extraída, nunca sobre `game/` do jogo.

**O que vem:** o roteiro `.rpy`: labels, menus de escolha, diálogos, variáveis (`$ afeto += 1`),
blocos Python e telas (screen language, o layout da interface).

**O que se perde:** comentários. O `init offset` é adivinhado; em jogos anteriores ao Ren'Py 6.99.10,
use `--no-init-offset`.

**Armadilhas**
- Versão do unrpyc trocada falha ou gera saída errada: confira a versão do Ren'Py antes.
- `-t <idioma>` reescreve os diálogos com a tradução de `game/tl`; `-d` mostra a árvore crua.
- Diálogos e textos se recriam, nunca se portam (tabela "O que vai para o jogo do usuário" no SKILL.md).

**Não use (grava arquivos):** os injetores (`un.rpyc`, `un.rpy`, `bytecode-39.rpyb`), que são
copiados para `game/` e rodam dentro do jogo; rpatool `-c`, `-a` e `-d` (criam, acrescentam e apagam
dentro do `.rpa`); unrpyc `-c`/`--clobber` numa pasta que já tem `.rpy` original (sobrescreve).

## 5. RPG Maker MV/MZ

**Reconhecer**
- MV: pasta `www/` com `index.html`, `js/`, `data/`, `img/`, `audio/`; núcleo em `js/rpg_*.js`
  (`rpg_objects.js`, `rpg_managers.js`...).
- MZ: `js/`, `data/` e `img/` direto na raiz; núcleo em `js/rmmz_*.js`.
- Os dois rodam em NW.js (`nw.dll` e `package.json` ao lado do `.exe`).

**Ferramenta padrão:** leitura direta da cópia num editor de texto (VS Code, por exemplo).

**O que vem:** tudo em texto puro.
- `data/*.json`, o banco de dados: `Actors`, `Classes` (`params` = atributos por nível;
  `expParams` = parâmetros da curva de XP), `Skills` (`damage.formula` = a fórmula de dano escrita
  como expressão JavaScript, ex.: `a.atk * 4 - b.def * 2`), `Items`, `Weapons`, `Armors`, `Enemies`
  (`dropItems` com `denominator`: chance de 1 em `denominator`), `Troops`, `States`, `System` e
  `MapNNN.json` (eventos de cada mapa).
- `js/`: a lógica do núcleo (dano em `Game_Action`, ex.: `evalDamageFormula` e `makeDamageValue`;
  curva de XP em `Game_Actor.prototype.expForLevel`) e os plugins em `js/plugins/*.js`, com a lista
  e os parâmetros dos ativos em `js/plugins.js`.

**O que se perde:** nada no código. Plugins podem vir minificados ou ofuscados, e a mídia pode vir
cifrada.

**Armadilhas**
- Plugins sobrescrevem funções do núcleo (padrão
  `const _Game_Action_apply = Game_Action.prototype.apply;` seguido de uma nova versão). Antes de
  marcar uma fórmula do núcleo como `confirmado`, procure o nome da função em `js/plugins/` e
  confira em `js/plugins.js` se o plugin está ativo.
- `damage.formula` é só o começo: variação, crítico, defesa e elementos entram depois, no núcleo.
- Mídia cifrada: `.rpgmvp` (png), `.rpgmvo` (ogg) e `.rpgmvm` (m4a) no MV; `.png_`, `.ogg_` e
  `.m4a_` no MZ. A chave fica em `data/System.json`, campo `encryptionKey` (no MV,
  `www/data/System.json`). Decifrar a cópia para leitura está no escopo; avise uma vez, como pede
  "Escopo e limites" no SKILL.md. Ferramenta: rmvdec 2.2.0 (verificado em 2026-10-11), de 2023,
  BSD-3-Clause, feita para MV e que também reconhece `.png_`. Informe sempre a pasta de saída:
  `rmvdec estudo/<jogo>/copia/img estudo/<jogo>/midia/img -r -k estudo/<jogo>/copia/data/System.json`.
  Arte e som abertos são referência de estudo, não asset do jogo do usuário.
- Sem `www/` nem `data/` visíveis, o jogo pode estar empacotado dentro do `.exe`. Veja os bytes do
  começo (seção 1); se não reconhecer o formato, pare e ofereça as alternativas (wiki, medição jogando).

**Não use (grava arquivos):** `rmvdec -rm` (apaga os originais depois de decifrar); ferramentas que
"restauram o projeto" gravando na pasta do jogo; o editor do RPG Maker sobre qualquer coisa que não
seja a cópia.

## 6. Electron, NW.js e HTML5

**Reconhecer**
- Electron: `resources/app.asar` (ou a pasta `resources/app/`) e arquivos do Chromium ao lado do
  `.exe` (`chrome_100_percent.pak`, `ffmpeg.dll`, `v8_context_snapshot.bin`, `LICENSES.chromium.html`).
- NW.js: `nw.dll` e `package.json` ou `package.nw` (que é um zip). RPG Maker MV/MZ: seção 5.

**Ferramenta padrão:** `@electron/asar` 4.3.1 (verificado em 2026-10-11), o pacote oficial do
Electron; precisa do Node.js.
- Listar: `npx @electron/asar list estudo/<jogo>/copia/resources/app.asar`
- Extrair: `npx @electron/asar extract estudo/<jogo>/copia/resources/app.asar estudo/<jogo>/app`
- Copie também `app.asar.unpacked/`, se existir: são arquivos guardados fora do pacote.
- `package.nw`: abra como zip.

**O que vem:** HTML, JavaScript, CSS, assets e JSON de dados. O nome dos arquivos JS revela a engine:
`c3runtime.js` (Construct 3), `phaser*.js` (Phaser), `pixi*.js` (PixiJS).

**O que se perde:** em código minificado, os nomes locais e a formatação. Formate a cópia com
`npx prettier --write "estudo/<jogo>/app/**/*.js"`. Um `.js.map` com `sourcesContent` traz o fonte
original: leia esse primeiro.

**Armadilhas**
- Código empacotado num arquivo só (webpack e similares): procure textos que aparecem na tela ou
  nomes de atributos (`damage`, `xp`) para achar a lógica.
- Arquivos `.jsc` são bytecode do V8 e não voltam a texto: marque a lógica
  `localizado-não-expandido` e meça jogando.

**Não use (grava arquivos):** `asar pack` e qualquer gravação em `resources/`.

## 7. LÖVE

**Reconhecer:** `love.dll`, `lua51.dll`, `SDL2.dll` e `OpenAL32.dll` ao lado do `.exe`, ou um
arquivo `.love`. O `.exe` "fundido" é o `love.exe` com o zip do jogo colado no fim; por isso abre
como zip.

**Ferramenta padrão:** 7-Zip (abra o `.love` ou o `.exe` da cópia como arquivo compactado) ou Python:
`python -m zipfile -e estudo/<jogo>/copia/<Jogo>.exe estudo/<jogo>/src`.

**O que vem:** o código Lua (`main.lua`; `conf.lua` traz a versão do LÖVE em `t.version`) e os assets.

**O que se perde:** nada, se o Lua vier em texto. Se o arquivo começar com `\x1bLJ` (bytecode
LuaJIT) ou `\x1bLua` (bytecode Lua), o texto não volta direto: marque a lógica
`localizado-não-expandido` e meça jogando.

**Não use (grava arquivos):** refundir o executável (`copy /b love.exe+jogo.love`) ou gravar
qualquer coisa no `.exe`.

## 8. Configurações e dados genéricos

**Onde procurar:** `data/`, `config/`, `.ini` ao lado do `.exe`; configurações e saves do usuário
em `%APPDATA%`, `%LOCALAPPDATA%` ou `Documentos/My Games`. Copie para `estudo/<jogo>/copia/` antes de
abrir. Save se lê, não se edita. `StreamingAssets/` é da Unity: siga a linha da Unity no Passo 1 do
SKILL.md.

| Formato | Como abrir só para leitura | Armadilhas |
|---|---|---|
| JSON | VS Code; `python -m json.tool arquivo.json` imprime formatado | número guardado como texto; IDs que apontam para outra tabela |
| CSV / TSV | editor de texto primeiro; no Excel, **Dados** > **De Texto/CSV**, com as colunas como texto | Excel em português usa `;` e vírgula decimal: `1.25` vira data ou 125 |
| XML, YAML, INI | editor de texto | comentários no próprio arquivo às vezes explicam valores |
| SQLite (`.db`, `.sqlite`) | DB Browser for SQLite em modo somente leitura; `sqlite3 -readonly arquivo.db`; Python `sqlite3.connect("file:arquivo.db?mode=ro", uri=True)` | abrir em modo normal pode criar `-journal` ou `-wal` e alterar o arquivo |
| Tabelas de localização | `.locres` do Unreal (FModel), `game/tl/<idioma>/` do Ren'Py, `.translation` do Godot (GDRE recupera), CSV ou JSON de textos | texto se recria, não se porta; as chaves (ex.: `ITEM_ESPADA_DESC`) revelam a estrutura |
| Binário desconhecido | bytes do começo (seção 1) | não tente "consertar" nem regravar |

**Confira a escala dos números antes de usar:** porcentagem pode estar em 0–1, 0–100 ou 0–10000
(10000 = 100%); valores inteiros podem ser ponto fixo (1000 = 1,0); tempo pode estar em frames
(60 = 1 s a 60 fps), milissegundos ou segundos. Compare com uma medição no jogo (`medido-jogando`).

**O que se perde:** a intenção do designer. A tabela mostra o número, não por que ele foi escolhido
nem como o código o usa.

**Não use (grava arquivos):** "Salvar" do Excel sobre o CSV original (muda separador, decimais e
datas), banco SQLite aberto em modo de escrita, editor que reformata o arquivo ao salvar. Trabalhe
sempre em outra cópia dentro de `estudo/<jogo>/`.

**Status:** o valor lido na tabela é `confirmado`. Como o jogo usa o valor (a fórmula) depende de
ler o código; sem isso, a fórmula fica `inferido`. Registre cada fato em `estudo/<jogo>/DIARIO.md`.

## 9. Fontes

Verificadas em 2026-10-11.

- GDRE Tools: https://github.com/GDRETools/gdsdecomp
- UndertaleModTool: https://github.com/UnderminersTeam/UndertaleModTool
- unrpyc: https://github.com/CensoredUsername/unrpyc
- unrpa: https://github.com/Lattyware/unrpa
- rpatool (arquivado): https://github.com/shizmob/rpatool
- rmvdec: https://github.com/Bioruebe/rmvdec
- @electron/asar: https://github.com/electron/asar
- LÖVE, distribuição de jogos: https://love2d.org/wiki/Game_Distribution
