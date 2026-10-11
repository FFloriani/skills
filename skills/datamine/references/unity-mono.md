# Unity Mono: ler o código C# do jogo

Num build Mono, a Unity guarda o código do jogo como IL (a linguagem intermediária do .NET) dentro
de DLLs. Decompilar, isto é, converter esse IL de volta em C#, devolve as classes e o corpo dos
métodos, sem os comentários. É o caso mais fácil de estudar.

## Sumário

1. Confirmar que é Mono
2. Ferramenta padrão: ILSpy
3. O que sai e o que se perde
4. Onde ficam a lógica e os dados
5. Achar um sistema rápido
6. Armadilhas da decompilação
7. Nomes ofuscados
8. Da leitura para a ficha da mecânica

## 1. Confirmar que é Mono

Copie a pasta do jogo para `estudo/<jogo>/copia/` e confira os marcadores nela (ou rode
`scripts/identificar_engine.py`, como diz o Passo 1 do SKILL.md):

| Na cópia | Conclusão |
|---|---|
| `<Jogo>_Data/Managed/Assembly-CSharp.dll` | Mono: o código principal está aqui |
| pasta `MonoBleedingEdge/` na raiz | o runtime Mono está presente (reforça) |
| `GameAssembly.dll` na raiz e `<Jogo>_Data/il2cpp_data/` | não é Mono, é IL2CPP: volte à triagem do SKILL.md |

O manual da Unity só documenta o `GameAssembly.dll` dos builds IL2CPP; os outros caminhos são o
padrão conhecido na comunidade.

- Versão da Unity: botão direito em `UnityPlayer.dll` › Propriedades › Detalhes › Versão do produto.
- Outros DLLs com código do jogo: `Assembly-CSharp-firstpass.dll` (scripts das pastas Plugins e
  Standard Assets) e DLLs com o nome do jogo ou do estúdio (código dividido em módulos). Ignore
  `UnityEngine.*`, `Unity.*`, `System.*`, `Mono.*`, `mscorlib.dll` e `netstandard.dll` (engine e
  bibliotecas), a não ser para entender uma API.
- Se o ILSpy disser que o arquivo não é um assembly .NET válido, o DLL pode estar cifrado (alguns
  jogos usam um sistema anti-tamper, isto é, contra alteração). Se a proteção fizer parte de um
  anti-cheat ou o jogo for online, pare (SKILL.md, "Escopo e limites"). Em jogo single-player,
  decifrar uma cópia para leitura está no escopo: a rotina fica no código nativo do próprio cliente,
  então essa parte vira leitura no Ghidra 12.1.4 (verificado em 2026-10-11), um descompilador de
  código nativo gratuito. O resultado fica em `estudo/<jogo>/`; chave, arquivo aberto e script não
  são publicados.

## 2. Ferramenta padrão: ILSpy

ILSpy 11.1 (verificado em 2026-10-11): gratuito, de código aberto, só lê.

- Interface: File › Open › a cópia do `Assembly-CSharp.dll`. Deixe os outros DLLs de `Managed/` na
  mesma pasta, para os tipos da Unity serem resolvidos. A árvore da esquerda mostra namespaces ›
  classes › métodos; clique num item para ver o C#.
- Exportar tudo (melhor para buscar): selecione o assembly › File › Save Code › escolha
  `estudo/<jogo>/codigo/`. Sai um projeto `.csproj` com um arquivo `.cs` por classe.
- Linha de comando (para o Claude rodar; precisa do .NET SDK): instale com
  `dotnet tool install --global ilspycmd`, confirme as opções com `ilspycmd -h` e rode
  `ilspycmd -p -o "estudo/<jogo>/codigo" "estudo/<jogo>/copia/<Jogo>_Data/Managed/Assembly-CSharp.dll"`.
