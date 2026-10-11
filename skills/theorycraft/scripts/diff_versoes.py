#!/usr/bin/env python3
"""Compara dois bancos do montar_banco.py (versão antiga x nova) e mostra o que mudou.

Para cada tabela presente nas duas versões, as linhas são casadas pela coluna-chave
(--chave, ou _chave, id, name, nome, ou a primeira coluna). Mostra linhas novas,
removidas e alteradas, com o valor antigo -> novo de cada coluna.

Uso:
    python diff_versoes.py antiga/jogo.sqlite nova/jogo.sqlite [--chave id] [--max 30] [--tabela itens]
"""
from __future__ import annotations

import argparse
import sqlite3
import sys

CHAVES_PADRAO = ("_chave", "id", "name", "nome", "key", "rowname")


def configurar_saida() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            if stream.isatty():
                stream.reconfigure(errors="replace")
            else:
                stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def tabelas(con: sqlite3.Connection) -> set[str]:
    return {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")} - {"_fontes"}


def carregar(con: sqlite3.Connection, tabela: str, chave_pedida: str | None):
    cur = con.execute(f'SELECT * FROM "{tabela}"')
    colunas = [d[0] for d in cur.description]
    chave = next((c for c in ([chave_pedida] if chave_pedida else []) + list(CHAVES_PADRAO) if c in colunas), colunas[0])
    i = colunas.index(chave)
    linhas = {}
    for linha in cur:
        linhas.setdefault(linha[i], dict(zip(colunas, linha)))
    return chave, linhas


def main(argv: list[str]) -> int:
    configurar_saida()
    ap = argparse.ArgumentParser(description="Diferenças entre duas versões do datasheet.")
    ap.add_argument("antiga")
    ap.add_argument("nova")
    ap.add_argument("--chave", help="coluna usada para casar as linhas")
    ap.add_argument("--tabela", help="comparar só esta tabela")
    ap.add_argument("--max", type=int, default=30, help="máximo de linhas alteradas listadas por tabela")
    args = ap.parse_args(argv)

    a, b = sqlite3.connect(args.antiga), sqlite3.connect(args.nova)
    ta, tb = tabelas(a), tabelas(b)
    if args.tabela:
        ta, tb = ta & {args.tabela}, tb & {args.tabela}
    for t in sorted(tb - ta):
        print(f"[nova tabela] {t}")
    for t in sorted(ta - tb):
        print(f"[tabela removida] {t}")

    total = 0
    for t in sorted(ta & tb):
        chave, la = carregar(a, t, args.chave)
        _, lb = carregar(b, t, chave)
        novas = [k for k in lb if k not in la]
        removidas = [k for k in la if k not in lb]
        alteradas = []
        for k in la.keys() & lb.keys():
            dif = [(c, la[k].get(c), lb[k].get(c)) for c in sorted(set(la[k]) | set(lb[k])) if la[k].get(c) != lb[k].get(c)]
            if dif:
                alteradas.append((k, dif))
        if not (novas or removidas or alteradas):
            continue
        total += len(novas) + len(removidas) + len(alteradas)
        print(f"\n== {t} (chave: {chave}) — {len(novas)} novas, {len(removidas)} removidas, {len(alteradas)} alteradas")
        for k in novas[: args.max]:
            print(f"  + {k}")
        for k in removidas[: args.max]:
            print(f"  - {k}")
        for k, dif in sorted(alteradas, key=lambda x: str(x[0]))[: args.max]:
            mudancas = "; ".join(f"{c}: {va} -> {vb}" for c, va, vb in dif)
            print(f"  ~ {k}: {mudancas}")
        resto = max(0, len(alteradas) - args.max)
        if resto:
            print(f"  ... e mais {resto} alteradas (use --max ou --tabela)")
    print(f"\nTotal de mudanças em linhas: {total}" if total else "\nNenhuma diferença nas tabelas comuns.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
