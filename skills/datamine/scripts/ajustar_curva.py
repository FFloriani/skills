#!/usr/bin/env python3
"""Testa curvas exponencial, de potência e quadrática numa tabela e mostra os resíduos.

Uso:
    python scripts/ajustar_curva.py 100 380 770 1300          (só y; x = 1, 2, 3...)
    python scripts/ajustar_curva.py 1:100 2:380 3:770          (pares x:y)
    python scripts/ajustar_curva.py "100, 380, 770, 1300"      (lista entre aspas)
    python scripts/ajustar_curva.py tabela.csv [--x nivel] [--y xp]

Opções: --x0 N (primeiro x quando só há y; padrão 1), --r2-min (padrão 0.99),
--residuo-max em % (padrão 10).
Usa só a biblioteca padrão do Python 3 (sem numpy). Só lê o CSV.
"""

import argparse
import csv
import math
import os
import sys


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


# ---------- formatação pt-BR ----------

def br(v, casas=1):
    """Número com vírgula decimal."""
    if v is None or (isinstance(v, float) and not math.isfinite(v)):
        return "-"
    if abs(v) < 0.5 * 10 ** -casas:
        v = 0.0  # evita "-0,0"
    return f"{v:.{casas}f}".replace(".", ",")


def sig(v, n=4):
    """Número com n algarismos significativos, vírgula decimal (para coeficientes)."""
    return f"{v:.{n}g}".replace(".", ",")


def sig_codigo(v, n=4):
    return f"{v:.{n}g}"


# ---------- leitura da entrada ----------

def numero(txt, decimal_virgula=False):
    t = txt.strip().replace(" ", "").replace(" ", "")
    if decimal_virgula and "," in t and "." not in t:
        t = t.replace(",", ".")
    try:
        return float(t)
    except ValueError:
        raise ValueError(f"valor não numérico: '{txt.strip()}'") from None


def ler_csv(caminho, col_x, col_y):
    with open(caminho, "r", encoding="utf-8-sig", errors="replace", newline="") as f:
        amostra = f.read(4096)
        f.seek(0)
        try:
            dialeto = csv.Sniffer().sniff(amostra, delimiters=",;\t")
        except csv.Error:
            dialeto = csv.excel
        linhas = [l for l in csv.reader(f, dialeto) if any(c.strip() for c in l)]
    if not linhas:
        raise ValueError("CSV vazio")
    virgula = dialeto.delimiter != ","

    def eh_num(c):
        try:
            numero(c, virgula)
            return True
        except ValueError:
            return False

    cabecalho = None
    if not all(eh_num(c) for c in linhas[0] if c.strip()):
        cabecalho = [c.strip() for c in linhas[0]]
        linhas = linhas[1:]

    def indice(col, padrao):
        if col is None:
            return padrao
        if cabecalho and col in cabecalho:
            return cabecalho.index(col)
        if cabecalho:
            baixo = [c.lower() for c in cabecalho]
            if col.lower() in baixo:
                return baixo.index(col.lower())
        if col.isdigit():
            return int(col) - 1
        raise ValueError(f"coluna '{col}' não encontrada (cabeçalho: {cabecalho})")

    ncol = max(len(l) for l in linhas)
    so_y = ncol == 1 and col_x is None
    iy = indice(col_y, 0 if so_y else 1)
    ix = None if so_y else indice(col_x, 0)

    xs, ys = [], []
    for k, l in enumerate(linhas, 1):
        try:
            y = numero(l[iy], virgula)
            x = float(k) if ix is None else numero(l[ix], virgula)
        except (ValueError, IndexError):
            continue  # pula linha sem número
        xs.append(x)
        ys.append(y)
    return xs, ys, ix is None


def ler_inline(args):
    tokens = []
    for a in args:
        if ":" not in a and "," in a:
            tokens.extend(t for t in a.split(",") if t.strip())
        else:
            tokens.extend(a.split())
    pares = [t for t in tokens if ":" in t]
    if pares and len(pares) != len(tokens):
        raise ValueError("não misture formatos: use só y (100 380 ...) ou só pares x:y "
                         "(1:100 2:380 ...)")
    if pares:
        xs, ys = [], []
        for t in tokens:
            x, y = t.split(":", 1)
            xs.append(numero(x))
            ys.append(numero(y))
        return xs, ys, False
    return None, [numero(t) for t in tokens], True


