#!/usr/bin/env python3
"""Exporta as tabelas e views do banco SQLite para uma planilha .xlsx (uma aba por tabela).

Usa openpyxl se estiver instalado (pip install openpyxl). Sem ele, exporta um CSV por
tabela numa pasta, que abre direto no Excel ou no Google Sheets.

Uso:
    python exportar_planilha.py jogo.sqlite --saida planilha.xlsx [--tabelas itens,skills]
"""
from __future__ import annotations

import argparse
import csv
import re
import sqlite3
import sys
from pathlib import Path

LIMITE_LINHAS = 1_048_575  # limite do Excel menos o cabeçalho


def configurar_saida() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            if stream.isatty():
                stream.reconfigure(errors="replace")
            else:
                stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def nome_aba(nome: str, usados: set[str]) -> str:
    base = re.sub(r"[\[\]:*?/\\]", "_", nome)[:31] or "aba"
    aba, i = base, 2
    while aba.lower() in usados:
        sufixo = f"_{i}"
        aba = base[: 31 - len(sufixo)] + sufixo
        i += 1
    usados.add(aba.lower())
    return aba


def main(argv: list[str]) -> int:
    configurar_saida()
    ap = argparse.ArgumentParser(description="Exporta o banco SQLite para planilha.")
    ap.add_argument("banco")
    ap.add_argument("--saida", required=True, help="arquivo .xlsx (ou pasta, se não houver openpyxl)")
    ap.add_argument("--tabelas", help="lista separada por vírgula; padrão: todas, menos _fontes")
    args = ap.parse_args(argv)

    con = sqlite3.connect(args.banco)
    todas = [r[0] for r in con.execute(
        "SELECT name FROM sqlite_master WHERE type IN ('table','view') AND name NOT LIKE 'sqlite_%' ORDER BY type, name")]
    escolhidas = [t.strip() for t in args.tabelas.split(",")] if args.tabelas else [t for t in todas if t != "_fontes"]

    try:
        import openpyxl
    except ImportError:
        openpyxl = None

    if openpyxl is None:
        pasta = Path(args.saida).with_suffix("")
        pasta.mkdir(parents=True, exist_ok=True)
        for t in escolhidas:
            cur = con.execute(f'SELECT * FROM "{t}"')
            with (pasta / f"{t}.csv").open("w", newline="", encoding="utf-8-sig") as f:
                w = csv.writer(f)
                w.writerow([d[0] for d in cur.description])
                w.writerows(cur)
        print(f"openpyxl não está instalado: exportei {len(escolhidas)} CSVs em {pasta}")
        print("Abra no Excel ou no Google Sheets, ou rode 'pip install openpyxl' e exporte de novo.")
        return 0

    wb = openpyxl.Workbook(write_only=True)
    usados: set[str] = set()
    for t in escolhidas:
        cur = con.execute(f'SELECT * FROM "{t}"')
        ws = wb.create_sheet(nome_aba(t, usados))
        ws.append([d[0] for d in cur.description])
        n = 0
        for linha in cur:
            if n >= LIMITE_LINHAS:
                print(f"  {t}: cortada em {LIMITE_LINHAS} linhas (limite do Excel); use o banco para o resto.")
                break
            ws.append(list(linha))
            n += 1
    wb.save(args.saida)
    print(f"Planilha gravada em {Path(args.saida).resolve()} com {len(escolhidas)} abas.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
