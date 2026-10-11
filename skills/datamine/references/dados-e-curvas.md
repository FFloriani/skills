# Dados e curvas

Como levar tabelas extraídas de um jogo para CSV, descobrir se há uma fórmula por trás delas e
recalcular os números para o jogo do usuário mantendo só a forma.

## Sumário

1. Status dos números
2. Onde as tabelas costumam estar
3. Converter para CSV
4. Curva com chaves: amostre, não ajuste
5. Ajustar curvas com `scripts/ajustar_curva.py`
6. Caso resolvido: XP de Stardew Valley
7. Drop rate e sorteio com pesos
8. Fórmulas de dano: ordem das operações
9. Inteiro, float e arredondamento
10. Recalcular para o jogo do usuário

## 1. Status dos números

Use os status do Passo 3 do SKILL.md também para dados:

| Situação | Status |
|---|---|
| Valor lido no arquivo extraído (tabela, JSON, ScriptableObject) | `confirmado` (cite arquivo e caminho dentro dele) |
| Fórmula achada por ajuste de curva; número tirado de dica, interface ou wiki | `inferido` |
| Tabela achada pelo nome ou arquivo, mas não aberta | `localizado-não-expandido` |
| Número contado ou cronometrado no jogo | `medido-jogando` |

Um valor `confirmado` na tabela não diz como o jogo o usa. Isso só fica `confirmado` lendo o
código que consome a tabela.

## 2. Onde as tabelas costumam estar

`scripts/identificar_engine.py` já lista os `.json`, `.csv`, `.tsv`, `.xml`, `.ini`, `.db` e `.sqlite`
soltos que encontrar. Trabalhe sempre na cópia em `estudo/<jogo>/`.

| Engine | Onde ficam os dados | Como abrir (só leitura) |
|---|---|---|
| Unity | ScriptableObject (arquivo de dados que o designer cria no editor) e MonoBehaviour dentro de `*.assets` e bundles; TextAsset (JSON, CSV ou XML embutido); arquivos soltos em `<Jogo>_Data/StreamingAssets/` | AssetRipper 2.0.0 (verificado em 2026-10-11) exporta o projeto; UnityPy 1.25.4 (verificado em 2026-10-11) para script |
| Unreal | DataTable (tabela com uma linha por nome), CurveTable e CurveFloat, dentro dos `.pak`/`.utoc` | FModel aug-2026 (verificado em 2026-10-11): exportar como Properties (.json) |
| Godot | Resources `.tres`/`.res` e JSON dentro do `.pck` | GDRE Tools 2.7.4 (verificado em 2026-10-11) converte recursos binários de volta para texto, com saída em `estudo/<jogo>/` |
| GameMaker | dentro do `data.win`; às vezes JSON, INI ou CSV incluídos ao lado dele | UndertaleModTool 0.9.2.0 (verificado em 2026-10-11), sem salvar |
| Ren'Py | valores nos scripts `.rpy` | unrpyc 2.0.4 (verificado em 2026-10-11) nos `.rpyc`; antes, extraia o `.rpa` com unrpa 2.3.0 (verificado em 2026-10-11), que só extrai |
| RPG Maker MV/MZ | `data/*.json` (no MV, `www/data/`): Actors, Classes, Skills, Items, Enemies e outros | editor de texto; são JSON puros |
| Qualquer uma | `.json`, `.csv`, `.xml`, `.ini`, `.db`/`.sqlite` soltos | leitura direta; SQLite com o `sqlite3` do Python |

UnityPy: fixe a versão (`pip install UnityPy==1.25.4`), porque uma versão nova, mesmo pequena, pode
mudar a API. Use só as funções de leitura do exemplo da seção 3; não use `save()` nem `patch()`, que gravam.

## 3. Converter para CSV

- Uma linha por entrada (item, nível, inimigo) e uma coluna por campo, com os nomes originais
  dos campos, para conferir com o arquivo depois.
- Salve em `estudo/<jogo>/tabelas/` e anote no `estudo/<jogo>/DIARIO.md` a origem de cada CSV:
  arquivo, caminho dentro dele, ferramenta e versão.
