# Unreal Engine 4 e 5

Detalhe da linha "Unreal" do Passo 1 do SKILL.md. Tudo aqui segue a seção "Escopo e limites" do
SKILL.md: cópia em `estudo/<jogo>/`, só modos de leitura e exportação, nada gravado na pasta do
jogo, só jogos single-player ou offline.

## Sumário

1. Reconhecer o jogo
2. O que volta e o que não volta
3. Preparar a cópia
4. FModel (ferramenta padrão)
5. Mapeamento `.usmap`
6. `.pak` cifrado
7. DataTable para JSON e CSV
8. CurveTable e curvas
9. Lógica: Blueprint ou C++
10. Preencher a ficha
11. Armadilhas
12. Padrões antigos
13. Fontes

## 1. Reconhecer o jogo

Dois destes marcadores bastam:

- `<Jogo>/Binaries/Win64/<Jogo>-Win64-Shipping.exe`: o executável de verdade. O `.exe` da raiz
  costuma ser só um lançador pequeno.
- `<Jogo>/Content/Paks/*.pak`: pacotes onde o Unreal guarda os assets (asset = qualquer conteúdo:
  modelo, textura, som, tabela).
- `.utoc` + `.ucas` ao lado dos `.pak`: formato IoStore. O `.utoc` é o índice, o `.ucas` guarda os
  dados. É o padrão no UE5; alguns jogos UE4 recentes também usam.
- Pasta `Engine/` na raiz do jogo.

Versão da engine (o FModel precisa dela): botão direito no `-Shipping.exe` > Propriedades >
Detalhes. "Versão do arquivo" costuma trazer a versão da engine (ex.: `5.3.2`). Se não trouxer,
teste versões próximas no FModel: versão errada dá erro ao abrir ou propriedades sem sentido.

## 2. O que volta e o que não volta

| Parte do jogo | Onde fica | O que você recebe |
|---|---|---|
| DataTables, CurveTables, curvas soltas (`CurveFloat`) | `.uasset` dentro dos paks | JSON com todos os valores |
| Valores padrão de personagens e componentes (velocidade, pulo, vida) | Blueprint da classe | JSON |
| Lógica feita em Blueprint | bytecode Kismet dentro do `.uasset` | pseudo C++ ou lista de instruções |
| Lógica feita em C++ | `-Shipping.exe` | só pseudo-C no Ghidra, devagar |
| Textos e traduções | `.locres` | JSON |
| Configurações | `<Jogo>/Config/*.ini` dentro dos paks | texto |
| Modelos, texturas, animações, sons | `.uasset` / `.ubulk` | arquivos exportados (referência de estudo) |

Blueprint é a linguagem visual de scripts do Unreal. No jogo pronto, cada Blueprint vira bytecode
(instruções para uma máquina virtual, bem mais fáceis de ler que código de máquina). Comentários e
nomes de variáveis locais do C++ nunca voltam.

## 3. Preparar a cópia

1. Copie a pasta `<Jogo>/Content/Paks/` inteira (com `global.utoc` e `global.ucas`, se existirem)
   para `estudo/<jogo>/copia/Paks/`. Costuma ter dezenas de GB: confira o espaço livre antes.
2. Crie `estudo/<jogo>/fmodel/` para as exportações e `estudo/<jogo>/DIARIO.md`.
3. Copie o jogo inteiro só se for gerar `.usmap` (seção 5).

## 4. FModel (ferramenta padrão)

FModel aug-2026 (verificado em 2026-10-11), lançado em 2026-08-02, licença GPL-3.0. Lê e exporta;
não grava nos paks. Baixe em `github.com/4sval/FModel/releases`. Se não abrir, instale o .NET
Desktop Runtime 10 (o projeto mira .NET 10; verificado em 2026-10-11).

Configuração, uma vez por jogo:

1. Na primeira abertura, o FModel sugere jogos que achou instalados. Não use essa sugestão, que
   aponta para a instalação: adicione manualmente a pasta `estudo/<jogo>/copia/Paks`.
