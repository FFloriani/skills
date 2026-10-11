# Extração rápida por engine

Resumo para chegar nas tabelas e no código. Versões verificadas em 2026-10-11. Para o passo a
passo detalhado de cada engine, instale também a skill `datamine`
(https://github.com/FFloriani/skills), que tem um arquivo de referência por engine.

Regra geral: a instalação é só lida. Ferramenta que grava (editor, "salvar", patch, decifrar no
lugar) roda numa cópia. Ferramenta que se injeta no jogo só em single-player offline.

## Identificar a engine

| Marcador na pasta | Engine |
|---|---|
| `<Jogo>_Data/Managed/Assembly-CSharp.dll` | Unity (Mono) |
| `GameAssembly.dll` + `<Jogo>_Data/il2cpp_data/Metadata/global-metadata.dat` | Unity (IL2CPP) |
| `<Jogo>/Content/Paks/*.pak`, `.utoc`, `.ucas`, `*-Shipping.exe` | Unreal Engine 4/5 |
| `.pck` (ou exe com pck embutido) | Godot |
| `data.win` | GameMaker |
| `game/*.rpa`, `.rpyc`, pasta `renpy/` | Ren'Py |
| `www/js/rpg_core.js` ou `js/rmmz_core.js` + `data/*.json` | RPG Maker MV/MZ |
| `resources/app.asar` | Electron/HTML5 |

`scripts/inventario.py` já tenta identificar e mostra a engine provável.

## Onde estão os números e como tirar

| Engine | Tabelas e números | Código (fórmulas) |
|---|---|---|
| Unity Mono | AssetRipper 2.0.0 ou UnityPy 1.25.4: ScriptableObjects, MonoBehaviours, TextAssets, StreamingAssets (JSON, CSV, SQLite) | ILSpy 11.1 (ou dnSpyEx 6.6.0 só para ler); corpo de método completo |
| Unity IL2CPP | AssetRipper/UnityPy; se os MonoBehaviours vierem "unreadable", gere os tipos com Cpp2IL ou Il2CppInspectorRedux | Il2CppInspectorRedux 2026.2 ou Cpp2IL (pre-release; recuperação de IL experimental) + Ghidra no endereço. O `dump.cs` só tem assinaturas, sem corpo |
| Unreal 4/5 | FModel (aug-2026): DataTables e CurveTables, Export > Properties (.json). Pak cifrado precisa da chave AES; muitos jogos têm a chave publicada pela comunidade | Blueprint vira bytecode dentro do .uasset (FModel mostra; "Decompile Blueprint" dá pseudo C++). Lógica em C++ fica no executável (Ghidra) |
| Godot | GDRE Tools 2.7.4 recupera o projeto: `.tres`, `.json`, cenas | GDScript recuperado legível pelo GDRE |
| GameMaker | UndertaleModTool 0.9.2.0 exporta tabelas e assets | GML só em build VM; YYC é nativo (Ghidra) |
| Ren'Py | unrpa 2.3.0 abre `.rpa` | unrpyc 2.0.4 decompila `.rpyc` |
| RPG Maker MV/MZ | `data/*.json` já em texto | `js/` em texto puro |
| Electron/HTML5 | `npx @electron/asar extract app.asar <pasta>` | JavaScript em texto |

Unreal com `.pak`/`.utoc` cifrado (a maioria dos MMOs): rode `scripts/verificar_cifra.py` e siga
`references/chaves-aes.md` para conseguir e validar a chave.

Ferramentas paradas, evite como padrão: Il2CppDumper (última versão 2024, só até Unity 2022.2),
Il2CppInspector original (suspenso em 2022), UModel (só até UE4, 2021), AssetStudio original.

## Jogo online

- Extraia com o jogo fechado; não use ferramenta que se injeta, lê memória ou mexe na rede.
- O cliente traz tabelas de itens, habilidades, atributos e textos, mas parte das regras (drop,
  alguns cálculos, valores ajustados por servidor) fica só no servidor. O que não estiver nos
  arquivos vira `medido-jogando` ou dado da comunidade com fonte.
- Muitos jogos online têm sites de datamine mantidos pela comunidade. Use para conferir a sua
  extração e para cobrir o que é do servidor.

## Depois de extrair

- Converta tudo para CSV ou JSON em `dados/` e rode `scripts/montar_banco.py`.
- Atualize o `inventario.csv`: cada contêiner aberto ganha as linhas dos arquivos de dentro.
- As tabelas de localização ligam IDs a nomes. Carregue-as também e crie views com nomes legíveis.