# ---------- álgebra ----------

def reta(xs, ys):
    """Mínimos quadrados de y = a + b·x. Devolve (a, b)."""
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx == 0:
        raise ZeroDivisionError
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    return my - b * mx, b


def resolver(m, v):
    """Eliminação de Gauss com pivoteamento parcial (sistema pequeno)."""
    n = len(v)
    a = [list(m[i]) + [v[i]] for i in range(n)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(a[r][c]))
        if abs(a[p][c]) < 1e-12:
            raise ZeroDivisionError
        a[c], a[p] = a[p], a[c]
        for r in range(c + 1, n):
            f = a[r][c] / a[c][c]
            for k in range(c, n + 1):
                a[r][k] -= f * a[c][k]
    sol = [0.0] * n
    for r in range(n - 1, -1, -1):
        sol[r] = (a[r][n] - sum(a[r][k] * sol[k] for k in range(r + 1, n))) / a[r][r]
    return sol


def ajustar_exp(xs, ys):
    if any(y <= 0 for y in ys):
        return None, "precisa de todos os y > 0"
    a0, b0 = reta(xs, [math.log(y) for y in ys])
    a, b = math.exp(a0), math.exp(b0)
    return {
        "nome": "exponencial",
        "f": lambda x: a * b ** x,
        "formula": f"y = {sig(a)} · {sig(b)}^x",
        "codigo": f"{sig_codigo(a)} * pow({sig_codigo(b)}, x)",
        "extra": f"{'+' if b >= 1 else ''}{br((b - 1) * 100)}% por passo de x",
        "params": 2,
    }, None


def ajustar_pot(xs, ys):
    if any(y <= 0 for y in ys) or any(x <= 0 for x in xs):
        return None, "precisa de todos os x > 0 e y > 0"
    a0, b = reta([math.log(x) for x in xs], [math.log(y) for y in ys])
    a = math.exp(a0)
    return {
        "nome": "potência",
        "f": lambda x: a * x ** b,
        "formula": f"y = {sig(a)} · x^{sig(b)}",
        "codigo": f"{sig_codigo(a)} * pow(x, {sig_codigo(b)})",
        "extra": None,
        "params": 2,
    }, None


def ajustar_quad(xs, ys):
    if len(xs) < 4:
        return None, "precisa de pelo menos 4 pontos (com 3 a parábola passa por todos)"
    s = [sum(x ** k for x in xs) for k in range(5)]
    t = [sum(y * x ** k for x, y in zip(xs, ys)) for k in range(3)]
    m = [[s[0], s[1], s[2]], [s[1], s[2], s[3]], [s[2], s[3], s[4]]]
    c0, c1, c2 = resolver(m, t)
    # zera coeficientes que são só ruído de arredondamento
    xmax = max(abs(x) for x in xs) or 1.0
    ymax = max(abs(y) for y in ys) or 1.0
    c0, c1, c2 = [0.0 if abs(c) * xmax ** k <= 1e-9 * ymax else c
                  for k, c in enumerate((c0, c1, c2))]

    def termo(c, sufixo):
        sinal = "-" if c < 0 else "+"
        return f" {sinal} {sig(abs(c))}{sufixo}"

    return {
        "nome": "quadrática",
        "f": lambda x: c0 + c1 * x + c2 * x * x,
        "formula": f"y = {sig(c2)}·x²{termo(c1, '·x')}{termo(c0, '')}",
        "codigo": f"{sig_codigo(c2)} * x * x + ({sig_codigo(c1)}) * x + ({sig_codigo(c0)})",
        "extra": "na prática, uma reta" if c2 == 0 else None,
        "params": 3,
    }, None