2. Escolha a versão em **UE Versions** (ex.: `GAME_UE5_3` para um jogo em 5.3).
3. Em **Settings**, aponte **Output Directory** e os diretórios de exportação (**Save Properties
   Directory**, **Save Texture Directory**, **Export Raw Data Directory**, **Save Audio Directory**)
   para `estudo/<jogo>/fmodel/`.
4. Para estudar Blueprint, ligue **Serialize Script Bytecode** e **Decompile Blueprint to Pseudo
   C++** (seção 9).
5. Carregue os pacotes. Pacote que não carrega por estar cifrado precisa de chave (seção 6).
   Propriedades vazias ou erro citando mappings pedem `.usmap` (seção 5).

Exportar: botão direito no asset > **Export**.

- **Properties (.json)**: tabelas, curvas, Blueprints, configs. É o que o estudo de design mais usa.
- **Texture**, **Model**, **Animation**, **Audio**: assets, só como referência de estudo (veja "O
  que vai para o jogo do usuário" no SKILL.md).
- **Raw Data (.uasset)**: o arquivo cru, para o kismet-analyzer (seção 9).
- **Decompile Blueprint** (direto no menu do botão direito, quando ligado): pseudo C++ de um Blueprint.

Duplo clique num asset mostra o JSON sem exportar. Exporte só as pastas que vai estudar: o jogo
inteiro em JSON ocupa muito espaço e demora.

## 5. Mapeamento `.usmap`

O `.usmap` guarda os nomes e os tipos das propriedades. Muitos jogos (sobretudo UE5) gravam as
propriedades "sem versão", sem esses nomes; sem o `.usmap`, o FModel não consegue lê-las.

1. Procure primeiro um `.usmap` publicado pela comunidade de modding do jogo, para a mesma versão
   do jogo que você tem.
2. Se não houver e o jogo for single-player ou offline, gere com o UE4SS numa cópia.

O UE4SS é **injetado**: carrega código dentro do processo do jogo enquanto ele roda. Por isso: só
jogo single-player ou offline, só na cópia, nunca em jogo online ou com anti-cheat (dá banimento e
está fora do escopo). Última versão estável: v3.0.1, de 2024-02-14 (verificado em 2026-10-11). O
repositório segue ativo e as builds `experimental-latest` acompanham versões novas da engine (o
README atual fala em UE 4.7 a 5.8); para UE5 recente, use a experimental.

1. Copie a pasta inteira do jogo para `estudo/<jogo>/copia-completa/`.
2. Extraia o pacote `zDEV-UE4SS` em `copia-completa/<Jogo>/Binaries/Win64/`, ao lado do
   `-Shipping.exe`. Ficam ali um `dwmapi.dll` e os arquivos do UE4SS. O pacote zDEV já abre o
   console gráfico.
3. Abra o `-Shipping.exe` da cópia e entre num mapa jogável, no modo offline.
4. Gere o arquivo: aba **Dumpers** > botão de gerar `.usmap`, ou `Ctrl` + `Numpad 6`. Sai um
   `Mappings.usmap`; procure na pasta do `-Shipping.exe` da cópia ou na pasta do UE4SS.
5. Feche o jogo, mova o `Mappings.usmap` para `estudo/<jogo>/` e, no FModel, ligue **Local
   Mapping File** em **Settings** e aponte **Mapping File Path** para ele.

Se a loja abrir a versão instalada em vez da cópia, pare. Não instale o UE4SS na pasta original:
fique com um `.usmap` da comunidade ou com os assets que abrem sem mapeamento. Do UE4SS, use só os
dumpers; a parte de edição de propriedades e os mods Lua/C++ alteram o jogo em execução e ficam de
fora.

## 6. `.pak` cifrado

Alguns jogos cifram os paks com uma chave AES: uma sequência de 64 caracteres hexadecimais,
normalmente escrita com `0x` na frente. Decifrar uma cópia para leitura está no escopo; avise o
usuário uma vez do risco legal, como pede a seção "Escopo e limites" do SKILL.md.

O passo a passo completo (diagnóstico, ordem para conseguir a chave, validação, mapeamentos e o que
fazer quando nada funciona) está em `references/chaves-aes.md`. Resumo:

- A chave costuma ser publicada pela comunidade de modding daquele jogo. Se não for, ela está no
  executável do cliente, e há scanners locais que leem uma cópia do `-Shipping.exe` e listam chaves
  candidatas.
- Não use serviço online que pede o executável (o AESDumpster 1.3 "Online Version" funciona assim):
  nada do jogo sai da máquina.
- No FModel, cole a chave em **Directory** > **AES**.
- Se a chave for aceita e os arquivos continuarem ilegíveis, o estúdio modificou a engine e o
  FModel não a suporta. Pare e ofereça alternativas: dados publicados, wiki, medição jogando.
- Não publique a chave, os arquivos abertos nem ferramentas.

## 7. DataTable para JSON e CSV

DataTable é uma tabela com uma linha por item (arma, inimigo, nível) e colunas definidas por uma
struct (o conjunto de campos). Nomes costumam começar com `DT_`.

1. Ache a tabela com a busca de pacotes do FModel e dê duplo clique para conferir o conteúdo.
2. Botão direito > **Export** > **Properties (.json)**.
3. O JSON é uma lista de exports. A tabela é o que tem `"Rows"`:
   `[{"Type": "DataTable", "Name": "DT_Armas", "Rows": {"Rifle_01": {"BaseDamage": 25, ...}}}]`
4. Converta com o script abaixo (Python 3, sem pacotes extras). Grave em `estudo/<jogo>/scripts/`
   e rode `python datatable_para_csv.py DT_Armas.json DT_Armas.csv --excel-br`.

```python
# datatable_para_csv.py: JSON de DataTable exportado pelo FModel -> CSV
import csv, json, re, sys

entrada, saida = sys.argv[1], sys.argv[2]
excel_br = "--excel-br" in sys.argv  # decimal com vírgula para o Excel em português
dados = json.load(open(entrada, encoding="utf-8"))
exports = dados if isinstance(dados, list) else [dados]
tabela = next(e for e in exports if isinstance(e, dict) and "Rows" in e)

def achatar(valor, prefixo=""):
    if isinstance(valor, dict):
        itens = {}
        for k, v in valor.items():
            k = re.sub(r"_\d+_[0-9A-Fa-f]{32}$", "", k)  # sufixo de struct criada em Blueprint
            itens.update(achatar(v, f"{prefixo}{k}."))
        return itens
    if isinstance(valor, list):
        return {prefixo[:-1]: json.dumps(valor, ensure_ascii=False)}
    if excel_br and isinstance(valor, float):
        valor = str(valor).replace(".", ",")
    return {prefixo[:-1]: valor}

linhas = [{"RowName": nome, **achatar(campos)} for nome, campos in tabela["Rows"].items()]
colunas = list(dict.fromkeys(c for linha in linhas for c in linha))
with open(saida, "w", newline="", encoding="utf-8-sig") as f:
    escritor = csv.DictWriter(f, fieldnames=colunas, delimiter=";")
    escritor.writeheader()
    escritor.writerows(linhas)
print(f"{len(linhas)} linhas, {len(colunas)} colunas -> {saida}")
```

Como ler o resultado:

- Sufixo `_12_<32 hexadecimais>` no nome do campo: struct criada em Blueprint. O script remove.
- Valor `NewEnumerator3`: enum criado em Blueprint. O nome legível está no asset do enum (exporte o
  JSON dele).
- Campo com `ObjectName` / `ObjectPath`: referência a outro asset.
- Campo com `SourceString`: texto exibido no jogo. Texto se recria, não se porta.
- Campo com `DataTable` + `RowName` ou `CurveTable` + `RowName`: aponta para a linha de outra tabela.

## 8. CurveTable e curvas

- **CurveTable**: cada linha é uma curva com chaves `Time` (eixo X: nível, segundos) e `Value`.
  `CurveTableMode` diz se é `SimpleCurves` ou `RichCurves`. Numa RichCurve, cada chave tem modo de
  interpolação e tangentes, e o valor entre duas chaves depende disso.
- **CurveFloat**: curva solta, usada por Timelines (arco de pulo, recuo de arma, fade). As chaves
  ficam em `FloatCurve` > `Keys`.
- **ScalableFloat** (do Gameplay Ability System): campo com `Value` e `Curve` (`CurveTable` +
  `RowName`). O valor final é `Value` × valor da curva no nível.

Script para levar as chaves a CSV (os nomes dos campos podem variar entre versões do FModel; abra o
JSON e ajuste se precisar):

```python
# curva_para_csv.py: CurveTable ou CurveFloat exportado pelo FModel -> CSV (curva, Time, Value)
import csv, json, sys

dados = json.load(open(sys.argv[1], encoding="utf-8"))
exports = dados if isinstance(dados, list) else [dados]
with open(sys.argv[2], "w", newline="", encoding="utf-8") as f:
    escritor = csv.writer(f)
    escritor.writerow(["curva", "Time", "Value"])
    for e in exports:
        curvas = dict(e.get("Rows") or {})
        if "FloatCurve" in e.get("Properties", {}):
            curvas[e.get("Name", "curva")] = e["Properties"]["FloatCurve"]
        for nome, curva in curvas.items():
            for chave in curva.get("Keys", []):
                escritor.writerow([nome, chave.get("Time"), chave.get("Value")])
```

As chaves são o dado confirmado. Se quiser uma fórmula que gere a curva, ajuste e mostre os resíduos;
muitas curvas foram desenhadas à mão e não têm fórmula.

## 9. Lógica: Blueprint ou C++

**Blueprint.** O bytecode fica no `.uasset` da classe (nomes `BP_...`; a classe gerada termina em
`_C`).

1. Padrão: botão direito > **Decompile Blueprint**. Sai um pseudo C++ legível, bom para entender o
   fluxo.
2. Para confirmar um número: **Properties (.json)** com **Serialize Script Bytecode** ligado. Cada
   função traz `ScriptBytecode`, a lista de instruções (`EX_...`) com os literais exatos.
3. Para ver o fluxo como grafo: kismet-analyzer, release `latest` de 2026-01-11 (verificado em
   2026-10-11), MIT. Sobre o Raw Data exportado: `kismet-analyzer cfg <caminho>/BP_Arma.uasset`
   abre o grafo de uma classe no navegador; `kismet-analyzer gen-cfg-tree <pasta> <saida> <Projeto>`
   faz o mesmo para uma pasta e gera a hierarquia de classes (`<Projeto>`, pelo exemplo do README,
   é o nome interno do projeto; `--render` precisa do Graphviz no PATH). Ele pode não ler pacotes IoStore; nesse caso fique com os passos 1 e 2. A ferramenta
   também se descreve como capaz de manipular bytecode: use só os comandos de análise.

O pseudo C++ e o grafo não são o Blueprint original e não voltam a ser um Blueprint editável com
fidelidade. Quando o bytecode chama uma função nativa, ele mostra só a chamada; o corpo está no
`.exe`.

**C++.** Fica compilado no `-Shipping.exe`, sem símbolos.

- Nomes de classes, campos e offsets: dumpers do UE4SS na mesma sessão da seção 5 (`Ctrl` + `H`
  gera headers C++; `Ctrl` + `Numpad 9` gera headers no formato UHT; `Ctrl` + `J` grava
  `UE4SS_ObjectDump.txt`). Isso dá o layout das classes, não o corpo das funções.
- Corpo da função: só como pseudo-C no Ghidra 12.1.4 (verificado em 2026-10-11), abrindo uma cópia
  do `.exe`. Achar uma função específica num executável sem símbolos é trabalho lento e avançado.
  Para quem está começando: anote classe e função, marque `localizado-não-expandido` e meça jogando.
- Não escreva corpo de função C++ que não foi lido.

## 10. Preencher a ficha

Use o formato do Passo 4 do SKILL.md. O status depende de onde veio cada fato:

| Origem do fato | Status |
|---|---|
| Valor lido em DataTable, CurveTable ou JSON de Blueprint | `confirmado` (o valor) |
| Fórmula lida no pseudo C++ do Blueprint ou no `ScriptBytecode` | `confirmado` |
| Fórmula deduzida de nome de coluna, de função ou de texto do jogo | `inferido` |
| Função C++ achada no dump, corpo não lido | `localizado-não-expandido` |
| Tempo, distância ou dano medidos no jogo | `medido-jogando` |

Exemplo fictício da parte A (Original, fiel):

- Regra: o dano do tiro é o dano base da arma, multiplicado no acerto crítico.
- Fórmula: `dano = BaseDamage × (crítico ? CritMultiplier : 1)`.
- Dados: `DT_Armas`, linha `Rifle_01`: `BaseDamage = 25`, `CritMultiplier = 1.5`.
- Fonte: `<Jogo>/Content/Data/DT_Armas.uasset` (linha `Rifle_01`); conta em `BP_Arma_C`, função
  `CalcularDano` (pseudo C++ do FModel).
- Status: valores `confirmado`; fórmula `confirmado` (bytecode lido). Se a conta estivesse numa
  função C++ não lida, a fórmula seria `localizado-não-expandido`.

Na parte B (redesenho), leve a estrutura (dano base por arma, multiplicador de crítico) e recalcule
os números para o jogo do usuário. Registre cada fato confirmado em `estudo/<jogo>/DIARIO.md`.

## 11. Armadilhas

- **Versão errada em UE Versions**: erros ao abrir ou valores sem sentido. Teste versões vizinhas.
- **Sem `.usmap`** em jogo com propriedades sem versão: tabelas vazias ou erro. Veja a seção 5.
- **Campo ausente no JSON**: o valor é o padrão da classe, não zero. Só se grava o que difere do
  padrão. Exemplo: um personagem sem `JumpZVelocity` no JSON usa o padrão do
  `CharacterMovementComponent` no código-fonte da engine (420).
- **Unidades do Unreal**: centímetros, cm/s, graus e segundos. Converta antes de portar.
- **Valor da tabela ≠ valor final**: o código pode somar buffs, dificuldade ou nível por cima.
  Confirme a fórmula antes de chamar o número de "dano real".
- **Tabelas compostas** (`CompositeDataTable`, `CompositeCurveTable`) juntam várias tabelas, e a
  ordem das tabelas-pai decide qual valor vale.
- **Sugestão automática do FModel** aponta para a pasta instalada. Use a cópia.

## 12. Padrões antigos

- **UE Viewer / UModel**: último release `ue4.27`, de 2021-12-17 (verificado em 2026-10-11). Cobre
  UE1 a UE4, não UE5. Ainda aparece em tutoriais antigos; prefira o FModel.
- **AESDumpster 1.3 "Online Version"**: envia o executável para um site. Não use (seção 6).

## 13. Fontes

Verificadas em 2026-10-11.

- FModel: https://github.com/4sval/FModel e release https://github.com/4sval/FModel/releases/tag/aug-2026
- RE-UE4SS: https://github.com/UE4SS-RE/RE-UE4SS e dumpers https://docs.ue4ss.com/dev/feature-overview/dumpers.html
- kismet-analyzer: https://github.com/trumank/kismet-analyzer
- CUE4Parse (formato do JSON do FModel): https://github.com/FabianFG/CUE4Parse
- IoStore (`.utoc`/`.ucas`): https://dev.epicgames.com/documentation/en-us/unreal-engine/zen-loader-in-unreal-engine
- Ghidra: https://github.com/NationalSecurityAgency/ghidra/releases/tag/Ghidra_12.1.4_build
- UE Viewer: https://github.com/gildor2/UEViewer
