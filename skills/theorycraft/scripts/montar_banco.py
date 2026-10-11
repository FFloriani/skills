#!/usr/bin/env python3
"""Junta todas as tabelas extraídas (CSV, TSV, JSON, JSONL) num banco SQLite.

Cada arquivo vira uma tabela com nome tirado do caminho. JSON aceito:
  - lista de objetos;
  - objeto com "Rows" (DataTable/CurveTable do Unreal exportado pelo FModel);
  - objeto de objetos (a chave vira a coluna _chave).
Objetos aninhados viram colunas "pai__filho"; listas viram texto JSON.
A tabela _fontes registra de qual arquivo veio cada tabela.

Uso:
    python montar_banco.py theorycraft/<jogo>/<versão>/dados --banco theorycraft/<jogo>/<versão>/jogo.sqlite
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sqlite3
import sys
from pathlib import Path

EXTENSOES = {".csv", ".tsv", ".json", ".jsonl"}


def configurar_saida() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            if stream.isatty():
                stream.reconfigure(errors="replace")
            else:
                stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def nome_sql(texto: str) -> str:
    nome = re.sub(r"[^0-9A-Za-z_]+", "_", texto).strip("_").lower() or "col"
    return f"t_{nome}" if nome[0].isdigit() else nome


def converter(valor):
    if valor is None or isinstance(valor, (int, float)):
        return valor
    if isinstance(valor, (list, dict)):
        return json.dumps(valor, ensure_ascii=False)
    texto = str(valor).strip()
    if texto == "":
        return None
    if re.fullmatch(r"-?0\d+", texto):  # ID com zero à esquerda continua texto
        return texto
    try:
        return int(texto)
    except ValueError:
        pass
    try:
        return float(texto.replace(",", ".")) if re.fullmatch(r"-?\d+[.,]\d+([eE]-?\d+)?", texto) else texto
    except ValueError:
        return texto


def achatar(obj: dict, prefixo: str = "") -> dict:
    saida = {}
    for chave, valor in obj.items():
        nome = f"{prefixo}__{chave}" if prefixo else str(chave)
        if isinstance(valor, dict) and valor and len(nome.split("__")) < 3:
            saida.update(achatar(valor, nome))
        else:
            saida[nome] = valor
    return saida


def linhas_json(dados) -> list[dict]:
    if isinstance(dados, list):
        return [achatar(x) if isinstance(x, dict) else {"valor": x} for x in dados]
    if isinstance(dados, dict):
        if isinstance(dados.get("Rows"), dict):
            return [{"_chave": k, **achatar(v if isinstance(v, dict) else {"valor": v})} for k, v in dados["Rows"].items()]
        if dados and all(isinstance(v, dict) for v in dados.values()):
            return [{"_chave": k, **achatar(v)} for k, v in dados.items()]
        return [achatar(dados)]
    return [{"valor": dados}]


def ler(caminho: Path) -> list[dict]:
    ext = caminho.suffix.lower()
    if ext in (".csv", ".tsv"):
        with caminho.open(newline="", encoding="utf-8-sig", errors="replace") as f:
            return list(csv.DictReader(f, delimiter="\t" if ext == ".tsv" else ","))
    texto = caminho.read_text(encoding="utf-8-sig", errors="replace")
    if ext == ".jsonl":
        return [achatar(json.loads(l)) for l in texto.splitlines() if l.strip()]
    dados = json.loads(texto)
    if isinstance(dados, list) and len(dados) == 1 and isinstance(dados[0], dict) and "Rows" in dados[0]:
        dados = dados[0]
    return linhas_json(dados)


def gravar(con: sqlite3.Connection, tabela: str, linhas: list[dict]) -> int:
    colunas: list[str] = []
    mapa: dict[str, str] = {}
    for l in linhas:
        for c in l:
            if c not in mapa:
                base = nome_sql(c)
                nome = base
                i = 2
                while nome in colunas:
                    nome = f"{base}_{i}"
                    i += 1
                mapa[c] = nome
                colunas.append(nome)
    if not colunas:
        colunas, mapa = ["valor"], {"valor": "valor"}
    con.execute(f'DROP TABLE IF EXISTS "{tabela}"')
    definicao = ", ".join('"' + c + '"' for c in colunas)
    con.execute(f'CREATE TABLE "{tabela}" ({definicao})')
    marcadores = ", ".join("?" for _ in colunas)
    inverso = {v: k for k, v in mapa.items()}
    con.executemany(
        f'INSERT INTO "{tabela}" VALUES ({marcadores})',
        ([converter(l.get(inverso[c])) for c in colunas] for l in linhas),
    )
    return len(colunas)


def main(argv: list[str]) -> int:
    configurar_saida()
    ap = argparse.ArgumentParser(description="Monta um banco SQLite com todas as tabelas extraídas.")
    ap.add_argument("pasta_dados")
    ap.add_argument("--banco", required=True)
    args = ap.parse_args(argv)

    raiz = Path(args.pasta_dados).resolve()
    arquivos = sorted(p for p in raiz.rglob("*") if p.is_file() and p.suffix.lower() in EXTENSOES)
    if not arquivos:
        print(f"Nenhum CSV/TSV/JSON em {raiz}", file=sys.stderr)
        return 2

    con = sqlite3.connect(args.banco)
    con.execute("DROP TABLE IF EXISTS _fontes")
    con.execute("CREATE TABLE _fontes (arquivo TEXT, tabela TEXT, linhas INTEGER, colunas INTEGER, erro TEXT)")
    usados: set[str] = set()
    ok = falhas = 0
    for arq in arquivos:
        rel = arq.relative_to(raiz).with_suffix("").as_posix()
        tabela = nome_sql(rel)
        base, i = tabela, 2
        while tabela in usados:
            tabela = f"{base}_{i}"
            i += 1
        usados.add(tabela)
        try:
            linhas = ler(arq)
            ncol = gravar(con, tabela, linhas) if linhas else 0
            con.execute("INSERT INTO _fontes VALUES (?,?,?,?,NULL)", (arq.relative_to(raiz).as_posix(), tabela, len(linhas), ncol))
            ok += 1
        except Exception as exc:  # um arquivo ruim não derruba o resto
            con.execute("INSERT INTO _fontes VALUES (?,?,0,0,?)", (arq.relative_to(raiz).as_posix(), tabela, str(exc)[:300]))
            falhas += 1
    con.commit()

    print(f"Banco: {Path(args.banco).resolve()}")
    print(f"{ok} tabelas carregadas, {falhas} arquivos com erro (veja a tabela _fontes).")
    for arquivo, tabela, n, ncol, erro in con.execute("SELECT * FROM _fontes ORDER BY linhas DESC LIMIT 15"):
        print(f"  {tabela:<40} {n:>7} linhas {ncol:>4} colunas" + (f"  ERRO: {erro}" if erro else ""))
    con.close()
    return 0 if falhas == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