- Para abrir no Excel em português, grave com `encoding="utf-8-sig"` e, se quiser, `delimiter=";"`.
  `scripts/ajustar_curva.py` lê `,`, `;` e tab e aceita vírgula decimal.

JSON para CSV (lista de objetos ou objeto de objetos; campos aninhados viram `pai.filho`):

```python
# uso: python json_para_csv.py entrada.json saida.csv
import csv, json, sys

def achatar(d, prefixo=""):
    out = {}
    for k, v in d.items():
        if isinstance(v, dict):
            out.update(achatar(v, f"{prefixo}{k}."))
        else:
            out[f"{prefixo}{k}"] = json.dumps(v, ensure_ascii=False) if isinstance(v, list) else v
    return out

with open(sys.argv[1], encoding="utf-8-sig") as f:
    dados = json.load(f)
if isinstance(dados, dict):   # {"Linha_1": {...}, "Linha_2": {...}}
    linhas = [{"linha": k, **achatar(v)} for k, v in dados.items() if isinstance(v, dict)]
else:                         # [{...}, {...}]
    linhas = [achatar(v) for v in dados if isinstance(v, dict)]
campos = list(dict.fromkeys(k for l in linhas for k in l))
with open(sys.argv[2], "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, campos)
    w.writeheader()
    w.writerows(linhas)
```

- Os JSON do RPG Maker começam com `null` (o índice 0 fica vazio); o filtro `isinstance` já ignora.
- O JSON de um DataTable exportado pelo FModel costuma trazer as linhas num objeto de objetos
  (procure uma chave como `Rows`). Confira no arquivo e aponte o script para esse objeto, por
  exemplo `dados = dados[0]["Rows"]`.

SQLite para CSV, abrindo em modo só leitura:

```python
import csv, os, sqlite3
db = "estudo/<jogo>/copia/dados.db"
os.makedirs("estudo/<jogo>/tabelas", exist_ok=True)
con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
for (tabela,) in con.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall():
    cur = con.execute(f'SELECT * FROM "{tabela}"')
    with open(f"estudo/<jogo>/tabelas/{tabela}.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow([c[0] for c in cur.description])
        w.writerows(cur)
```

Se aparecer `file is not a database`, o arquivo está cifrado ou não é SQLite: siga a regra de
arquivo cifrado em "Escopo e limites" do SKILL.md.

ScriptableObject e MonoBehaviour da Unity para JSON com UnityPy (ScriptableObjects são gravados
como MonoBehaviour):

```python
import json, pathlib, re, UnityPy
env = UnityPy.load("estudo/<jogo>/copia/resources.assets")
saida = pathlib.Path("estudo/<jogo>/tabelas/monobehaviours")
saida.mkdir(parents=True, exist_ok=True)
for obj in env.objects:
    if obj.type.name != "MonoBehaviour":
        continue
    try:
        d = obj.parse_as_dict()
    except Exception:
        continue  # sem type tree (a descrição dos campos)
    nome = re.sub(r'[<>:"/\\|?*]', "_", d.get("m_Name") or "sem_nome")
    # path_id identifica o objeto dentro do arquivo: anote-o como fonte no DIARIO.md
    (saida / f"{nome}_{obj.path_id}.json").write_text(
        json.dumps(d, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
```