- Ver o IL de um método (quando o C# parecer errado): troque a linguagem na barra de ferramentas
  para "IL with C#".

Alternativa: dnSpyEx 6.6.0 (verificado em 2026-10-11), só para ler um método em que o ILSpy falhou.
Não use o editor (Edit Method, Edit IL Instructions, Save Module), que grava o DLL, nem o depurador,
que exige trocar o runtime Mono dentro da pasta do jogo (repositório à parte, dnSpy-Unity-mono).

## 3. O que sai e o que se perde

Sai:
- classes, campos, propriedades e métodos com corpo, com os nomes originais (se não houver ofuscação);
- literais: números, strings, valores de enum com nome;
- atributos: `[SerializeField]`, `[CreateAssetMenu]`, `[Range(0, 100)]`, `[Tooltip("...")]`,
  `[Header("...")]`. Tooltip e Header são o mais perto de um comentário do designer que sobra;
  Range mostra os limites que ele usava;
- tabelas escritas no código (arrays inicializados com valores).

Perde-se:
- comentários, formatação e `#region`;
- nomes de variáveis locais (viram `num`, `num2`, `flag`);
- nomes de constantes nos pontos de uso (viram número solto);
- às vezes a forma exata de corrotinas, `async`, lambdas e LINQ (seção 6);
- **os valores que o jogo usa de verdade nos campos serializados.** Eles ficam nos assets (prefab,
  cena, ScriptableObject), não no código. `public float speed = 5f;` só dá o valor padrão; o
  designer pode ter posto 7,5 no Inspector (o painel do editor da Unity onde se ajustam valores).

## 4. Onde ficam a lógica e os dados

Termos: **MonoBehaviour** é um script preso a um objeto da cena. **ScriptableObject** é um arquivo
de dados criado no editor (item, inimigo, tabela). **Campo serializado** é um campo `public` ou
`[SerializeField] private` que a Unity grava no asset e o designer ajusta no Inspector.

| Onde | O que costuma ter | Como ler |
|---|---|---|
| classes que herdam de `MonoBehaviour` | lógica por objeto: `Update`, `FixedUpdate`, `OnTriggerEnter`, `OnCollisionEnter` | ILSpy |
| classes que herdam de `ScriptableObject` (muitas com `[CreateAssetMenu]`) | definição de itens, armas, inimigos, níveis, drop | a classe no ILSpy; os valores nos assets |
| campos serializados | números de balanceamento | valor real no prefab, na cena ou no asset |
| `<Jogo>_Data/StreamingAssets/` | arquivos copiados como estão: JSON, CSV, XML, SQLite, bundles | abra direto (editor de texto, DB Browser for SQLite, Python) |
| `<Jogo>_Data/resources.assets` | o que o código carrega com `Resources.Load("caminho")` | busque `Resources.Load` no código para achar os caminhos |
| `StreamingAssets/aa/` (Addressables) | conteúdo carregado por chave: `Addressables.LoadAssetAsync<T>("chave")` | o catálogo liga cada chave a um bundle: `catalog.json`, ou `catalog.bin` (binário, padrão no Addressables 2.x) |
| `sharedassets*.assets`, `level*` | cenas, prefabs e os valores deles | extração de assets |
| TextAsset | JSON, CSV ou texto embutido num asset | campo `m_Script` |

Extração de assets:
- AssetRipper 2.0.0 (verificado em 2026-10-11) exporta o projeto inteiro (Unity 3.5 a 6000.4) para
  uma pasta que você escolhe: use `estudo/<jogo>/projeto/`. Num jogo Mono, ele lê os DLLs de
  `Managed/` e exporta MonoBehaviours e ScriptableObjects com os campos legíveis. A versão grátis
  serve para código e dados; a edição Premium, paga, acrescenta extras como decompilação de shader.
- UnityPy 1.25.4 (verificado em 2026-10-11) serve para scripts: `obj.parse_as_dict()` devolve os
  campos de um MonoBehaviour ou ScriptableObject. Fixe a versão (`pip install UnityPy==1.25.4`),
  porque a troca do segundo número (1.25 para 1.26) pode quebrar a API, e não use `patch()` nem
  `save()`, que gravam.

## 5. Achar um sistema rápido

Trabalhe no projeto exportado (`estudo/<jogo>/codigo/`) com busca de texto (`rg` ou Grep). No
ILSpy, use o painel de busca.

1. **Por nome.** Código de jogo costuma estar em inglês: `Damage`, `Hit`, `Crit`, `Health`, `Exp`,
   `Level`, `Drop`, `Loot`, `Rarity`, `Spawn`, `Wave`, `Price`, `Upgrade`, `Stat`, `Modifier`,
   `Formula`, `Calc`.
2. **Por string.** Um texto da tela, ou a chave de localização dele (`ui_crit_hit`), leva ao código
   que o mostra. Dali, suba até quem calcula o valor.
3. **Por campo serializado.** Os nomes de campo que aparecem nos assets extraídos (`baseDamage`,
   `critMultiplier`) são os mesmos do C#. Busque-os para achar a classe que os usa, e vice-versa.
4. **Pela engine.** Métodos que a Unity chama pelo nome (`Update`, `OnTriggerEnter2D`) e handlers
   de botão (`onClick.AddListener`) são boas portas de entrada.
5. **Siga as chamadas uns dois níveis.** No ILSpy, botão direito no método › Analyze: "Used By"
   mostra quem chama, "Uses" mostra o que ele chama; em campos, "Read By" e "Assigned By". Anote o
   caminho e só desça mais se a fórmula continuar lá embaixo.

Registre em `estudo/<jogo>/DIARIO.md` cada classe e método que fizer parte do sistema.

## 6. Armadilhas da decompilação

Código gerado pelo compilador não é decisão de design. Reconstrua a forma provável do fonte:

| O que aparece | O que era no fonte | O que fazer |
|---|---|---|
| classe `<Atacar>d__12` com `MoveNext()`, `<>1__state`, `<>2__current` | corrotina (método `IEnumerator` com `yield return`, que roda em etapas ao longo de vários frames) ou método `async` | O ILSpy costuma reconstruir. Se não, leia `MoveNext`: cada `case` do `switch` sobre `<>1__state` é o trecho entre dois `yield`, e `<>2__current = new WaitForSeconds(0.5f)` é a espera. Corrotinas às vezes saem erradas (há relato de erro com `IEnumerator` no dnSpyEx); na dúvida, confira no IL. |
| classe `<>c__DisplayClass5_0` com campos e métodos `<Metodo>b__0` | closure: lambda que usa variáveis locais do método | leia como uma lambda no ponto onde a classe é criada |
| classe `<>c` com campos `<>9__5_0` | lambda sem variáveis capturadas, guardada em cache | leia como lambda |
| número solto (`* 1.5f`) | constante `const`, embutida na compilação | procure na classe um `const` com o mesmo valor para dar nome; `static readonly` não é embutido e aparece como campo |
| `switch` sobre `ComputeStringHash(s)` com números grandes, seguido de `s == "fire"` | `switch` com muitos casos de string | os casos são as strings; os números são hash e podem ser ignorados |
| `<MaxHealth>k__BackingField` | campo escondido de uma propriedade automática (`public int MaxHealth { get; set; }`) | trate como a propriedade; nos assets, é o nome do campo quando há `[field: SerializeField]` |
| `<PrivateImplementationDetails>` com `InitializeArray` | array inicializado com valores no código | o ILSpy costuma mostrar `new int[] { ... }`; é uma tabela, leve para o estudo |
| `num`, `num2`, `flag` | variáveis locais com o nome perdido | renomeie nas suas notas |

Tipos e arredondamentos: preserve-os na ficha. `(int)x` corta a parte decimal, `Mathf.RoundToInt`
arredonda .5 para o inteiro par mais próximo, `Mathf.FloorToInt` arredonda para baixo, e `0.2f`
(float) não dá o mesmo resultado que `0.2` (double) nas contas.

## 7. Nomes ofuscados

Ofuscação é a troca, antes de publicar, dos nomes de classes, métodos e campos por nomes sem
sentido (o Beebyte Obfuscator é comum em Unity). Sinal: muitos nomes que são sequências aleatórias
de letras ou caracteres invisíveis. A lógica continua legível; só os nomes somem.

O que costuma sobreviver e serve de âncora:
- métodos que a Unity chama pelo nome (`Awake`, `Update`, `OnTriggerEnter2D` e cerca de sessenta outros);
- métodos que sobrescrevem ou implementam tipos da engine e de bibliotecas (`OnPointerClick`, de
  `IPointerClickHandler`);
- nomes de campos serializados, que os assets referenciam pelo nome;
- strings, nomes de parâmetros do Animator (`SetTrigger("Attack")`) e chamadas à API da Unity
  (`Random.Range`, `Mathf.Pow`, `Physics.Raycast`);
- tipos de DLLs que não foram ofuscados.

O que fazer:
1. Comece pelas âncoras e dê nomes provisórios às classes e aos métodos em volta.
2. Mantenha `estudo/<jogo>/nomes.md` no formato nome ofuscado › nome provisório › evidência.
   Renomeie só nas notas ou na sua cópia do código exportado, nunca no DLL.
3. Se o usuário tiver uma versão antiga sem ofuscação (demo, build anterior), compare as duas:
   assinaturas, strings e campos serializados iguais ajudam a casar os nomes.
4. Corpo cheio de `goto` e de `switch` sem sentido indica ofuscação de fluxo. Leia um método pequeno
   por vez, no IL se precisar, e marque o que não ficar claro como `localizado-não-expandido`.

Uma fórmula pode ser `confirmado` com nomes provisórios; diga na ficha que os nomes são seus.

## 8. Da leitura para a ficha da mecânica

Preencha a parte A da ficha (SKILL.md, Passo 4) assim:
- **Regra em palavras e fórmula matemática:** do corpo do método, com os nomes dos campos.
- **Trecho mínimo:** só as linhas da conta, com a mesma ordem de operações, os mesmos tipos, casts,
  `Mathf.Clamp`/`Min`/`Max` e arredondamentos. Corrotina vira linha do tempo (t = 0 s inicia a
  animação, t = 0,25 s liga a hitbox...).
- **Números:** do asset (prefab, cena, ScriptableObject), não do inicializador no código. Se só
  houver o valor do código, marque esse número como `inferido`, porque o asset pode sobrescrevê-lo.
- **Fonte:** DLL › `Namespace.Classe.Metodo` › arquivo e linha no projeto exportado; para números,
  o asset e o campo.
- **Status:** a regra é `confirmado` quando o corpo do método foi lido. Cada número leva o seu:
  `confirmado` se lido no asset, `inferido` se só veio do inicializador no código.

Exemplo (nomes inventados):

```text
A. Original (fiel)
Regra: o crítico multiplica o dano depois de subtrair a defesa; o mínimo é 1.
Fórmula: dano = trunc(max(1, (atk − def) × (crit ? critMult : 1)))
Código: int dmg = (int)Mathf.Max(1f, (atk - def) * (isCrit ? critMult : 1f));
Fonte: Assembly-CSharp.dll › Combat.DamageCalc.Compute (codigo/Combat/DamageCalc.cs:41);
       critMult = 1.5 em dados/Balance.asset, campo critMultiplier
Status: confirmado (corpo lido; valor lido no asset)
```

As partes B (redesenho) e C (como testar) seguem o SKILL.md.
