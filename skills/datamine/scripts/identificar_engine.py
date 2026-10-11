#!/usr/bin/env python3
"""Identifica a engine de um jogo instalado pelos arquivos da pasta.

Uso:
    python scripts/identificar_engine.py "<pasta do jogo>" [--profundidade 4]

Só lê: lista nomes de arquivos e, em poucos casos, os primeiros ou últimos
bytes de um arquivo (assinatura). Nunca grava, move ou altera nada.
Usa só a biblioteca padrão do Python 3.
"""

import argparse
import os
import struct
import sys

LIMITE_ARQUIVOS = 300_000   # evita travar em pastas enormes
MAX_EXEMPLOS = 4            # evidências mostradas por marcador

REF = {
    "unity-mono": "references/unity-mono.md",
    "unity-il2cpp": "references/unity-il2cpp.md",
    "unreal": "references/unreal.md",
    "outras": "references/outras-engines.md",
    "dados": "references/dados-e-curvas.md",
}

EXT_DADOS = (".json", ".csv", ".tsv", ".xml", ".db", ".sqlite", ".sqlite3", ".ini")
EXT_RPGMAKER_CIFRADA = (".rpgmvp", ".rpgmvm", ".rpgmvo", ".png_", ".ogg_", ".m4a_")


def configurar_saida():
    # Saída redirecionada ou capturada por outro programa: UTF-8. Console do Windows:
    # o Python já escreve Unicode; caractere que faltar vira "?".
    for fluxo in (sys.stdout, sys.stderr):
        try:
            if fluxo.isatty():
                fluxo.reconfigure(errors="replace")
            else:
                fluxo.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError, OSError):
            pass


def caminhar(raiz, max_prof):
    """Gera (partes_relativas, nomes_de_pastas, nomes_de_arquivos) até max_prof níveis."""
    pilha = [(raiz, ())]
    while pilha:
        atual, partes = pilha.pop()
        pastas, arquivos = [], []
        try:
            with os.scandir(atual) as it:
                for e in it:
                    try:
                        if e.is_dir(follow_symlinks=False):
                            pastas.append(e.name)
                        elif e.is_file(follow_symlinks=False):
                            arquivos.append(e.name)
                    except OSError:
                        continue
        except OSError:
            continue
        yield partes, pastas, arquivos
        if len(partes) < max_prof:
            for p in sorted(pastas, reverse=True):
                pilha.append((os.path.join(atual, p), partes + (p,)))


def ler_bytes(caminho, inicio, n):
    """Lê n bytes a partir de `inicio` (negativo = contado do fim). Só leitura."""
    try:
        with open(caminho, "rb") as f:
            if inicio < 0:
                f.seek(0, os.SEEK_END)
                tam = f.tell()
                if tam < -inicio:
                    return b""
                f.seek(tam + inicio)
            else:
                f.seek(inicio)
            return f.read(n)
    except OSError:
        return b""


def gamemaker_backend(caminho):
    """data.win é um arquivo IFF (FORM + blocos). Bloco CODE vazio ou ausente sugere YYC."""
    try:
        with open(caminho, "rb") as f:
            cab = f.read(8)
            if len(cab) < 8 or cab[:4] != b"FORM":
                return "assinatura FORM não encontrada; backend não determinado"
            fim = 8 + struct.unpack("<I", cab[4:])[0]
            pos = 8
            for _ in range(200):
                if pos + 8 > fim:
                    break
                f.seek(pos)
                bloco = f.read(8)
                if len(bloco) < 8:
                    break
                nome, tam = bloco[:4], struct.unpack("<I", bloco[4:])[0]
                if nome == b"CODE":
                    if tam == 0:
                        return ("provavelmente YYC (bloco CODE vazio: o código está compilado "
                                "no .exe e só os assets voltam)")
                    return "provavelmente VM (bloco CODE com dados: o GML pode ser decompilado)"
                pos += 8 + tam
            return ("provavelmente YYC (sem bloco CODE: o código está compilado no .exe "
                    "e só os assets voltam)")
    except (OSError, struct.error):
        return "não foi possível ler os blocos; backend não determinado"


class Achados:
    def __init__(self):
        self.itens = {}  # marcador -> lista de caminhos relativos

    def add(self, chave, rel):
        lista = self.itens.setdefault(chave, [])
        if rel not in lista:
            lista.append(rel)

    def get(self, chave):
        return self.itens.get(chave, [])

    def tem(self, *chaves):
        return any(self.itens.get(c) for c in chaves)


def rel_path(partes, nome=None):
    p = list(partes) + ([nome] if nome else [])
    return "/".join(p) if p else "."


