#!/usr/bin/env python3
"""Modelo de calculadora e otimizador de builds.

Copie para theorycraft/<jogo>/calc.py e troque cada função marcada EXEMPLO pela fórmula
confirmada do jogo (veja mecanicas/*.md). Toda fórmula precisa de casos em CASOS_DE_TESTE
com números vistos no jogo (tooltip, dano no boneco de treino, ficha do personagem).

Rodar sem argumentos executa os testes e a demonstração com itens de mentira:
    python calc.py
"""
from __future__ import annotations

import itertools
import math
import sys

# ---------------------------------------------------------------------------
# Atributos
# Chaves que começam com "mais_" são multiplicadores independentes (multiplicam entre si).
# As outras somam. Essa separação é a fonte de erro mais comum em build: confira no código
# do jogo em qual grupo cada bônus entra.
# ---------------------------------------------------------------------------


def somar_atributos(*partes: dict) -> dict:
    total: dict = {}
    for parte in partes:
        for chave, valor in parte.items():
            if chave.startswith("mais_"):
                total.setdefault(chave, []).append(valor)
            else:
                total[chave] = total.get(chave, 0.0) + valor
    return total


def produto_mais(total: dict, chave: str) -> float:
    return math.prod(1 + v for v in total.get(chave, []))


# ---------------------------------------------------------------------------
# Fórmulas: EXEMPLOS genéricos. Substitua pelas do jogo e ajuste os testes.
# ---------------------------------------------------------------------------


def dano_por_acerto(t: dict) -> float:
    """EXEMPLO: base x (1 + soma dos aumentos) x produto dos multiplicadores 'mais'."""
    return t.get("dano_base", 0) * (1 + t.get("dano_aumentado", 0)) * produto_mais(t, "mais_dano")


def multiplicador_critico(t: dict) -> float:
    """EXEMPLO: dano médio com crítico; chance limitada entre 0 e 1."""
    chance = min(max(t.get("chance_critico", 0), 0.0), 1.0)
    return 1 + chance * (t.get("mult_critico", 1.5) - 1)


def ataques_por_segundo(t: dict, fps: int = 60) -> float:
    """EXEMPLO de breakpoint: o ataque dura um número inteiro de quadros."""
    aps = t.get("aps_base", 1.0) * (1 + t.get("velocidade_ataque", 0))
    quadros = max(1, math.ceil(fps / aps - 1e-9))  # tolerância para erro de ponto flutuante
    return fps / quadros


def mitigacao_inimigo(t: dict, armadura_inimigo: float = 500.0) -> float:
    """EXEMPLO: armadura efetiva depois da penetração, curva a/(a+k)."""
    armadura = max(0.0, armadura_inimigo * (1 - t.get("penetracao", 0)))
    return armadura / (armadura + 1000.0)


def dps(t: dict, **premissas) -> float:
    return (dano_por_acerto(t) * multiplicador_critico(t) * ataques_por_segundo(t)
            * (1 - mitigacao_inimigo(t, premissas.get("armadura_inimigo", 500.0))))


def vida_efetiva(t: dict) -> float:
    """EXEMPLO: reduções multiplicativas entre si; resistência com teto de 75%."""
    red_armadura = t.get("armadura", 0) / (t.get("armadura", 0) + 1000.0)
    resist = min(t.get("resistencia", 0), 0.75)
    reducao_total = 1 - (1 - red_armadura) * (1 - resist)
    return t.get("vida", 0) / (1 - reducao_total)


# ---------------------------------------------------------------------------
# Testes: números vistos no jogo. Fórmula que falha volta a "inferido" na ficha.
# (descrição, função, atributos, premissas, esperado, tolerância relativa)
# ---------------------------------------------------------------------------

CASOS_DE_TESTE = [
    ("EXEMPLO: 100 de base, +50% aumentado, 20% mais", dano_por_acerto,
     {"dano_base": 100, "dano_aumentado": 0.5, "mais_dano": [0.2]}, {}, 180.0, 0.001),
    ("EXEMPLO: 1,2 ataque/s vira 50 quadros = 1,2 ataque/s", ataques_por_segundo,
     {"aps_base": 1.2}, {}, 1.2, 0.001),
    ("EXEMPLO: 1,25 ataque/s arredonda para 48 quadros = 1,25", ataques_por_segundo,
     {"aps_base": 1.25}, {}, 1.25, 0.001),
]


def verificar() -> int:
    falhas = 0
    for descricao, funcao, atributos, premissas, esperado, tol in CASOS_DE_TESTE:
        obtido = funcao(atributos, **premissas)
        ok = abs(obtido - esperado) <= abs(esperado) * tol + 1e-9
        falhas += not ok
        print(f"  [{'ok' if ok else 'FALHOU'}] {descricao}: esperado {esperado}, obtido {obtido:.4f}")
    return falhas


# ---------------------------------------------------------------------------
# Otimizador
# ---------------------------------------------------------------------------