def medir(modelo, xs, ys):
    prev = [modelo["f"](x) for x in xs]
    res = [y - p for y, p in zip(ys, prev)]
    my = sum(ys) / len(ys)
    sst = sum((y - my) ** 2 for y in ys)
    ssr = sum(r * r for r in res)
    r2 = 1 - ssr / sst if sst > 0 else (1.0 if ssr == 0 else float("-inf"))
    escala = max(abs(y) for y in ys) or 1.0
    rel = []
    for r, y in zip(res, ys):
        if abs(r) <= 1e-9 * escala:
            rel.append(0.0)
        elif y == 0:
            rel.append(float("inf"))
        else:
            rel.append(abs(r) / abs(y) * 100)
    i = max(range(len(res)), key=lambda k: abs(res[k]))
    return {"prev": prev, "res": res, "r2": r2, "rel": rel,
            "max_abs": res[i], "x_max": xs[i], "max_rel": max(rel)}


def melhor_quebra(xs, ys, minimo=4):
    """Procura onde partir a tabela em dois trechos (exponencial ou potência em cada um)."""
    n = len(xs)
    if n < 2 * minimo:
        return None
    melhor = None
    for k in range(minimo, n - minimo + 1):
        trechos = []
        for a, b in ((0, k), (k, n)):
            tx, ty = xs[a:b], ys[a:b]
            op = []
            for fn in (ajustar_exp, ajustar_pot):
                try:
                    mod, _ = fn(tx, ty)
                except (ZeroDivisionError, OverflowError, ValueError):
                    mod = None
                if mod:
                    op.append((sum((y - mod["f"](x)) ** 2 for x, y in zip(tx, ty)), mod))
            if not op:
                break
            trechos.append(min(op, key=lambda o: o[0]))
        if len(trechos) != 2:
            continue
        my = sum(ys) / n
        sst = sum((y - my) ** 2 for y in ys)
        ssr = trechos[0][0] + trechos[1][0]
        r2 = 1 - ssr / sst if sst > 0 else 1.0
        if melhor is None or r2 > melhor[0]:
            prev = [trechos[0][1]["f"](x) for x in xs[:k]] + [trechos[1][1]["f"](x) for x in xs[k:]]
            max_rel = max((abs(y - p) / abs(y) * 100 for y, p in zip(ys, prev) if y != 0),
                          default=0.0)
            melhor = (r2, k, trechos[0][1], trechos[1][1], max_rel)
    return melhor


def fmt_x(x):
    return br(x, 0) if float(x).is_integer() else br(x, 2)