def varrer(raiz, max_prof):
    a = Achados()
    total = 0
    cortado = False
    exes_rasos = []

    for partes, pastas, arquivos in caminhar(raiz, max_prof):
        baixo = [p.lower() for p in partes]
        pastas_l = {p.lower(): p for p in pastas}
        ultima = baixo[-1] if baixo else ""

        # pastas marcadoras
        if "renpy" in pastas_l:
            a.add("renpy_pasta", rel_path(partes, pastas_l["renpy"]) + "/")
        if "binaries" in pastas_l and "content" in pastas_l:
            a.add("unreal_estrutura", rel_path(partes) + "/ (tem Binaries/ e Content/)")
        if ultima.endswith("_data") and "streamingassets" in pastas_l:
            a.add("unity_dados", rel_path(partes, pastas_l["streamingassets"]) + "/")

        for nome in arquivos:
            total += 1
            if total > LIMITE_ARQUIVOS:
                cortado = True
                break
            n = nome.lower()
            rel = rel_path(partes, nome)
            completo = os.path.join(raiz, *partes, nome)

            # Unity
            if n == "assembly-csharp.dll":
                if ultima == "managed" and len(baixo) >= 2 and baixo[-2].endswith("_data"):
                    a.add("unity_mono", rel)
            elif n == "gameassembly.dll":
                a.add("unity_il2cpp_dll", rel)
            elif n == "global-metadata.dat":
                a.add("unity_il2cpp_meta", rel)
            elif n == "unityplayer.dll":
                a.add("unity_player", rel)
            elif n in ("resources.assets", "globalgamemanagers", "data.unity3d"):
                a.add("unity_dados", rel)

            # Unreal
            elif n.endswith(".pak") and "paks" in baixo:
                a.add("unreal_pak", rel)
            elif n.endswith((".utoc", ".ucas")):
                a.add("unreal_iostore", rel)
            elif n.endswith("shipping.exe"):
                a.add("unreal_exe", rel)

            # .pck: Godot usa a assinatura GDPC; pacotes de áudio Wwise usam AKPK
            elif n.endswith(".pck"):
                mag = ler_bytes(completo, 0, 4)
                if mag == b"GDPC":
                    a.add("godot_pck", rel)
                elif mag == b"AKPK":
                    a.add("wwise_pck", rel)
                else:
                    a.add("pck_desconhecido", rel)

            # GameMaker
            elif n in ("data.win", "game.unx", "game.ios", "game.droid"):
                a.add("gamemaker", rel)

            # Ren'Py
            elif n.endswith((".rpa", ".rpyc")) and "game" in baixo:
                a.add("renpy_arquivo", rel)

            # RPG Maker MV / MZ
            elif n == "rpg_core.js" and ultima == "js":
                a.add("rpgmaker_mv", rel)
            elif n == "rmmz_core.js" and ultima == "js":
                a.add("rpgmaker_mz", rel)
            elif n == "system.json" and ultima == "data":
                a.add("rpgmaker_system", rel)
            elif n.endswith(EXT_RPGMAKER_CIFRADA):
                a.add("rpgmaker_midia_cifrada", rel)

            # Electron
            elif n == "app.asar" and ultima == "resources":
                a.add("electron", rel)

            # LÖVE
            elif n.endswith(".love"):
                a.add("love_arquivo", rel)
            elif n == "love.dll":
                a.add("love_dll", rel)

            # dados soltos (qualquer engine)
            if n.endswith(EXT_DADOS):
                a.add("dados_soltos", rel)
            if n.endswith(".exe") and len(partes) <= 1:
                exes_rasos.append((rel, completo))
        if cortado:
            break

    # Godot com .pck embutido: o .exe termina com a assinatura "GDPC".
    for rel, completo in exes_rasos:
        if ler_bytes(completo, -4, 4) == b"GDPC":
            a.add("godot_exe", rel)

    return a, total, cortado


