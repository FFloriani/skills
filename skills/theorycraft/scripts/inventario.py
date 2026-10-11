#!/usr/bin/env python3
"""Inventário de 100% dos arquivos de um jogo instalado (somente leitura).

Percorre a pasta do jogo, classifica cada arquivo e grava inventario.csv na pasta
de saída (que não pode ficar dentro da pasta do jogo). Nada é alterado no jogo.

Uso:
    python inventario.py "<pasta do jogo>" --saida theorycraft/<jogo>/<versão>
    python inventario.py "<pasta do jogo>" --saida <pasta> --hash   (sha1 de cada arquivo; lento)
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import os
import sys
from pathlib import Path

CATEGORIAS = {
    "codigo": {".dll", ".exe", ".so", ".dylib", ".lua", ".luac", ".js", ".mjs", ".py", ".pyc",
               ".gd", ".gdc", ".rpy", ".rpyc", ".cs", ".wasm", ".jar", ".class", ".csx"},
    "conteiner": {".pak", ".utoc", ".ucas", ".pck", ".bundle", ".assets", ".resource", ".ress",
                  ".unity3d", ".rpa", ".asar", ".love", ".zip", ".7z", ".rar", ".vpk", ".bsa",
                  ".ba2", ".arc", ".cpk", ".big", ".win", ".forge", ".archive", ".wad", ".pkg"},
    "dados": {".json", ".jsonl", ".csv", ".tsv", ".xml", ".yaml", ".yml", ".ini", ".cfg", ".toml",
              ".db", ".sqlite", ".sqlite3", ".tbl", ".bytes", ".asset", ".uasset", ".uexp",
              ".tres", ".res", ".txt", ".dat", ".bin"},
    "localizacao": {".locres", ".locmeta", ".po", ".mo", ".loc", ".lang"},
    "textura": {".png", ".jpg", ".jpeg", ".dds", ".tga", ".bmp", ".ktx", ".ktx2", ".astc",
                ".webp", ".exr", ".hdr", ".psd", ".ico"},
    "modelo": {".fbx", ".obj", ".gltf", ".glb", ".mesh", ".blend"},
    "audio": {".wav", ".ogg", ".mp3", ".bnk", ".wem", ".fsb", ".flac", ".opus", ".awb", ".acb"},
    "video": {".mp4", ".webm", ".bk2", ".bik", ".usm", ".mkv", ".avi", ".mov"},
}
PISTAS_LOCALIZACAO = ("localization", "localisation", "locale", "lang", "i18n", "strings", "text")
MIDIA = {"textura", "modelo", "audio", "video"}

MARCADORES_ENGINE = [
    ("Unity IL2CPP", lambda nomes, rel: "gameassembly.dll" in nomes or any(r.endswith("global-metadata.dat") for r in rel)),
    ("Unity Mono", lambda nomes, rel: any(r.endswith("managed/assembly-csharp.dll") for r in rel)),
    ("Unreal Engine", lambda nomes, rel: any("/content/paks/" in r for r in rel) or any(n.endswith(".utoc") for n in nomes)),
    ("Godot", lambda nomes, rel: any(n.endswith(".pck") for n in nomes)),
    ("GameMaker", lambda nomes, rel: "data.win" in nomes),
    ("Ren'Py", lambda nomes, rel: any("/renpy/" in r for r in rel) or any(n.endswith(".rpa") for n in nomes)),
    ("RPG Maker MV/MZ", lambda nomes, rel: "rpg_core.js" in nomes or "rmmz_core.js" in nomes),
    ("Electron/HTML5", lambda nomes, rel: any(r.endswith("resources/app.asar") for r in rel)),
]


def configurar_saida() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            if stream.isatty():
                stream.reconfigure(errors="replace")
            else:
                stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def categoria(rel: str, ext: str) -> str:
    baixo = rel.lower()
    if ext in CATEGORIAS["localizacao"]:
        return "localizacao"
    for nome, exts in CATEGORIAS.items():
        if ext in exts:
            if nome == "dados" and any(f"/{p}" in "/" + baixo for p in PISTAS_LOCALIZACAO):
                return "localizacao"
            return nome
    return "desconhecido"


def sha1(caminho: Path) -> str:
    h = hashlib.sha1()
    with caminho.open("rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def tamanho_legivel(n: float) -> str:
    for unidade in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.0f} {unidade}" if unidade == "B" else f"{n:.1f} {unidade}"
        n /= 1024
    return f"{n:.1f} TB"


def main(argv: list[str]) -> int:
    configurar_saida()
    ap = argparse.ArgumentParser(description="Inventário completo dos arquivos de um jogo (somente leitura).")
    ap.add_argument("pasta_jogo")
    ap.add_argument("--saida", required=True, help="pasta onde gravar inventario.csv (fora da pasta do jogo)")
    ap.add_argument("--hash", action="store_true", help="calcula sha1 de cada arquivo (útil para comparar versões)")
    args = ap.parse_args(argv)

    raiz = Path(args.pasta_jogo).resolve()
    saida = Path(args.saida).resolve()
    if not raiz.is_dir():
        print(f"Pasta do jogo não encontrada: {raiz}", file=sys.stderr)
        return 2
    if saida == raiz or raiz in saida.parents:
        print("A pasta de saída não pode ficar dentro da pasta do jogo.", file=sys.stderr)
        return 2

    linhas = []
    erros = 0
    for pasta, subpastas, arquivos in os.walk(raiz, onerror=lambda e: None, followlinks=False):
        subpastas.sort()
        for nome in sorted(arquivos):
            caminho = Path(pasta) / nome
            rel = caminho.relative_to(raiz).as_posix()
            try:
                tam = caminho.stat().st_size
            except OSError:
                erros += 1
                continue
            ext = caminho.suffix.lower()
            cat = categoria(rel, ext)
            status, obs = ("irrelevante", "mídia: não afeta números") if cat in MIDIA else ("pendente", "")
            linha = {"caminho": rel, "tamanho": tam, "extensao": ext, "categoria": cat,
                     "status": status, "observacao": obs}
            if args.hash:
                try:
                    linha["sha1"] = sha1(caminho)
                except OSError:
                    linha["sha1"] = ""
            linhas.append(linha)

    saida.mkdir(parents=True, exist_ok=True)
    destino = saida / "inventario.csv"
    campos = ["caminho", "tamanho", "extensao", "categoria", "status", "observacao"] + (["sha1"] if args.hash else [])
    with destino.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        w.writerows(linhas)

    nomes = {Path(l["caminho"]).name.lower() for l in linhas}
    rels = ["/" + l["caminho"].lower() for l in linhas]
    engines = [n for n, teste in MARCADORES_ENGINE if teste(nomes, rels)]

    print(f"Jogo: {raiz}")
    print(f"Engine provável: {', '.join(engines) if engines else 'desconhecida (veja references/extracao-rapida.md)'}")
    print(f"{len(linhas)} arquivos, {tamanho_legivel(sum(l['tamanho'] for l in linhas))}"
          + (f" ({erros} sem acesso)" if erros else ""))
    resumo: dict[str, list[int]] = {}
    for l in linhas:
        r = resumo.setdefault(l["categoria"], [0, 0])
        r[0] += 1
        r[1] += l["tamanho"]
    for cat, (qtd, tam) in sorted(resumo.items(), key=lambda x: -x[1][1]):
        marca = "  (marcado irrelevante)" if cat in MIDIA else ""
        print(f"  {cat:<13} {qtd:>7} arquivos  {tamanho_legivel(tam):>10}{marca}")
    print(f"Inventário gravado em {destino}")
    print("Próximo passo: extrair contêineres e tabelas, atualizar a coluna status e rodar cobertura.py.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
