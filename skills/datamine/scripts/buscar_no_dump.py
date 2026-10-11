#!/usr/bin/env python3
"""Procura um nome (ou regex) num dump.cs grande, linha por linha, sem carregar o arquivo inteiro.

Uso:
    python scripts/buscar_no_dump.py <arquivo> <termo ou regex> [-i] [-C N] [-F] [--so-tipos] [--max N]

Para cada linha encontrada mostra o número da linha, o namespace e a classe em que ela
está, e N linhas de contexto (-C). Numa linha de método do dump.cs, a linha de
endereço logo acima ("// RVA: ...") aparece junto mesmo sem -C.
Funciona também com código C# exportado por um decompilador ou qualquer texto grande.
Só lê o arquivo. Usa só a biblioteca padrão do Python 3.
"""

import argparse
import collections
import re
import sys

LARGURA = 300  # caracteres por linha mostrada

RE_NS_COMENTARIO = re.compile(r"^\s*//\s*Namespace:\s*(.*?)\s*$")
RE_NS_BLOCO = re.compile(r"^\s*namespace\s+([\w.]+)\s*(;)?")
RE_TIPO = re.compile(
    r"^\s*(?:\[[^\]]*\]\s*)*"
    r"(?:(?:public|private|protected|internal|static|sealed|abstract|readonly|unsafe|"
    r"partial|ref|new|file)\s+)*"
    r"(record\s+struct|record\s+class|class|struct|enum|interface|record)\s+"
    r"(.+?)(?=\s*:\s|\s*//|\s*\{|\s*\(|\s+where\s|\s*;|\s*$)")
RE_ENDERECO = re.compile(r"^\s*//\s*RVA:", re.IGNORECASE)
RE_MARCA_DUMP = re.compile(r"//\s*(RVA:|TypeDefIndex:)")
PALAVRAS_TIPO = ("class", "struct", "enum", "interface", "record")
RE_METODO = re.compile(r"\)\s*(\{\s*\}|;)?\s*(//.*)?$")
RE_STRING = re.compile(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'')


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


def saldo_chaves(linha):
    """Quantas chaves { abrem menos } fecham, ignorando strings e comentários //."""
    if "{" not in linha and "}" not in linha:
        return 0
    sem_str = RE_STRING.sub('""', linha)
    corte = sem_str.find("//")
    if corte >= 0:
        sem_str = sem_str[:corte]
    return sem_str.count("{") - sem_str.count("}")


def cortar(linha):
    linha = linha.rstrip("\r\n")
    return linha if len(linha) <= LARGURA else linha[:LARGURA] + " ..."


class Escopo:
    """Acompanha namespace e classe atuais enquanto o arquivo é lido."""

    def __init__(self):
        self.prof = 0
        self.ns_comentario = ""   # estilo dump.cs: "// Namespace: X" antes de cada tipo
        self.ns_pilha = []        # estilo C#: namespace X { ... } -> (nome, prof_de_abertura)
        self.ns_arquivo = ""      # estilo C# 10: namespace X;
        self.tipos = []           # (nome, prof_de_abertura)
        self.pendente = None      # ("tipo"|"ns", nome) esperando a chave {

    def namespace(self):
        if self.ns_pilha:
            return ".".join(n for n, _ in self.ns_pilha)
        if self.ns_arquivo:
            return self.ns_arquivo
        return self.ns_comentario

    def classe(self):
        return ".".join(n for n, _ in self.tipos)

    def atualizar(self, linha):
        """Atualiza o escopo com a linha. Devolve o nome do tipo se a linha declara um."""
        declarado = None
        m = RE_NS_COMENTARIO.match(linha)
        if m:
            self.ns_comentario = m.group(1)
            return None
        m = RE_NS_BLOCO.match(linha)
        if m:
            if m.group(2):
                self.ns_arquivo = m.group(1)
            else:
                self.pendente = ("ns", m.group(1))
        elif any(p in linha for p in PALAVRAS_TIPO):
            m = RE_TIPO.match(linha)
            if m:
                declarado = m.group(2).strip()
                self.pendente = ("tipo", declarado)

        saldo = saldo_chaves(linha)
        if saldo > 0:
            if self.pendente:
                tipo, nome = self.pendente
                (self.ns_pilha if tipo == "ns" else self.tipos).append((nome, self.prof))
                self.pendente = None
            self.prof += saldo
        elif saldo < 0:
            self.prof = max(0, self.prof + saldo)
            while self.tipos and self.tipos[-1][1] >= self.prof:
                self.tipos.pop()
            while self.ns_pilha and self.ns_pilha[-1][1] >= self.prof:
                self.ns_pilha.pop()
        return declarado


