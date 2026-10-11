# Unity IL2CPP: ler um jogo compilado para código nativo

No backend IL2CPP, a Unity converte o C# em C++ e compila tudo para código de máquina. Os nomes de
classes, métodos e campos ficam num arquivo à parte, o `global-metadata.dat`. A lógica fica em
`GameAssembly.dll` e só pode ser lida como pseudo-C: um C aproximado que um descompilador de código
nativo, como o Ghidra, gera a partir do código de máquina.

## Sumário

1. Confirmar que é IL2CPP
2. O que o dump.cs e as DummyDll são e não são
3. Ferramentas padrão
4. Ler a lógica no Ghidra
5. Ruído do pseudo-C do IL2CPP
6. Status das afirmações
7. global-metadata.dat cifrado
8. Dados: AssetRipper, "unreadable" e type trees
9. Padrões antigos
10. Da leitura para a ficha da mecânica

## 1. Confirmar que é IL2CPP

Copie a pasta inteira do jogo para `estudo/<jogo>/copia/` e confira os marcadores nela (ou rode
`scripts/identificar_engine.py`, como diz o Passo 1 do SKILL.md):

| Na cópia | Conclusão |
|---|---|
| `GameAssembly.dll` na raiz | o código do jogo, compilado para código nativo |
| `<Jogo>_Data/il2cpp_data/Metadata/global-metadata.dat` | nomes, tipos e strings |
| nenhum `<Jogo>_Data/Managed/Assembly-CSharp.dll` | confirma que não é Mono |

O manual da Unity (página de arquivos do build IL2CPP para Windows, verificado em 2026-10-11)
descreve o `GameAssembly.dll` como a biblioteca com o runtime do IL2CPP e todo o código dos
scripts; o caminho do `global-metadata.dat` é o padrão conhecido na comunidade. Em Android,
`libil2cpp.so` ocupa o lugar de `GameAssembly.dll`, e o metadata fica em
`assets/bin/Data/Managed/Metadata/`.

- Versão da Unity: botão direito em `UnityPlayer.dll` › Propriedades › Detalhes › Versão do produto.
- Versão do metadata (decide qual ferramenta consegue ler):

  ```
  python -I -c "d=open('estudo/<jogo>/copia/<Jogo>_Data/il2cpp_data/Metadata/global-metadata.dat','rb').read(8); print(d[:4].hex(' '), int.from_bytes(d[4:8],'little'))"
  ```

  A saída normal é `af 1b b1 fa` seguido da versão (29, 31, 39, 104...). Se os 4 primeiros bytes
  forem outros, o metadata está cifrado ou alterado (seção 7).

## 2. O que o dump.cs e as DummyDll são e não são

- `dump.cs`: um arquivo de texto com todas as classes, campos e métodos do jogo, gerado pelo
  Il2CppDumper (seção 9); o Redux gera um índice parecido em C#. Costuma passar de 10 MB; busque com
  `scripts/buscar_no_dump.py` (SKILL.md, Passo 2) em vez de ler tudo.
- DummyDll (ou DLLs "shim"): DLLs .NET com os mesmos nomes, que abrem no ILSpy, mas com os métodos
  vazios.

São um **índice**:
- nomes de namespaces, classes, métodos, campos e enums;
- assinaturas (tipos dos parâmetros e do retorno);
- offset de cada campo (`// 0x48`), que traduz `*(float *)(this + 0x48)` no pseudo-C;
- endereço de cada método (RVA e VA, explicados na seção 4), que leva ao corpo no Ghidra. Ignore o
  "Offset" ao lado, que é a posição no arquivo;
- atributos e valores de `const` e de enums, que vêm do metadata;
- strings literais (num arquivo à parte, conforme a ferramenta).

**Não são código-fonte: nenhum método tem corpo.** `CalculateDamage(float atk, float def)` prova
que o método existe e quais tipos recebe, mas não diz nada sobre a fórmula. Não escreva um corpo
plausível a partir do nome: marque `inferido` e aponte o endereço.

## 3. Ferramentas padrão

