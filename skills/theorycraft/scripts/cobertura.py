#!/usr/bin/env python3
"""Relatório de cobertura do inventário: o que já foi extraído e o que falta.

Lê um ou mais CSVs no formato do inventario.csv (caminho, tamanho, categoria, status,
observacao). Status aceitos: pendente, extraido, irrelevante, falhou.
Sai com código 1 se algum arquivo relevante ainda estiver pendente.

Uso:
    python cobertura.py theorycraft/<jogo>/<versão>/inventario.csv [outros.csv ...] [--top 20]
"""
from __future__ import annotations

import argparse
import csv
import sys

RELEVANTES = {"codigo", "conteiner", "dados", "localizacao", "desconhecido"}
STATUS = ("extraido", "irrelevante", "falhou", "pendente")


def configurar_saida() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            if stream.isatty():
                stream.reconfigure(errors="replace")
            else:
                stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def mb(n: int) -> str:
    return f"{n / (1 << 20):.1f} MB"


def main(argv: list[str]) -> int:
    configurar_saida()
    ap = argparse.ArgumentParser(description="Cobertura do inventário de arquivos do jogo.")
    ap.add_argument("csvs", nargs="+")
    ap.add_argument("--top", type=int, default=20, help="quantos pendentes/falhas listar")
    args = ap.parse_args(argv)

    linhas = []
    for caminho in args.csvs:
        with open(caminho, newline="", encoding="utf-8") as f:
            linhas.extend(csv.DictReader(f))

    contagem = {s: [0, 0] for s in STATUS}
    sem_motivo = []
    for l in linhas:
        if l.get("categoria") not in RELEVANTES:
            continue
        status = (l.get("status") or "pendente").strip().lower()
        status = status if status in contagem else "pendente"
        tam = int(l.get("tamanho") or 0)
        contagem[status][0] += 1
        contagem[status][1] += tam
        if status in ("irrelevante", "falhou") and not (l.get("observacao") or "").strip():
            sem_motivo.append(l)

    total_qtd = sum(v[0] for v in contagem.values())
    total_tam = sum(v[1] for v in contagem.values()) or 1
    if total_qtd == 0:
        print("Nenhum arquivo relevante no inventário.")
        return 0

    coberto_qtd = contagem["extraido"][0] + contagem["irrelevante"][0]
    coberto_tam = contagem["extraido"][1] + contagem["irrelevante"][1]
    print(f"Arquivos relevantes (código, contêiner, dados, localização, desconhecido): {total_qtd}")
    for s in STATUS:
        qtd, tam = contagem[s]
        print(f"  {s:<12} {qtd:>7}  ({100 * qtd / total_qtd:5.1f}% dos arquivos, {100 * tam / total_tam:5.1f}% do tamanho)")
    print(f"Cobertura: {100 * coberto_qtd / total_qtd:.1f}% dos arquivos, {100 * coberto_tam / total_tam:.1f}% do tamanho")

    pendentes = sorted((l for l in linhas if l.get("categoria") in RELEVANTES
                        and (l.get("status") or "pendente").strip().lower() not in ("extraido", "irrelevante", "falhou")),
                       key=lambda l: -int(l.get("tamanho") or 0))
    falhas = [l for l in linhas if l.get("categoria") in RELEVANTES and (l.get("status") or "").strip().lower() == "falhou"]

    if pendentes:
        print(f"\nPendentes (maiores primeiro, {min(args.top, len(pendentes))} de {len(pendentes)}):")
        for l in pendentes[: args.top]:
            print(f"  {mb(int(l.get('tamanho') or 0)):>10}  {l['categoria']:<12} {l['caminho']}")
    if falhas:
        print(f"\nFalhas ({len(falhas)}):")
        for l in falhas[: args.top]:
            print(f"  {l['caminho']}  -> {l.get('observacao') or 'SEM MOTIVO'}")
    if sem_motivo:
        print(f"\n{len(sem_motivo)} arquivos marcados irrelevante/falhou sem motivo na coluna observacao.")

    if not pendentes and not sem_motivo:
        print("\nTudo coberto: nada pendente e todo descarte tem motivo.")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