def montar_padrao(termo, ignorar_caixa, literal):
    flags = re.IGNORECASE if ignorar_caixa else 0
    if literal:
        return re.compile(re.escape(termo), flags), None
    try:
        return re.compile(termo, flags), None
    except re.error as e:
        aviso = f"Regex inválida ({e}); buscando o texto literal."
        return re.compile(re.escape(termo), flags), aviso


def main():
    configurar_saida()
    ap = argparse.ArgumentParser(
        description="Procura classe, método ou campo num dump.cs grande (só leitura).")
    ap.add_argument("arquivo", help="caminho do dump.cs (ou outro texto grande)")
    ap.add_argument("termo", help="nome ou expressão regular")
    ap.add_argument("-i", action="store_true", help="ignorar maiúsculas/minúsculas")
    ap.add_argument("-C", type=int, default=0, metavar="N", help="linhas de contexto antes e depois")
    ap.add_argument("-F", action="store_true", help="tratar o termo como texto literal, não regex")
    ap.add_argument("--so-tipos", action="store_true",
                    help="mostrar só linhas que declaram class/struct/enum/interface")
    ap.add_argument("--max", type=int, default=200, help="máximo de resultados (padrão: 200)")
    args = ap.parse_args()

    padrao, aviso = montar_padrao(args.termo, args.i, args.F)
    if aviso:
        print(aviso)

    ctx = max(0, args.C)
    antes = collections.deque(maxlen=max(ctx, 1))   # (nº, linha) anteriores
    escopo = Escopo()
    resultados = 0
    ultima_impressa = 0
    depois_restante = 0
    por_classe = collections.Counter()
    n = 0
    parou_no_max = False
    parece_dump = False

    try:
        f = open(args.arquivo, "r", encoding="utf-8-sig", errors="replace", newline="")
    except OSError as e:
        print(f"Erro ao abrir {args.arquivo}: {e}", file=sys.stderr)
        return 2

    with f:
        for n, linha in enumerate(f, 1):
            ns_antes, classe_antes = escopo.namespace(), escopo.classe()
            declarado = escopo.atualizar(linha)
            if not parece_dump and "//" in linha and RE_MARCA_DUMP.search(linha):
                parece_dump = True

            casou = padrao.search(linha) is not None
            if casou and args.so_tipos and not declarado:
                casou = False

            if casou:
                if resultados >= args.max:
                    parou_no_max = True
                    break
                resultados += 1
                classe = declarado if declarado else classe_antes
                ns = ns_antes if not declarado else escopo.namespace()
                if declarado and classe_antes:
                    classe = classe_antes + "." + declarado
                por_classe[(ns, classe)] += 1

                # contexto anterior (e a linha "// RVA:" logo acima de um método)
                anteriores = list(antes)[-ctx:] if ctx else []
                if not ctx and antes and RE_ENDERECO.match(antes[-1][1]) \
                        and RE_METODO.search(linha.rstrip()):
                    anteriores = [antes[-1]]
                anteriores = [(k, t) for k, t in anteriores if k > ultima_impressa]

                if ultima_impressa and (anteriores[0][0] if anteriores else n) > ultima_impressa + 1:
                    print("--")
                print(f"== linha {n} | namespace: {ns or '(global)'} | classe: {classe or '(nenhuma)'}")
                for k, t in anteriores:
                    print(f"{k}- {cortar(t)}")
                print(f"{n}: {cortar(linha)}")
                ultima_impressa = n
                depois_restante = ctx
            elif depois_restante > 0:
                print(f"{n}- {cortar(linha)}")
                ultima_impressa = n
                depois_restante -= 1

            antes.append((n, linha))

    print()
    if parou_no_max:
        print(f"Parou em {args.max} resultados (linha {n}). Use --max para ver mais "
              "ou um termo mais específico.")
    else:
        print(f"{resultados} resultado(s) em {n} linhas lidas.")
    if len(por_classe) > 1:
        print("Classes com mais resultados:")
        for (ns, classe), qtd in por_classe.most_common(10):
            print(f"  {qtd:5d}  {(ns + '.') if ns else ''}{classe or '(fora de classe)'}")
    if resultados and parece_dump:
        print("Lembrete: dump.cs só tem assinaturas e endereços, sem corpo de método. O que "
              "sair daqui é inferido ou localizado-não-expandido até o corpo ser lido.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