| Ferramenta | Use para | Atenção |
|---|---|---|
| Cpp2IL 2022.1.0-pre-release.21 (verificado em 2026-10-11) | detectar a versão da Unity e gerar DummyDll; lê até a Unity 6000.5 alfa | é pre-release, "work in progress"; a última estável, 2022.0.7 (verificado em 2026-10-11), é de 2022 |
| Il2CppInspectorRedux 2026.2 (verificado em 2026-10-11) | índice em C#, DLLs shim, cabeçalho C++, script para o Ghidra e JSON com o mapa de endereços; metadata de 29 a 110 | também extrai o conteúdo de arrays estáticos (tabelas escritas no código) |
| Ghidra 12.1.4 (verificado em 2026-10-11) | ler a lógica pelo endereço, com os nomes aplicados pelo script do Redux | o script do Redux pede Ghidra 11.3 ou mais novo (verificado em 2026-10-11), aberto no modo PyGhidra |
| ILSpy 11.1 (verificado em 2026-10-11) | abrir as DummyDll e o IL recuperado pelo Cpp2IL | lida com IL quebrado melhor que o dnSpy, segundo o autor do Cpp2IL |

Fluxo: Redux para o índice e o script do Ghidra; Cpp2IL como segunda opinião e para tentar
recuperar IL. Se uma delas falhar na versão do metadata, use a outra antes de concluir que não dá.

**Cpp2IL** (o nome do `.exe` muda conforme o download):

```
Cpp2IL-Win.exe --game-path="estudo/<jogo>/copia" --output-to="estudo/<jogo>/cpp2il_out"
Cpp2IL-Win.exe --list-output-formats
```

Para tentar recuperar o corpo dos métodos como IL, acrescente `--output-as dll_il_recovery`. A
recuperação é experimental e vem desligada por padrão, e o próprio autor diz que o IL sai
bagunçado. Abra no ILSpy e trate o resultado como pista (seção 6).

**Il2CppInspectorRedux** (tem interface com arrastar e soltar, ou linha de comando):

```
Il2CppInspector.exe -i "estudo/<jogo>/copia/GameAssembly.dll" -m "estudo/<jogo>/copia/<Jogo>_Data/il2cpp_data/Metadata/global-metadata.dat" -t Ghidra
```

`-t Ghidra` diferencia maiúsculas. Aponte as saídas para `estudo/<jogo>/redux/` com `--cs-out`,
`-p`, `--cpp-out` e `--json-out`, e as DLLs shim para `estudo/<jogo>/dummydll/` com `--dll-out`
(seção 8). Mantenha juntos o script, o JSON e o cabeçalho C++: o script do Ghidra usa os três.
Veja as opções com `--help`: no Redux, `-h` é a saída C++, não a ajuda.

## 4. Ler a lógica no Ghidra

1. Abra o Ghidra no modo PyGhidra (`support/pyghidraRun.bat`), crie um projeto em
   `estudo/<jogo>/ghidra/` e importe a cópia de `GameAssembly.dll`.
2. Quando ele oferecer a análise automática, responda No.
3. File › Parse C Source: crie um perfil com o cabeçalho do Redux (`il2cpp.h` na interface,
   `cpp/appdata/il2cpp-types.h` na linha de comando), use a opção `-D_GHIDRA_` e clique em
   Parse to Program.
4. Window › Script Manager: adicione a pasta de saída do Redux, clique em Refresh e rode o script
   Python gerado. Ele dá às funções o nome da classe e do método e aplica os tipos.
5. Rode a análise automática (Analysis › Auto Analyze) e depois o script de novo.
6. Vá até o método. RVA (Relative Virtual Address) é a distância do método até o início do DLL; o
   endereço no Ghidra (VA) é a base da imagem + RVA. A base de `GameAssembly.dll` costuma ser
   `0x180000000` (confira em Window › Memory Map), então o RVA `0x4A3B20` vira `0x1804A3B20`.
   Tecle G e cole. Se a ferramenta já mostrar o VA, use direto.
