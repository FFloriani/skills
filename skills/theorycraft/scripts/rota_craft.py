#!/usr/bin/env python3
"""Rota mais barata para criar um item, a partir do grafo de receitas.

receitas.csv: uma linha por insumo de cada receita.
  colunas: produto, insumo, quantidade, [receita], [rende], [tempo], [estacao]
  - receita: ID para separar receitas alternativas do mesmo produto (padrão: produto+estacao)
  - rende: quantos produtos saem por fabricação (padrão 1)
  - tempo: segundos por fabricação (opcional)
custos.csv (opcional): item, custo   (preço de compra ou custo de coleta; vale também para
  itens intermediários, e aí o script decide entre comprar e fabricar)

Uso:
    python rota_craft.py receitas.csv --alvo "Espada de Mithril" --quantidade 3 --custos custos.csv
    python rota_craft.py receitas.csv --alvo X --peso-tempo 0.5   (cada segundo custa 0,5)
"""
from __future__ import annotations

import argparse
import csv
import math
import sys
from collections import defaultdict


def configurar_saida() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            if stream.isatty():
                stream.reconfigure(errors="replace")
            else:
                stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def num(v, padrao=0.0) -> float:
    v = (v or "").strip().replace(",", ".")
    return float(v) if v else padrao


def carregar_receitas(caminho: str) -> dict:
    receitas: dict = {}
    with open(caminho, newline="", encoding="utf-8-sig") as f:
        for l in csv.DictReader(f):
            produto = l["produto"].strip()
            rid = (l.get("receita") or "").strip() or f"{produto} @ {(l.get('estacao') or '').strip() or '-'}"
            r = receitas.setdefault(rid, {"id": rid, "produto": produto, "rende": num(l.get("rende"), 1.0),
                                          "tempo": num(l.get("tempo")), "estacao": (l.get("estacao") or "").strip(),
                                          "insumos": []})
            r["insumos"].append((l["insumo"].strip(), num(l.get("quantidade"), 1.0)))
    por_produto = defaultdict(list)
    for r in receitas.values():
        por_produto[r["produto"]].append(r)
    return por_produto


def main(argv: list[str]) -> int:
    configurar_saida()
    ap = argparse.ArgumentParser(description="Rota de criação mais barata.")
    ap.add_argument("receitas")
    ap.add_argument("--alvo", required=True)
    ap.add_argument("--quantidade", type=float, default=1)
    ap.add_argument("--custos")
    ap.add_argument("--peso-tempo", type=float, default=0.0, help="custo por segundo de fabricação")
    args = ap.parse_args(argv)

    por_produto = carregar_receitas(args.receitas)
    custos: dict[str, float] = {}
    if args.custos:
        with open(args.custos, newline="", encoding="utf-8-sig") as f:
            for l in csv.DictReader(f):
                custos[l["item"].strip()] = num(l.get("custo"))

    if args.alvo not in por_produto and args.alvo not in custos:
        print(f"'{args.alvo}' não aparece como produto nem tem custo.", file=sys.stderr)
        return 2

    melhor: dict[str, tuple[float, object]] = {}  # item -> (custo unitário, "comprar" | receita | None)
    sem_custo: set[str] = set()
    em_ciclo: set[str] = set()

    def custo_unitario(item: str, pilha: frozenset) -> float:
        if item in melhor:
            return melhor[item][0]
        opcoes = []
        pulou_ciclo = False
        if item in custos:
            opcoes.append((custos[item], "comprar"))
        for r in por_produto.get(item, []):
            if any(i in pilha | {item} for i, _ in r["insumos"]):
                pulou_ciclo = True  # receita que depende do próprio item: ignorada
                continue
            total = sum(q * custo_unitario(i, pilha | {item}) for i, q in r["insumos"])
            total += r["tempo"] * args.peso_tempo
            opcoes.append((total / r["rende"], r))
        if not opcoes:
            (em_ciclo if pulou_ciclo else sem_custo).add(item)
            opcoes.append((0.0, None))
        escolha = min(opcoes, key=lambda o: o[0])
        melhor[item] = escolha
        return escolha[0]

    custo_unitario(args.alvo, frozenset())

    comprar: dict[str, float] = defaultdict(float)
    fabricar: dict[str, int] = defaultdict(int)
    sobra: dict[str, float] = defaultdict(float)
    profundidade: dict[str, int] = defaultdict(int)
    linhas_arvore: list[str] = []

    def precisar(item: str, qtd: float, nivel: int) -> None:
        usar = min(sobra[item], qtd)
        sobra[item] -= usar
        qtd -= usar
        if qtd <= 1e-9:
            return
        custo, opcao = melhor[item]
        recuo = "  " * nivel
        if opcao == "comprar" or opcao is None:
            comprar[item] += qtd
            rotulo = ("comprar/coletar" if opcao == "comprar"
                      else "SÓ TEM RECEITA EM CICLO" if item in em_ciclo else "SEM RECEITA E SEM CUSTO")
            linhas_arvore.append(f"{recuo}- {qtd:g} x {item}  ({rotulo}, {custo:g} cada)")
            return
        r = opcao
        vezes = math.ceil(qtd / r["rende"] - 1e-9)
        sobra[item] += vezes * r["rende"] - qtd
        fabricar[r["id"]] += vezes
        profundidade[r["id"]] = max(profundidade[r["id"]], nivel)
        onde = f" na {r['estacao']}" if r["estacao"] else ""
        linhas_arvore.append(f"{recuo}- {qtd:g} x {item}: fabricar {vezes}x{onde} (receita {r['id']})")
        for insumo, q in r["insumos"]:
            precisar(insumo, vezes * q, nivel + 1)

    precisar(args.alvo, args.quantidade, 0)

    receitas_por_id = {r["id"]: r for rs in por_produto.values() for r in rs}
    print(f"Rota para {args.quantidade:g} x {args.alvo}  (custo unitário estimado {melhor[args.alvo][0]:g})\n")
    print("Árvore escolhida:")
    print("\n".join(linhas_arvore))
    print("\nComprar ou coletar:")
    total = 0.0
    for item, qtd in sorted(comprar.items()):
        c = custos.get(item, 0.0) * qtd
        total += c
        print(f"  {qtd:g} x {item}" + (f"  = {c:g}" if item in custos else "  (sem custo informado)"))
    print("\nOrdem de fabricação (de baixo para cima):")
    tempo_total = 0.0
    for rid in sorted(fabricar, key=lambda k: -profundidade[k]):
        r = receitas_por_id[rid]
        tempo_total += fabricar[rid] * r["tempo"]
        print(f"  {fabricar[rid]}x {r['produto']}" + (f" ({r['estacao']})" if r["estacao"] else ""))
    print(f"\nCusto total de matéria-prima: {total:g}")
    if tempo_total:
        print(f"Tempo total de fabricação: {tempo_total:g} s")
    sobras = {k: v for k, v in sobra.items() if v > 1e-9}
    if sobras:
        print("Sobras: " + ", ".join(f"{v:g} x {k}" for k, v in sorted(sobras.items())))
    if sem_custo:
        print("Atenção, sem receita e sem custo (contados como 0): " + ", ".join(sorted(sem_custo)))
    if em_ciclo:
        print("Atenção, só têm receita que depende do próprio item (informe um custo): " + ", ".join(sorted(em_ciclo)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