def totais(base: dict, build: dict) -> dict:
    return somar_atributos(base, *(item["atributos"] for item in build.values() if item))


def buscar(base: dict, slots: dict, avaliar, top: int = 5, limite_exaustivo: int = 200_000, largura: int = 300):
    """Busca exaustiva quando cabe; senão, busca em feixe slot a slot."""
    nomes = list(slots)
    combinacoes = math.prod(len(slots[s]) for s in nomes)
    if combinacoes <= limite_exaustivo:
        resultados = []
        for escolha in itertools.product(*(slots[s] for s in nomes)):
            build = dict(zip(nomes, escolha))
            resultados.append((avaliar(totais(base, build)), build))
        resultados.sort(key=lambda r: r[0], reverse=True)
        return resultados[:top], f"exaustiva ({combinacoes} combinações)"
    feixe = [{}]
    for s in nomes:
        candidatos = [{**b, s: item} for b in feixe for item in slots[s]]
        candidatos.sort(key=lambda b: avaliar(totais(base, b)), reverse=True)
        feixe = candidatos[:largura]
    resultados = sorted(((avaliar(totais(base, b)), b) for b in feixe), key=lambda r: r[0], reverse=True)
    return resultados[:top], f"feixe (largura {largura}; {combinacoes} combinações no total)"


def pesos_de_atributo(t: dict, avaliar, deltas: dict) -> dict:
    """Quanto o objetivo sobe com +delta de cada atributo (diferença finita)."""
    referencia = avaliar(t)
    pesos = {}
    for chave, delta in deltas.items():
        novo = dict(t)
        if chave.startswith("mais_"):
            novo[chave] = list(t.get(chave, [])) + [delta]
        else:
            novo[chave] = t.get(chave, 0) + delta
        pesos[chave] = avaliar(novo) - referencia
    return pesos


# ---------------------------------------------------------------------------
# Demonstração com itens de mentira
# ---------------------------------------------------------------------------


def demonstracao() -> None:
    base = {"dano_base": 100, "aps_base": 1.2, "chance_critico": 0.05, "mult_critico": 1.5,
            "vida": 1000, "armadura": 200}
    slots = {
        "arma": [
            {"nome": "Espada pesada", "atributos": {"dano_base": 60, "mais_dano": 0.10}},
            {"nome": "Adaga rápida", "atributos": {"dano_base": 25, "velocidade_ataque": 0.30, "chance_critico": 0.10}},
            {"nome": "Lança perfurante", "atributos": {"dano_base": 40, "penetracao": 0.40}},
        ],
        "armadura": [
            {"nome": "Placas", "atributos": {"armadura": 600, "vida": 200}},
            {"nome": "Couro", "atributos": {"armadura": 250, "velocidade_ataque": 0.10}},
            {"nome": "Manto", "atributos": {"resistencia": 0.30, "dano_aumentado": 0.15}},
        ],
        "anel": [
            {"nome": "Anel de fúria", "atributos": {"dano_aumentado": 0.30}},
            {"nome": "Anel preciso", "atributos": {"chance_critico": 0.15, "mult_critico": 0.50}},
            {"nome": "Anel vital", "atributos": {"vida": 400}},
        ],
    }
    vida_minima = 1800

    def objetivo(t: dict) -> float:
        # DPS, mas build que não aguenta o mínimo de vida efetiva fica de fora.
        return dps(t) if vida_efetiva(t) >= vida_minima else float("-inf")

    melhores, metodo = buscar(base, slots, objetivo, top=3)
    print(f"\nDemonstração: maior DPS com vida efetiva >= {vida_minima} (busca {metodo})")
    for pos, (valor, build) in enumerate(melhores, 1):
        t = totais(base, build)
        itens = ", ".join(i["nome"] for i in build.values())
        print(f"  {pos}. DPS {valor:7.1f} | vida efetiva {vida_efetiva(t):7.1f} | {itens}")
        print(f"     dano/acerto {dano_por_acerto(t):.1f} x crítico {multiplicador_critico(t):.3f}"
              f" x ataques/s {ataques_por_segundo(t):.3f} x (1 - mitigação {mitigacao_inimigo(t):.3f})")
    _, campea = melhores[0]
    pesos = pesos_de_atributo(totais(base, campea), dps,
                              {"dano_base": 10, "dano_aumentado": 0.10, "chance_critico": 0.05, "penetracao": 0.10})
    print("  Pesos de atributo (ganho de DPS por +10 de dano, +10% aumentado, +5% crítico, +10% penetração):")
    for chave, ganho in sorted(pesos.items(), key=lambda x: -x[1]):
        print(f"     {chave:<15} {ganho:+.1f}")


def main(argv: list[str]) -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace") if not stream.isatty() else stream.reconfigure(errors="replace")
        except Exception:
            pass
    print("Testes das fórmulas:")
    falhas = verificar()
    if "--sem-exemplo" not in argv:
        demonstracao()
    print(f"\n{falhas} teste(s) falharam." if falhas else "\nTodos os testes passaram.")
    return 1 if falhas else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