def main():
    configurar_saida()
    ap = argparse.ArgumentParser(
        description="Testa curvas exponencial, de potência e quadrática e mostra os resíduos.")
    ap.add_argument("dados", nargs="+", help="caminho de um CSV ou os números (y ou pares x:y)")
    ap.add_argument("--x", dest="col_x", help="coluna x do CSV (nome ou número, a partir de 1)")
    ap.add_argument("--y", dest="col_y", help="coluna y do CSV (nome ou número, a partir de 1)")
    ap.add_argument("--x0", type=float, default=1.0, help="primeiro x quando só há y (padrão: 1)")
    ap.add_argument("--r2-min", type=float, default=0.99, help="R² mínimo para aceitar (padrão: 0.99)")
    ap.add_argument("--residuo-max", type=float, default=10.0,
                    help="maior resíduo aceito, em %% do valor real (padrão: 10)")
    args = ap.parse_args()

    try:
        if len(args.dados) == 1 and os.path.isfile(args.dados[0]):
            xs, ys, so_y = ler_csv(args.dados[0], args.col_x, args.col_y)
            origem = args.dados[0].replace("\\", "/")
            if so_y:
                xs = [args.x0 + k for k in range(len(ys))]
        else:
            xs, ys, so_y = ler_inline(args.dados)
            origem = "números na linha de comando"
            if so_y:
                xs = [args.x0 + k for k in range(len(ys))]
    except (OSError, ValueError) as e:
        print(f"Erro ao ler os dados: {e}", file=sys.stderr)
        return 2

    if len(ys) < 3:
        print("Erro: são precisos pelo menos 3 pontos.", file=sys.stderr)
        return 2

    pares = sorted(zip(xs, ys))
    xs, ys = [p[0] for p in pares], [p[1] for p in pares]
    n = len(xs)

    print(f"Dados: {n} pontos ({origem}); x de {fmt_x(xs[0])} a {fmt_x(xs[-1])}")
    print()
    print("1) Incrementos e razões (olhe isto antes das curvas)")
    print(f"{'x':>8} {'y':>12} {'incremento':>12} {'razão do incr.':>15} {'% do último':>12}")
    inc_ant = None
    for k in range(n):
        inc = ys[k] - ys[k - 1] if k else None
        razao = inc / inc_ant if (inc is not None and inc_ant not in (None, 0)) else None
        pct = ys[k] / ys[-1] * 100 if ys[-1] else None
        print(f"{fmt_x(xs[k]):>8} {br(ys[k], 1):>12} {br(inc, 1):>12} {br(razao, 2):>15} {br(pct, 1):>11}%")
        inc_ant = inc
    print("   Incremento constante = reta; incremento que cresce sempre igual = quadrática;")
    print("   razão do incremento constante = exponencial; saltos irregulares = tabela à mão.")
    print()

    print("2) Modelos")
    modelos = []
    for fn, nome in ((ajustar_exp, "exponencial"), (ajustar_pot, "potência"),
                     (ajustar_quad, "quadrática")):
        try:
            mod, motivo = fn(xs, ys)
        except (ZeroDivisionError, OverflowError, ValueError):
            mod, motivo = None, "não foi possível ajustar (dados degenerados)"
        if mod is None:
            print(f"[{nome}] pulado: {motivo}")
            print()
            continue
        m = medir(mod, xs, ys)
        modelos.append((mod, m))
        print(f"[{mod['nome']}]  {mod['formula']}" + (f"   ({mod['extra']})" if mod["extra"] else ""))
        print(f"  em código: {mod['codigo']}")
        print(f"  R² = {br(m['r2'], 4)}   maior resíduo: {br(m['max_abs'], 1)} em x={fmt_x(m['x_max'])}"
              f"   maior resíduo %: {br(m['max_rel'], 1)}%")
        print(f"  {'x':>8} {'real':>12} {'previsto':>12} {'resíduo':>12} {'resíduo %':>10}")
        for x, y, p, r, rl in zip(xs, ys, m["prev"], m["res"], m["rel"]):
            print(f"  {fmt_x(x):>8} {br(y, 1):>12} {br(p, 1):>12} {br(r, 1):>12} {br(rl, 1):>9}%")
        print()

    if not modelos:
        print("Veredito: nenhum modelo pôde ser ajustado; trate como tabela ajustada à mão.")
        return 0

    bons = [(mod, m) for mod, m in modelos
            if m["r2"] >= args.r2_min and m["max_rel"] <= args.residuo_max]
    melhor_mod, melhor_m = max(modelos, key=lambda t: t[1]["r2"])
    print("3) Veredito")
    if bons:
        mod, m = min(bons, key=lambda t: (t[0]["params"], -t[1]["r2"]))
        print(f"   A curva {mod['nome']} descreve bem a tabela (R² {br(m['r2'], 4)}, maior resíduo "
              f"{br(m['max_rel'], 1)}%). Status da fórmula: inferido (ajuste), até ser vista no código.")
    else:
        print(f"   Nenhum modelo chega a R² >= {br(args.r2_min, 2)} com resíduo <= "
              f"{br(args.residuo_max, 0)}% em todos os pontos")
        print(f"   (o melhor foi {melhor_mod['nome']}: R² {br(melhor_m['r2'], 4)}, maior resíduo "
              f"{br(melhor_m['max_rel'], 1)}%).")
        print("   Conclusão provável: tabela ajustada à mão / por partes. Reaproveite a forma,")
        print("   não os números.")
        q = melhor_quebra(xs, ys)
        if q and q[0] > melhor_m["r2"]:
            r2q, k, m1, m2, max_rel = q
            print(f"   Indício de trechos: quebra entre x={fmt_x(xs[k - 1])} e x={fmt_x(xs[k])};"
                  f" {m1['nome']} no 1º trecho ({m1['formula']}),")
            print(f"   {m2['nome']} no 2º ({m2['formula']}); R² combinado {br(r2q, 4)}, "
                  f"maior resíduo {br(max_rel, 1)}%.")
            print("   Com poucos pontos por trecho isto é só uma pista, não uma prova.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