7. Leia a janela Decompile, um método por vez, começando pelas funções pequenas. Limpe o ruído
   (seção 5) e abra as funções chamadas que mudam o resultado.

## 5. Ruído do pseudo-C do IL2CPP

O conversor do IL2CPP insere verificações e inicializações que não existiam no C#. Tire-as antes de
escrever a fórmula:

| Padrão no pseudo-C | O que é | O que fazer |
|---|---|---|
| teste `== NULL` seguido de uma chamada que não retorna | verificação de nulo (lança NullReferenceException) | apague |
| no começo, `if (DAT_xxx == 0) { chamada(&..._TypeInfo); DAT_xxx = 1; }` | inicialização única dos metadados do método (`s_Il2CppMethodInitialized` no C++ gerado) | apague |
| teste de um campo `cctor_finished` (ou parecido) seguido de uma chamada com a classe | garante que o construtor estático da classe já rodou | apague |
| índice comparado com `max_length`, seguido de chamada que não retorna | verificação de limite de array | apague |
| chamada logo depois de gravar uma referência num campo | barreira de escrita do coletor de lixo | apague |
| último parâmetro `MethodInfo *method`; último argumento das chamadas é um ponteiro de metadados ou `0` | ponteiro interno do IL2CPP | ignore |
| primeiro parâmetro `__this` | a instância (o `this` do C#) | leia como `this` |
| `..._TypeInfo->static_fields->bar` | campo estático `Classe.bar` | leia como campo estático |
| chamada por `klass->vtable.<slot>.methodPtr`, ou por ponteiro num offset do objeto | método virtual (pode ser um override) | descubra a classe concreta e abra o método dela |
| constante hexadecimal como `0x3fc00000` numa conta de float, ou leitura de um `DAT_...` | float guardado como bits (`0x3fc00000` é 1,5) | mude o tipo para float no Ghidra e anote o valor |

Efeitos do compilador que também enganam:
- Funções pequenas (getters, `Mathf.Min`, `Mathf.Clamp`) aparecem embutidas em quem as chama.
- O compilador C++ pode pré-calcular contas: `atk * 0.75f` pode ter sido `atk * (1 - 0.25f)` no
  fonte. Anote o número visto como "possivelmente pré-calculado".
- Métodos genéricos podem compartilhar um corpo só; o mesmo endereço aparece para vários métodos no índice.
- Nomes ofuscados (Beebyte): o Redux desfaz a troca com o plugin Beebyte Deobfuscator, se houver uma
  versão antiga do mesmo jogo sem ofuscação (IL2CPP ou Mono). Sem ela, parta das âncoras: métodos
  que a Unity chama pelo nome (`Update`, `OnTriggerEnter2D`), strings e chamadas à API da Unity.

## 6. Status das afirmações

| Você tem | Status |
|---|---|
| só nome, assinatura ou tipo de campo (dump.cs, DummyDll, DLL shim) | `inferido` |
| IL recuperado pelo Cpp2IL, ainda não conferido no pseudo-C | `inferido` |
| texto do jogo (dica, descrição de item) | `inferido` |
| endereço achado, mas corpo não lido ou lido em parte, ou com sub-chamadas que mudam o resultado ainda fechadas | `localizado-não-expandido` |
| pseudo-C do endereço lido, ruído removido, sub-chamadas relevantes abertas, literais conferidos | `confirmado` |
| comportamento cronometrado ou contado jogando | `medido-jogando` |

Sem corpo, escreva assim: "só a assinatura está disponível; a lógica está em `GameAssembly.dll`,
endereço 0x1804A3B20 (`Combat.DamageCalc.Compute`)". Nunca preencha o corpo pelo contexto.

## 7. global-metadata.dat cifrado

Sinais: os 4 primeiros bytes não são `af 1b b1 fa`, o Cpp2IL e o Redux falham ao ler, ou os nomes
saem como lixo.

- Metadata cifrado é comum em jogos online (gacha, competitivos). Nesses, pare: a skill só cobre
  jogos single-player ou offline (SKILL.md, "Escopo e limites").
- Tente o Redux primeiro. Ele reconhece sozinho alguns esquemas conhecidos (DLL empacotado, XOR,
  nomes de exportação embaralhados) e tem plugins para outros.
- Se ele não reconhecer, decifrar uma cópia para leitura está no escopo. A rotina está no próprio
  cliente, em `GameAssembly.dll` ou `UnityPlayer.dll`: é o código que abre o metadata e transforma
  os bytes antes de usá-los (costuma aparecer perto de quem usa a string `global-metadata.dat`).
  O arquivo aberto vai para `estudo/<jogo>/metadata-aberto/` e só vale se começar com
  `af 1b b1 fa` e abrir nas ferramentas.
- Tudo fica em `estudo/<jogo>/`: não recifre, não grave de volta no jogo e não publique a chave, o
  arquivo nem o script. Avise o usuário do risco legal uma vez, como diz o SKILL.md.
- Se a rotina não aparecer (string escondida, carregador ofuscado), registre
  `localizado-não-expandido` no `DIARIO.md` e siga pelo que não depende do metadata: texturas,
  modelos, áudio e TextAssets saem normalmente, e wiki e medição jogando cobrem os números.

## 8. Dados: AssetRipper, "unreadable" e type trees

Os assets não mudam com o IL2CPP: texturas, modelos, áudio, TextAssets e tabelas saem como num
jogo Mono. A exceção são os MonoBehaviours (scripts presos a objetos) e os ScriptableObjects
(arquivos de dados), que no arquivo também aparecem como `MonoBehaviour`.

Type tree é a descrição dos campos de cada tipo gravado num asset (nome, tipo, ordem). Builds de
jogo costumam sair sem ela. Nesse caso, a ferramenta precisa das classes dos scripts para saber como
ler os bytes: num jogo Mono, ela lê os DLLs de `Managed/`; num IL2CPP, precisa de `GameAssembly.dll`
e `global-metadata.dat`.

- O AssetRipper 2.0.0 (verificado em 2026-10-11) já traz o Cpp2IL embutido. Abra a pasta raiz da
  cópia (a que tem `GameAssembly.dll` e `<Jogo>_Data/`), não só `<Jogo>_Data/`, e exporte para
  `estudo/<jogo>/projeto/`.
- Se os MonoBehaviours ainda saírem como "unreadable" ou sem campos, ele não conseguiu montar as
  classes: metadata numa versão que ele não lê, metadata cifrado (seção 7) ou arquivo faltando na cópia.
- Contorno: gere as DummyDll (com `--dll-out` no Redux; no Cpp2IL, veja em
  `--list-output-formats` qual formato gera DLLs) e entregue-as ao UnityPy 1.25.4 (verificado em
  2026-10-11), que monta as type trees a partir delas. Isso exige o pacote `TypeTreeGeneratorAPI`.

Salve como `estudo/<jogo>/ler_monobehaviours.py`, troque os dois caminhos e rode
`python -I estudo/<jogo>/ler_monobehaviours.py > estudo/<jogo>/dados/monobehaviours.json`
(crie a pasta `dados/` antes; no PowerShell 5, troque `> arquivo` por
`| Out-File -Encoding utf8 arquivo`). O script só lê e escreve na tela (stdout).

```python
# pip install UnityPy==1.25.4 TypeTreeGeneratorAPI
import json
import sys

import UnityPy
from UnityPy.helpers.TypeTreeGenerator import TypeTreeGenerator

DADOS = "estudo/<jogo>/copia/<Jogo>_Data"
DUMMY = "estudo/<jogo>/dummydll"  # pasta com as DummyDll (Redux --dll-out ou Cpp2IL)

env = UnityPy.load(DADOS)
if not env.objects:
    sys.exit(f"nenhum asset encontrado em {DADOS}")
gen = TypeTreeGenerator(env.objects[0].assets_file.unity_version)
gen.load_dll_folder(DUMMY)
# alternativas: gen.load_local_game("estudo/<jogo>/copia")  (pasta raiz da cópia) ou
#   gen.load_il2cpp(bytes_do_GameAssembly_dll, bytes_do_global_metadata_dat)
env.typetree_generator = gen

saida = {}
for obj in env.objects:
    if obj.type.name == "MonoBehaviour":
        try:
            saida[str(obj.path_id)] = obj.parse_as_dict()
        except Exception as erro:
            saida[str(obj.path_id)] = f"falhou: {erro}"

sys.stdout.reconfigure(encoding="utf-8")
print(json.dumps(saida, ensure_ascii=False, indent=1, default=str))
```

- Só leitura: não use `patch()` nem `save()`.
- Se o Python fechar sozinho durante a leitura, desligue o leitor em C antes do laço:
  `from UnityPy.helpers import TypeTreeHelper` e `TypeTreeHelper.read_typetree_boost = False`.
- No UnityPy, a troca do segundo número da versão (1.25 para 1.26) pode quebrar a API; mantenha a
  versão fixa.

## 9. Padrões antigos

Tutoriais e skills antigas ainda mandam usar estas ferramentas. Não as escolha por padrão: em Unity
recente elas falham ou saem incompletas, e quem está começando conclui que "não dá para ler".

| Ferramenta | Situação | Por que não é o padrão | Quando ainda serve |
|---|---|---|---|
| Il2CppDumper v6.7.46 (verificado em 2026-10-11) | último release em 2024-07; sem commits desde 2024-08 | o README promete só Unity 5.3 a 2022.2; restaura os DLLs "exceto o código"; com metadata cifrado, só avisa que o arquivo não é válido | jogo de Unity antiga, ou quando o usuário já tem o `dump.cs` dele: use como índice |
| Il2CppInspector original 2021.1 (verificado em 2026-10-11) | desenvolvimento suspenso | parou antes dos metadata recentes | não use; o Il2CppInspectorRedux é a continuação |
| AssetStudio original | arquivado | parou em Unity antiga; o fork AssetStudioMod v0.18.0 (verificado em 2026-10-11) vai até a Unity 6000.2 | ver um asset isolado de jogo antigo; para o resto, AssetRipper ou UnityPy |
| Cpp2IL 2022.0.7 (verificado em 2026-10-11) | última estável, de 2022-09 | não lê os metadata mais novos | jogo antigo em que a recuperação de IL do pre-release falhou: em 2025, o mantenedor indicou essa versão como a última com recuperação de corpo |

## 10. Da leitura para a ficha da mecânica

Preencha a parte A da ficha (SKILL.md, Passo 4) assim:
- **Fonte:** `GameAssembly.dll`, endereço (VA e RVA), `Classe.Metodo` do índice, versão da Unity e
  versão do metadata.
- **Trecho mínimo:** o pseudo-C limpo, reescrito como pseudocódigo na mesma ordem, com os tipos
  (int/float), casts, limites e arredondamentos. Marque números como "possivelmente pré-calculado"
  quando couber.
- **Números de balanceamento:** dos MonoBehaviours e ScriptableObjects extraídos (seção 8), não do
  pseudo-C, quando forem campos serializados.
- **Status:** pela tabela da seção 6. Sem `confirmado`, a parte B (redesenho) pode seguir, mas diga
  que parte da regra é hipótese e proponha medir jogando.

Exemplo (nomes e endereços inventados):

```text
A. Original (fiel)
Regra: chance de crítico = base + 0,5% por ponto de sorte, limitada a 50%.
Fórmula: chance = min(0,5; base + 0,005 × sorte)
Pseudocódigo: chance = fminf(this.critBase + (float)luck * 0.005f, 0.5f)
Fonte: GameAssembly.dll, VA 0x1804A3B20 (RVA 0x4A3B20), Combat.CritCalc.GetChance;
       Unity <versão>, metadata v<n>
Status: confirmado (pseudo-C lido, ruído removido; 0.005f pode ser pré-calculado)
```

As partes B (redesenho) e C (como testar) seguem o SKILL.md.