Se quase tudo cair no `except`, o arquivo não traz a type tree. Exporte com o AssetRipper, que
tenta montar os campos a partir do código do jogo. Se ainda aparecer "Unreadable" (comum em
IL2CPP, o tipo de build da Unity em que o C# vira código nativo), siga o arquivo de referência
de IL2CPP indicado no Passo 1 do SKILL.md.

## 4. Curva com chaves: amostre, não ajuste

Muitos jogos guardam a progressão como curva editável, não como fórmula:

- Unity `AnimationCurve`: lista de chaves com `time`, `value`, `inSlope` e `outSlope`.
- Unreal `CurveFloat` e `CurveTable`: chaves com `Time`, `Value` e modo de interpolação
  (constante, linear ou cúbica).

Nesse caso a curva já é a resposta (`confirmado`): copie as chaves para o CSV (x = time, y = value,
mais tangentes e modo). Para ter o valor em cada nível inteiro, avalie a curva com a mesma
interpolação ou meça jogando. Ajustar uma fórmula por cima só perde precisão.

## 5. Ajustar curvas com `scripts/ajustar_curva.py`

Termos:
- **Resíduo**: valor real menos valor previsto pela curva.
- **R²** (coeficiente de determinação): quanto da variação a curva explica. 1 = passa por todos
  os pontos; perto de 0 = não explica nada.

Comandos:

```bash
python scripts/ajustar_curva.py 100 380 770 1300 2150          # só y; x = 1, 2, 3...
python scripts/ajustar_curva.py 0:5 1:10 2:20 3:40             # pares x:y
python scripts/ajustar_curva.py estudo/<jogo>/tabelas/xp.csv --x nivel --y xp
```

O script mostra, nesta ordem:

1. **Incrementos e razões.** Incremento constante = reta. Incremento que cresce sempre a mesma
   quantidade = quadrática. Razão entre incrementos constante = exponencial. Saltos irregulares =
   tabela feita à mão.
2. **Três modelos**, cada um com fórmula, versão para código, R², maior resíduo e resíduo por ponto:
   - exponencial `y = a · b^x`: cada passo multiplica por `b` (comum em XP de RPG);
   - potência `y = a · x^b`: a razão entre níveis cai com o tempo;
   - quadrática `y = c2·x² + c1·x + c0`: o incremento cresce em passos iguais. Se `c2` sair 0,
     a tabela é uma reta.
3. **Veredito.** Aceita um modelo só com R² >= 0,99 e todos os resíduos <= 10% do valor real
   (mude com `--r2-min` e `--residuo-max`). Senão, conclui "tabela ajustada à mão / por partes" e,
   com 8 pontos ou mais, procura uma quebra em dois trechos.

Leia o R² junto com o resíduo em %. O R² é dominado pelos valores grandes do fim da tabela; um erro
enorme no nível 1 passa despercebido, e o começo do jogo é onde o jogador mais sente.

Antes de ajustar, confirme se a tabela é acumulada (total até o nível) ou por nível (o que falta
para o próximo). Na dúvida, ajuste as duas.

A fórmula ajustada é `inferido`. Ela só vira `confirmado` se aparecer no código ou nos dados.

## 6. Caso resolvido: XP de Stardew Valley

A Stardew Valley Wiki (página "Skills") publica o XP acumulado das habilidades nos níveis 1 a 10:
100, 380, 770, 1300, 2150, 3300, 4800, 6900, 10000 e 15000.

```bash
python scripts/ajustar_curva.py 100 380 770 1300 2150 3300 4800 6900 10000 15000
```

Trecho da saída:

```
[exponencial]  y = 127,9 · 1,657^x   (+65,7% por passo de x)
  R² = 0,8618   maior resíduo: -4923,1 em x=10   maior resíduo %: 111,9%
[potência]  y = 83,26 · x^2,122
  R² = 0,9175   maior resíduo: 3961,3 em x=10   maior resíduo %: 26,4%
[quadrática]  y = 240,9·x² - 1172·x + 1644
  R² = 0,9854   maior resíduo: 992,1 em x=10   maior resíduo %: 613,0%
3) Veredito
   Nenhum modelo chega a R² >= 0,99 com resíduo <= 10% em todos os pontos
   (o melhor foi quadrática: R² 0,9854, maior resíduo 613,0%).
   Conclusão provável: tabela ajustada à mão / por partes. Reaproveite a forma,
   não os números.
   Indício de trechos: quebra entre x=4 e x=5; potência no 1º trecho (y = 101,7 · x^1,848),
   exponencial no 2º (y = 324,1 · 1,467^x); R² combinado 0,9998, maior resíduo 3,6%.
   Com poucos pontos por trecho isto é só uma pista, não uma prova.
```

Como ler:
- O nível 1 custa 100; os incrementos seguintes são 280, 390, 530, 850, 1150, 1500, 2100, 3100 e
  5000. Do nível 3 em diante, a razão entre incrementos seguidos varia de 1,30 a 1,61 sem padrão
  (do 1 para o 2 o salto é 2,8×), então não é exponencial pura.
- A exponencial prevê 19.923 no nível 10 e a potência, 11.039, contra 15.000 reais.
- A quadrática tem o maior R² (0,985) e mesmo assim erra o nível 1 em 613% (prevê 713, o real é
  100). É o exemplo de por que o R² sozinho engana.
- A quebra entre os níveis 4 e 5 encaixa bem, mas o primeiro trecho tem só 4 pontos: é pista, não prova.
- Conclusão: **tabela ajustada à mão** (status `inferido`). Achar a tabela literal nos dados ou no
  código a torna `confirmado`.
- Forma que pode ir para outro jogo: a partir do nível 3, o custo de cada nível cresce de 30% a 60%
  sobre o anterior, o último degrau é o maior e o total até o nível máximo é cerca de 150 vezes o
  custo do primeiro nível. Os números, não.

## 7. Drop rate e sorteio com pesos

- **Drop rate**: chance de um item cair.
- **Tabela de pesos**: lista de resultados com um peso cada; probabilidade = peso ÷ soma dos pesos.

Descubra qual estrutura o código usa antes de calcular:

| Estrutura | Como funciona | Como reconhecer no código |
|---|---|---|
| Sorteio único com pesos | sai exatamente um resultado (muitas vezes com uma entrada "nada") | soma dos pesos, um número aleatório entre 0 e a soma, laço que acumula pesos até passar o número |
| Chance independente por item | cada item rola sozinho; podem cair vários ou nenhum | um teste `aleatorio < chance` por item dentro do laço |

Anote também: quantos sorteios por inimigo, quantidade mínima e máxima, modificadores (sorte,
dificuldade) e garantia contra azar (contador que força o item depois de N falhas). Colunas
sugeridas para o CSV: `tabela, resultado, peso, probabilidade, qtd_min, qtd_max, condicao`.

Contas para explicar ao usuário:
- Com chance `p` por tentativa, a média é `1/p` tentativas. Com `p` = 2%, a média é 50.
- Chance de ter pelo menos um em `n` tentativas = `1 − (1 − p)^n`. Com `p` = 2%: 63,6% em 50
  tentativas e 86,7% em 100. "Em média 50" não quer dizer "garantido em 50".

Cuidados ao ler:
- Limites do sorteio. Na Unity, `Random.Range(0, 100)` com inteiros devolve de 0 a 99 (o máximo
  fica de fora); a versão com float inclui os dois extremos. Trocar `<` por `<=` muda a chance em
  1 ponto. Copie o teste exato para a ficha.
- A porcentagem da interface pode não ser a da conta. Um datamine de Palworld relatado na
  comunidade (r/Palworld) achou, no bytecode (código compilado) de um Blueprint (script visual do
  Unreal), um multiplicador constante de 1,25 entre a taxa real de captura e a exibida. Trate número
  de interface como `inferido`.

## 8. Fórmulas de dano: ordem das operações

Registre os passos na ordem do código. Uma lista do que procurar (a ordem real é a do código):
valor base (atributo × multiplicador da habilidade) → bônus somados → bônus multiplicados →
defesa ou resistência → crítico → variação aleatória → limites (mínimo 1, teto) → arredondamento.

A ordem muda o resultado. Ataque 100, bônus fixo +20, multiplicador ×1,5, defesa 30:
- (100 + 20) × 1,5 − 30 = **150**
- 100 × 1,5 + 20 − 30 = **140**
- (100 + 20 − 30) × 1,5 = **135**

Bônus percentuais também: +10% e +20% somados dão ×1,30; multiplicados, 1,1 × 1,2 = ×1,32.

Formas comuns de defesa, para reconhecer (não para supor): subtração com mínimo
(`ataque − defesa`, nunca abaixo de 1), razão (`dano × 100 / (100 + defesa)`) e porcentagem com teto.

Exemplo real em código aberto (licença MIT): no RPG Maker MV, `Game_Action.makeDamageValue`
(repositório rpgtkoolmv/corescript, consultado em 2026-10-11) faz, nesta ordem:
1. avalia a fórmula da habilidade, que é texto no campo `damage.formula` de `data/Skills.json`,
   e trava o resultado em no mínimo 0 (em habilidade de cura, troca o sinal para negativo);
2. multiplica pela taxa do elemento;
3. multiplica pela taxa de dano físico ou mágico do alvo (`pdr` ou `mdr`), e por `rec` se for cura;
4. crítico: multiplica por 3;
5. variação: amplitude = parte inteira de |dano| × variância ÷ 100; soma dois sorteios inteiros
   de 0 até a amplitude e subtrai a amplitude. O resultado fica entre −amplitude e +amplitude,
   com o centro mais provável (dois sorteios somados não dão chances iguais);
6. guarda: se o alvo está defendendo e o dano é positivo, divide por 2 × `grd`;
7. arredonda (`Math.round`) só no final.

Num jogo RPG Maker, ler a fórmula no `Skills.json` é `confirmado` para aquela habilidade.

## 9. Inteiro, float e arredondamento

- Divisão de inteiros corta a parte decimal: em C#, `7 / 2` dá 3 e `-7 / 2` dá -3. `(int)2.9f` dá 2.
- O ".5" muda por linguagem. C# `Math.Round` e Unity `Mathf.RoundToInt` levam ao par mais próximo
  (2,5 → 2; 3,5 → 4). JavaScript `Math.round` sobe (2,5 → 3; −2,5 → −2). GDScript `round` se
  afasta do zero (2,5 → 3; −2,5 → −3).
- O momento do arredondamento muda o resultado. Base 10 com dois bônus de ×1,15, cortando para
  inteiro a cada passo: 10 → 11 → 12. Cortando só no fim: 10 × 1,15 × 1,15 = 13,2 → 13.
- Float tem erro de representação: 0,1 + 0,2 não dá exatamente 0,3. Não compare floats com `==`.
- Constantes podem vir pré-calculadas. Uma `const` do C# aparece como número solto no código
  decompilado, e o compilador de IL2CPP ou C++ pode juntar contas: um 0,75 no pseudo-C (código
  aproximado que o Ghidra mostra para código nativo) pode ser 1,5 × 0,5 no fonte. Anote o número como aparece e marque a origem dele como `inferido`.

Na ficha A do Passo 4 do SKILL.md, mantenha os mesmos tipos, a mesma ordem, os mesmos
arredondamentos e os mesmos limites do original.

## 10. Recalcular para o jogo do usuário

Do original vai a forma: quanto cresce por nível, onde a curva quebra, o teto, a proporção entre
começo e fim. Os números são recriados (veja "O que vai para o jogo do usuário" no SKILL.md).
Multiplicar a tabela original por uma constante não é recalcular: cada número continua derivado do
original. Gere os números a partir dos alvos do jogo do usuário:

1. Descreva a forma em parâmetros, não em tabela. Exemplo do caso 6: "cada nível custa de 30% a 60%
   a mais que o anterior; último degrau maior".
2. Defina os alvos do jogo dele: número de níveis, quanto XP o jogador ganha por dia ou por sessão,
   em quanto tempo deve chegar ao máximo. Exemplo: 8 níveis, cerca de 150 XP por dia, nível
   máximo em uns 60 dias, total de 9.000 XP.
3. Gere a tabela com esses alvos:

   ```python
   # Distribui um total de XP em n níveis; cada incremento é r vezes o anterior.
   total, n, r = 9000, 8, 1.4      # alvos do jogo do usuário; r vem da forma estudada
   inc1 = total * (r - 1) / (r ** n - 1)
   acumulado, xp = 0.0, []
   for k in range(n):
       acumulado += inc1 * r ** k
       xp.append(10 * round(acumulado / 10))   # números redondos
   print(xp)  # [260, 630, 1140, 1860, 2860, 4270, 6240, 9000]
   ```

4. Para um último degrau maior, aumente só o último incremento e confira o total.
5. Rode `scripts/ajustar_curva.py` na tabela nova para ver se a forma saiu como planejado.
6. Teste jogando (Passo 5 do SKILL.md) e ajuste.
7. Registre no `DIARIO.md` de onde veio a forma e por que cada parâmetro mudou.

O mesmo vale para os outros sistemas:
- **Drop:** mantenha a estrutura (pesos, garantia contra azar) e escolha a chance pelo alvo
  "quantas tentativas em média": `p = 1 / média`.
- **Dano:** mantenha a ordem dos passos e escolha as constantes pelo alvo "quantos golpes para
  derrotar um inimigo do mesmo nível".
