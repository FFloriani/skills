#!/usr/bin/env python3
"""Mostra o que está cifrado num jogo Unreal Engine (.pak e .utoc). Somente leitura.

Lê apenas o rodapé de cada .pak e o cabeçalho de cada .utoc; não decifra nem grava nada.

Uso:
    python verificar_cifra.py "<pasta do jogo>" [--lista 20]
"""
from __future__ import annotations

import argparse
import os
import sys
from collections import Counter
from pathlib import Path

MAGIC_PAK = b"\xe1\x12\x6f\x5a"      # 0x5A6F12E1, little-endian
MAGIC_UTOC = b"-==--==--==--==-"     # 16 bytes
ZERO = "0" * 32


def configurar_saida() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            if stream.isatty():
                stream.reconfigure(errors="replace")
            else:
                stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def ler_utoc(caminho: Path):
    with caminho.open("rb") as f:
        h = f.read(81)
    if len(h) < 81 or h[:16] != MAGIC_UTOC:
        return None
    flags = h[80]  # 1 compactado, 2 cifrado, 4 assinado, 8 indexado
    return bool(flags & 2), h[64:80].hex()


def ler_pak(caminho: Path):
    tam = caminho.stat().st_size
    with caminho.open("rb") as f:
        f.seek(max(0, tam - 1024))
        t = f.read()
    i = t.rfind(MAGIC_PAK)
    if i < 17:
        return None
    # rodapé: [GUID da chave: 16][índice cifrado: 1][magic: 4]...
    return bool(t[i - 1]), t[i - 17:i - 1].hex()


def mb(n: int) -> str:
    return f"{n / (1 << 20):.1f} MB"


def main(argv: list[str]) -> int:
    configurar_saida()
    ap = argparse.ArgumentParser(description="Diagnóstico de cifra de .pak/.utoc (somente leitura).")
    ap.add_argument("pasta")
    ap.add_argument("--lista", type=int, default=20, help="quantos contêineres abertos listar")
    args = ap.parse_args(argv)

    raiz = Path(args.pasta).resolve()
    if not raiz.is_dir():
        print(f"Pasta não encontrada: {raiz}", file=sys.stderr)
        return 2

    resumo = {"pak": Counter(), "utoc": Counter()}
    tamanho = {"pak": Counter(), "utoc": Counter()}
    guids: Counter = Counter()
    abertos = []
    ilegiveis = []

    for pasta, _, arquivos in os.walk(raiz, followlinks=False):
        for nome in arquivos:
            baixo = nome.lower()
            tipo = "pak" if baixo.endswith(".pak") else "utoc" if baixo.endswith(".utoc") else None
            if tipo is None:
                continue
            caminho = Path(pasta) / nome
            rel = caminho.relative_to(raiz).as_posix()
            try:
                tam = caminho.stat().st_size
                if tipo == "utoc":  # o .utoc é só o índice; os dados estão no .ucas ao lado
                    ucas = caminho.with_suffix(".ucas")
                    tam = ucas.stat().st_size if ucas.exists() else tam
                dado = ler_pak(caminho) if tipo == "pak" else ler_utoc(caminho)
            except OSError:
                ilegiveis.append(rel)
                continue
            if dado is None:
                resumo[tipo]["sem cabeçalho reconhecido"] += 1
                tamanho[tipo]["sem cabeçalho reconhecido"] += tam
                continue
            cifrado, guid = dado
            estado = "cifrado" if cifrado else "aberto"
            resumo[tipo][estado] += 1
            tamanho[tipo][estado] += tam
            if cifrado:
                guids[guid] += 1
            else:
                abertos.append((tam, rel))

    total = sum(sum(c.values()) for c in resumo.values())
    if total == 0:
        print("Nenhum .pak ou .utoc encontrado: não é um jogo Unreal empacotado, ou a pasta está errada.")
        return 0

    print(f"Pasta: {raiz}")
    for tipo in ("pak", "utoc"):
        if not resumo[tipo]:
            continue
        partes = [f"{n} {estado} ({mb(tamanho[tipo][estado])})" for estado, n in sorted(resumo[tipo].items())]
        print(f"  .{tipo}: " + ", ".join(partes))
    if guids:
        print(f"\nChaves distintas (GUID) entre os cifrados: {len(guids)}")
        for g, n in guids.most_common(5):
            rotulo = "GUID zerado = chave padrão do jogo" if g == ZERO else "GUID próprio"
            print(f"  {g[:8]}...  {n} contêineres  ({rotulo})")
        print("Para obter a chave: references/chaves-aes.md")
    else:
        print("\nNenhum contêiner cifrado: não precisa de chave.")
    if abertos:
        abertos.sort(reverse=True)
        print(f"\nContêineres que abrem sem chave ({len(abertos)}; maiores primeiro):")
        for tam, rel in abertos[: args.lista]:
            print(f"  {mb(tam):>10}  {rel}")
    if ilegiveis:
        print(f"\n{len(ilegiveis)} arquivos sem permissão de leitura.")
    print("\nNada foi gravado.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