def montar_resultados(a, raiz):
    """Lista de (engine, backend, marcadores_de_evidência, referência, observação)."""
    res = []

    mono = a.tem("unity_mono")
    il2cpp = a.tem("unity_il2cpp_dll", "unity_il2cpp_meta")
    if mono and il2cpp:
        res.append(("Unity",
                    "Mono e IL2CPP ao mesmo tempo (veja qual .exe é o jogo; pode haver duas builds)",
                    ["unity_mono", "unity_il2cpp_dll", "unity_il2cpp_meta", "unity_player"],
                    REF["unity-mono"] + " e " + REF["unity-il2cpp"], None))
    elif mono:
        res.append(("Unity",
                    "Mono (C# gerenciado: o corpo dos métodos volta no decompilador)",
                    ["unity_mono", "unity_player", "unity_dados"], REF["unity-mono"], None))
    elif il2cpp:
        obs = None
        if not (a.tem("unity_il2cpp_dll") and a.tem("unity_il2cpp_meta")):
            obs = ("Só um dos dois arquivos do IL2CPP apareceu; o outro pode estar mais fundo "
                   "ou com outro nome.")
        res.append(("Unity",
                    "IL2CPP (lógica em código nativo: voltam nomes, assinaturas e endereços, "
                    "não o corpo dos métodos)",
                    ["unity_il2cpp_dll", "unity_il2cpp_meta", "unity_player", "unity_dados"],
                    REF["unity-il2cpp"], obs))
    elif a.tem("unity_player", "unity_dados"):
        res.append(("Unity",
                    "backend não determinado (sem Assembly-CSharp.dll e sem GameAssembly.dll)",
                    ["unity_player", "unity_dados"],
                    REF["unity-mono"] + " e " + REF["unity-il2cpp"], None))

    if a.tem("unreal_pak", "unreal_iostore", "unreal_exe"):
        res.append(("Unreal Engine (4 ou 5; a versão exata não sai dos nomes de arquivo)",
                    "lógica em C++ fica no .exe; DataTables, curvas e Blueprints ficam nos pacotes",
                    ["unreal_exe", "unreal_pak", "unreal_iostore", "unreal_estrutura"],
                    REF["unreal"], None))

    if a.tem("godot_pck", "godot_exe"):
        res.append(("Godot", ".pck solto ou embutido no .exe (assinatura GDPC)",
                    ["godot_pck", "godot_exe"], REF["outras"], None))
    elif a.tem("pck_desconhecido") and not res:
        res.append(("possivelmente Godot",
                    ".pck sem a assinatura GDPC (pode ser outro formato ou estar cifrado)",
                    ["pck_desconhecido"], REF["outras"], None))

    if a.tem("gamemaker"):
        alvo = os.path.join(raiz, *a.get("gamemaker")[0].split("/"))
        res.append(("GameMaker", "indício: " + gamemaker_backend(alvo),
                    ["gamemaker"], REF["outras"], None))

    if a.tem("renpy_arquivo", "renpy_pasta"):
        res.append(("Ren'Py", "scripts .rpyc (compilados) e/ou pacotes .rpa",
                    ["renpy_pasta", "renpy_arquivo"], REF["outras"], None))

    if a.tem("rpgmaker_mv", "rpgmaker_mz"):
        versao = "MZ" if a.tem("rpgmaker_mz") else "MV"
        obs = None
        if a.tem("rpgmaker_midia_cifrada"):
            obs = "Há mídia cifrada (.rpgmvp, .png_ etc.); JS e JSON continuam em texto puro."
        res.append(("RPG Maker " + versao, "JavaScript e JSON em texto puro",
                    ["rpgmaker_mv", "rpgmaker_mz", "rpgmaker_system", "rpgmaker_midia_cifrada"],
                    REF["outras"], obs))

    if a.tem("electron"):
        res.append(("Electron", "código JavaScript dentro de resources/app.asar",
                    ["electron"], REF["outras"], None))

    if a.tem("love_arquivo", "love_dll"):
        res.append(("LÖVE (Love2D)", "código Lua num .love ou num .exe fundido (abre como zip)",
                    ["love_arquivo", "love_dll"], REF["outras"], None))

    return res


def main():
    configurar_saida()
    ap = argparse.ArgumentParser(
        description="Identifica a engine de um jogo pelos arquivos da pasta (só leitura).")
    ap.add_argument("pasta", help="pasta de instalação do jogo (ou uma cópia dela)")
    ap.add_argument("--profundidade", type=int, default=4,
                    help="quantos níveis de subpasta descer (padrão: 4)")
    args = ap.parse_args()

    raiz = os.path.abspath(args.pasta)
    if not os.path.isdir(raiz):
        print(f"Erro: pasta não encontrada: {args.pasta}", file=sys.stderr)
        return 2

    a, total, cortado = varrer(raiz, max(0, args.profundidade))
    resultados = montar_resultados(a, raiz)

    print(f"Pasta analisada: {raiz.replace(os.sep, '/')}")
    print(f"Arquivos olhados: {total}"
          + (" (limite atingido; resultado parcial)" if cortado else ""))
    print()

    if not resultados:
        print("Engine: desconhecido")
        print(f"Nenhum marcador conhecido até {args.profundidade} níveis de subpasta.")
        print("Tente --profundidade maior ou aponte a pasta onde fica o .exe do jogo.")
        print("Próximo passo: confira a tabela do Passo 1 (Triagem) no SKILL.md.")
        print()
    for i, (engine, backend, chaves, ref, obs) in enumerate(resultados, 1):
        if len(resultados) > 1:
            print(f"[{i}]")
        print(f"Engine:  {engine}")
        print(f"Backend: {backend}")
        print("Evidências:")
        for c in chaves:
            lista = a.get(c)
            for rel in lista[:MAX_EXEMPLOS]:
                print(f"  - {rel}")
            if len(lista) > MAX_EXEMPLOS:
                print(f"  - ... e mais {len(lista) - MAX_EXEMPLOS}")
        if obs:
            print(f"Obs.: {obs}")
        print(f"Próximo passo: leia {ref}")
        print()

    if a.tem("wwise_pck"):
        print("Também achado: pacote de áudio Wwise (.pck com assinatura AKPK; não indica engine)")
        for rel in a.get("wwise_pck")[:MAX_EXEMPLOS]:
            print(f"  - {rel}")
        print()

    dados = a.get("dados_soltos")
    if dados:
        print(f"Arquivos de dados em texto ou SQLite: {len(dados)} (ex.: {', '.join(dados[:3])})")
        print(f"Para tabelas e curvas: {REF['dados']}")
        print()

    print("Nada foi gravado. Antes de extrair, copie o que for estudar para estudo/<jogo>/,")
    print("fora da pasta de instalação.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
