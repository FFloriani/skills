#!/usr/bin/env python3
"""Audita um README do GitHub com checagens mecânicas, em prioridades P0/P1/P2.

Uso:
    python auditar_readme.py README.md [--raiz PASTA] [--tipo TIPO] [--json]

    --raiz  raiz do repositório (padrão: pasta do README; sobe um nível se o
            README estiver em .github/ ou docs/)
    --tipo  app | jogo | mod | cli | biblioteca | api | awesome | extensao
            (liga checagens que dependem do tipo, como "prova visual")
    --json  saída em JSON

Código de saída: 1 se houver algum P0, senão 0.

P0 = engana, não informa ou quebra: bloqueia a publicação.
P1 = degrada compreensão ou confiança.
P2 = polimento.
Os limiares numéricos (ex.: até 5 badges) são decisões de design, não normas.
Só a biblioteca padrão. Não altera nenhum arquivo.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import unquote

GITHUB_RELATIVOS = (
    "issues", "pulls", "pull", "releases", "actions", "wiki", "discussions", "projects",
    "security", "network", "pulse", "tags", "compare", "commits", "commit", "blob",
    "tree", "labels", "milestones", "stargazers", "forks", "graphs", "raw",
)
HOSTS_BADGE = (
    "shields.io", "badgen.net", "forthebadge.com", "badge.fury.io", "codecov.io",
    "coveralls.io", "travis-ci", "circleci.com", "codacy.com", "snyk.io",
    "bestpractices.dev", "securityscorecards.dev", "badgesize.io", "api.netlify.com",
)
VIDEO_EXT = (".mp4", ".webm", ".mov")
ALT_GENERICO = {
    "image", "img", "imagem", "screenshot", "captura", "captura de tela", "picture",
    "foto", "print", "screen shot", "demo", "gif", "logo",
}
LINK_VAGO = {
    "aqui", "clique aqui", "here", "click here", "link", "este link", "this link",
    "leia mais", "read more", "saiba mais", "more", "mais",
}
HTML_REMOVIDO = ("style", "script", "iframe", "form", "center", "font", "u", "small",
                 "svg", "object", "embed", "input", "button")
MERMAID_TIPOS = {
    "flowchart", "graph", "sequencediagram", "classdiagram", "statediagram",
    "statediagram-v2", "erdiagram", "journey", "gantt", "pie", "quadrantchart",
    "requirementdiagram", "gitgraph", "mindmap", "timeline", "c4context", "c4container",
    "c4component", "c4dynamic", "c4deployment", "sankey-beta", "xychart-beta",
    "block-beta", "packet-beta", "architecture-beta", "kanban", "radar-beta", "treemap-beta",
}
EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿⭐⬆✅❌✨⚠ℹ]")
RE_OBTER = re.compile(
    r"(?i)(instala|install|download|baixar|obter|get(ting)? started|come[çc]ar|começando|"
    r"primeiros passos|quick ?start|in[ií]cio r[aá]pido|requisitos|requirements|releases)"
)
RE_APOIO = re.compile(
    r"(?i)(sponsor|patroc|apoie|apoio|doa[çc]|donat|support (the|this|my)|buy me|ko-?fi|patreon|merch|\bpix\b)"
)
RE_INICIO_RAPIDO = re.compile(r"(?i)(quick ?start|in[ií]cio r[aá]pido|primeiros passos|getting started)")
SEGREDOS = [
    (r"ghp_[A-Za-z0-9]{30,}|gho_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{20,}", "token do GitHub"),
    (r"AKIA[0-9A-Z]{16}", "chave de acesso da AWS"),
    (r"sk-ant-[A-Za-z0-9_-]{20,}|sk-[A-Za-z0-9]{32,}", "chave de API (formato sk-)"),
    (r"xox[baprs]-[A-Za-z0-9-]{10,}", "token do Slack"),
    (r"AIza[0-9A-Za-z_-]{35}", "chave de API do Google"),
    (r"-----BEGIN (RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----", "chave privada"),
]
RE_SEGREDO_ATRIBUIDO = re.compile(
    r"""(?i)\b(password|senha|secret|token|api[_-]?key)\b\s*[:=]\s*['"]([^'"\s]{8,})['"]"""
)
NAO_E_SEGREDO = re.compile(r"(?i)your|xxx|\*\*\*|<|example|exemplo|seu|sua|changeme|placeholder|token_aqui|\$\{")
PLACEHOLDERS = [
    (r"\bTODO\b|\bTBD\b|\bFIXME\b", "TODO/TBD/FIXME"),
    (r"(?i)\bem breve\b|\bcoming soon\b|\blorem ipsum\b", "texto provisório ('em breve', 'coming soon', lorem ipsum)"),
    (r"NomeDo(App|Projeto|Biblioteca|CLI|Jogo|Mod)\b|nome-do-(cli|projeto)\b", "nome de modelo não substituído"),
    (r"(?i)\[badge [^\]]*\]", "marcador [badge ...] não substituído"),
    (r"(?i)\bSEU[-_ ]USU[ÁA]RIO\b|\bYOUR[-_ ]USERNAME\b|\bUSERNAME/REPO\b", "usuário de exemplo não substituído"),
]
RE_OWNER_REPO = re.compile(r"\bOWNER/REPO\b|<owner>/<repo>|\bseu-usuario/seu-repo\b", re.I)
HYPE = re.compile(
    r"(?i)\b(poderos[oa]s?|incr[ií]vel|incr[ií]veis|revolucion[aá]ri[oa]s?|inovador[a]?|"
    r"blazing(ly)?[ -]fast|powerful|amazing|awesome|ultimate|cutting[- ]edge|state[- ]of[- ]the[- ]art|"
    r"seamless(ly)?|game[- ]changer|world[- ]class|next[- ]gen(eration)?|robust[oa]?|perfeit[oa]s?)\b"
)
CARA_DE_IA = re.compile(
    r"(?i)\b(mergulhe|desbloqueie|potencialize|eleve (seu|sua)|jornada|navegue pelo|\bdelve\b|unleash|"
    r"supercharge|elevate your|in today'?s fast[- ]paced|no mundo (acelerado|digital) de hoje|"
    r"whether you'?re|seja voc[eê]|prepare-se para)\b"
)
CONTAGEM_FIXA = re.compile(r"(?i)\b\d[\d.,]*\s*[kK+]?\s*(stars|estrelas|downloads|forks|usu[aá]rios|users)\b")
VERSAO_FIXA = re.compile(r"(?i)\b(vers[aã]o|version)\s+v?\d+\.\d+(\.\d+)?")


class Achado:
    def __init__(self, prio, codigo, linha, problema, correcao):
        self.prio, self.codigo, self.linha, self.problema, self.correcao = prio, codigo, linha, problema, correcao

    def dict(self):
        return {"prioridade": self.prio, "codigo": self.codigo, "linha": self.linha,
                "problema": self.problema, "correcao": self.correcao}


def slug_github(texto: str) -> str:
    t = re.sub(r"<[^>]+>", "", texto)
    t = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", t)
    t = re.sub(r"[`*~]", "", t).strip().lower()
    t = re.sub(r"[^\w\- ]", "", t, flags=re.UNICODE)
    return t.replace(" ", "-")


def existe_com_caixa(base: Path, alvo: str) -> tuple[bool, bool]:
    """(existe, caixa_confere). Compara cada componente com o nome real em disco."""
    atual = base
    caixa_ok = True
    for parte in Path(alvo).parts:
        if parte in ("", "."):
            continue
        if parte == "..":
            atual = atual.parent
            continue
        try:
            nomes = os.listdir(atual)
        except OSError:
            return False, True
        if parte in nomes:
            atual = atual / parte
        else:
            achou = next((n for n in nomes if n.lower() == parte.lower()), None)
            if achou is None:
                return False, True
            caixa_ok = False
            atual = atual / achou
    return True, caixa_ok


def e_badge(src: str) -> bool:
    s = src.lower()
    return any(h in s for h in HOSTS_BADGE) or re.search(r"/badge\.svg|/badge(\?|/)", s) is not None


def auditar(readme: Path, raiz: Path, tipo: str | None) -> tuple[list[Achado], dict, list]:
    texto = readme.read_text(encoding="utf-8", errors="replace")
    linhas = texto.splitlines()
    n = len(linhas)
    achados: list[Achado] = []
    pendencias: list[tuple[int, str]] = []

    def add(prio, codigo, linha, problema, correcao):
        achados.append(Achado(prio, codigo, linha, problema, correcao))

    # --- marca blocos de código e comentários HTML ---
    em_codigo = [False] * n
    blocos = []  # (inicio, fim, lang)
    cerca = None
    for i, l in enumerate(linhas):
        m = re.match(r"^\s*(`{3,}|~{3,})\s*([\w+#.-]*)", l)
        if cerca is None and m:
            cerca = (m.group(1)[0], len(m.group(1)), i, m.group(2).lower())
            em_codigo[i] = True
        elif cerca is not None:
            em_codigo[i] = True
            if re.match(rf"^\s*{re.escape(cerca[0])}{{{cerca[1]},}}\s*$", l):
                blocos.append((cerca[2], i, cerca[3]))
                cerca = None
    if cerca is not None:
        blocos.append((cerca[2], n - 1, cerca[3]))

    em_comentario = [False] * n
    dentro = False
    for i, l in enumerate(linhas):
        if em_codigo[i]:
            continue
        if dentro:
            em_comentario[i] = True
            if "-->" in l:
                dentro = False
            continue
        if "<!--" in l:
            em_comentario[i] = True
            if "-->" not in l[l.index("<!--"):]:
                dentro = True

    def prosa(i):
        return not em_codigo[i] and not em_comentario[i]

    for i, l in enumerate(linhas):
        for m in re.finditer(r"<!--\s*PENDENTE[:\s](.*?)-->", l, re.I):
            pendencias.append((i + 1, m.group(1).strip() or "preencher"))

    # --- títulos ---
    titulos = []  # (linha_idx, nivel, texto)
    for i, l in enumerate(linhas):
        if not prosa(i):
            continue
        m = re.match(r"^(#{1,6})\s+(.*?)\s*#*\s*$", l)
        if m:
            titulos.append((i, len(m.group(1)), m.group(2)))
            continue
        for m in re.finditer(r"<h([1-6])\b[^>]*>(.*?)</h\1>", l, re.I):
            titulos.append((i, int(m.group(1)), re.sub(r"<[^>]+>", "", m.group(2)).strip()))
    h1s = [t for t in titulos if t[1] == 1]
    if not h1s:
        add("P1", "sem-h1", 1, "Não há título H1.", "Use um único H1 com o nome do projeto.")
    elif len(h1s) > 1:
        add("P1", "varios-h1", h1s[1][0] + 1, f"Há {len(h1s)} títulos H1.", "Mantenha um único H1; rebaixe os demais.")
    ant = 0
    for i, nivel, t in titulos:
        if ant and nivel > ant + 1:
            add("P1", "nivel-pulado", i + 1, f"Título pula de H{ant} para H{nivel}: '{t[:40]}'.", "Não pule níveis de título (leitores de tela navegam por eles).")
        ant = nivel

    # --- texto sem código/comentários ---
    corpo = "\n".join(l if prosa(i) else "" for i, l in enumerate(linhas))

    # --- imagens, links, badges ---
    imagens = []  # (linha, alt, src)
    for i, l in enumerate(linhas):
        if not prosa(i):
            continue
        for m in re.finditer(r"!\[([^\]]*)\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)", l):
            imagens.append((i + 1, m.group(1), m.group(2)))
        for m in re.finditer(r"<img\b[^>]*>", l, re.I):
            tag = m.group(0)
            src = re.search(r"\bsrc\s*=\s*[\"']([^\"']+)", tag, re.I)
            alt = re.search(r"\balt\s*=\s*[\"']([^\"']*)", tag, re.I)
            if src:
                imagens.append((i + 1, alt.group(1) if alt else "", src.group(1)))
        for m in re.finditer(r"<source\b[^>]*\bsrcset\s*=\s*[\"']([^\"'\s]+)", l, re.I):
            imagens.append((i + 1, "<source>", m.group(1)))

    links = []  # (linha, texto, alvo)
    for i, l in enumerate(linhas):
        if not prosa(i):
            continue
        for m in re.finditer(r"(?<!!)\[([^\]]*)\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)", l):
            links.append((i + 1, m.group(1), m.group(2)))
        for m in re.finditer(r"<a\b[^>]*\bhref\s*=\s*[\"']([^\"']+)", l, re.I):
            links.append((i + 1, "", m.group(1)))
        m = re.match(r"^\s*\[[^\]]+\]:\s*(\S+)", l)
        if m:
            links.append((i + 1, "", m.group(1)))

    badges = [(ln, alt, src) for ln, alt, src in imagens if e_badge(src)]
    visuais = [(ln, alt, src) for ln, alt, src in imagens if not e_badge(src) and alt != "<source>"]
    videos = [ln for ln, _, alvo in links if alvo.lower().endswith(VIDEO_EXT) or "user-attachments/assets" in alvo]
    videos += [ln for ln, _, src in imagens if src.lower().endswith(VIDEO_EXT) or "user-attachments/assets" in src]
    for i, l in enumerate(linhas):
        if prosa(i) and re.match(r"^\s*https://github\.com/user-attachments/assets/\S+\s*$", l):
            videos.append(i + 1)

    # --- P0: links e imagens locais ---
    def checar_local(ln, alvo, rotulo):
        if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", alvo) or alvo.startswith(("//", "#", "mailto:")):
            return
        caminho = unquote(alvo.split("#", 1)[0].split("?", 1)[0])
        if not caminho:
            return
        partes = [p for p in caminho.split("/") if p not in ("", ".")]
        if caminho.startswith("../") and any(p in GITHUB_RELATIVOS for p in partes):
            return  # ../../issues, ../../releases etc. são rotas do GitHub, não arquivos
        base = raiz if caminho.startswith("/") else readme.parent
        ok, caixa = existe_com_caixa(base, caminho.lstrip("/"))
        if not ok:
            add("P0", f"{rotulo}-quebrado", ln, f"{rotulo.capitalize()} local não existe: {alvo}",
                "Corrija o caminho ou adicione o arquivo ao repositório (confira se não está no .gitignore).")
        elif not caixa:
            add("P0", "caixa-errada", ln, f"Maiúsculas/minúsculas diferem do arquivo real: {alvo}",
                "Use exatamente o nome do arquivo: funciona no Windows/macOS e quebra no GitHub.")

    for ln, _, src in imagens:
        checar_local(ln, src, "imagem")
    for ln, _, alvo in links:
        checar_local(ln, alvo, "link")

    # --- P1: âncoras ---
    slugs: dict[str, int] = {}
    existentes = set()
    for _, _, t in titulos:
        base = slug_github(t)
        k = slugs.get(base, 0)
        existentes.add(base if k == 0 else f"{base}-{k}")
        slugs[base] = k + 1
    for l in linhas:
        for m in re.finditer(r"""<(?:a|h[1-6])\b[^>]*\b(?:id|name)\s*=\s*["']([^"']+)""", l, re.I):
            existentes.add(m.group(1).lower())
    for ln, _, alvo in links:
        if alvo.startswith("#") and len(alvo) > 1 and unquote(alvo[1:]).lower() not in existentes:
            add("P1", "ancora-quebrada", ln, f"Âncora sem título correspondente: {alvo}", "Ajuste o link ao título real (o GitHub gera a âncora do texto do título).")

    # --- P0: segredos, placeholders ---
    for i, l in enumerate(linhas):
        achou_segredo = False
        for padrao, nome in SEGREDOS:
            if re.search(padrao, l):
                add("P0", "segredo", i + 1, f"Possível {nome} no README.", "Remova e revogue o valor; use um nome de variável de ambiente.")
                achou_segredo = True
                break
        m = None if achou_segredo else RE_SEGREDO_ATRIBUIDO.search(l)
        if m and not NAO_E_SEGREDO.search(m.group(2)):
            add("P0", "segredo", i + 1, f"Valor literal atribuído a '{m.group(1)}'.", "Troque por um placeholder (ex.: SEU_TOKEN_AQUI) ou variável de ambiente.")
        if RE_OWNER_REPO.search(l):
            add("P0", "placeholder", i + 1, "OWNER/REPO (ou equivalente) não foi substituído.", "Use o owner/repo real do remoto git.")
        if prosa(i):
            for padrao, nome in PLACEHOLDERS:
                if re.search(padrao, l):
                    add("P0", "placeholder", i + 1, f"Conteúdo provisório: {nome}.", "Preencha com fato real ou remova a seção.")
                    break

    # --- P1: caminhos locais e e-mails ---
    for i, l in enumerate(linhas):
        m = re.search(r"[A-Za-z]:\\Users\\([^\\\s]+)\\|/Users/([^/\s]+)/|/home/([^/\s]+)/", l)
        if m:
            nome = next(g for g in m.groups() if g)
            if nome.lower() not in {"user", "username", "you", "seu_usuario", "usuario", "<user>", "%username%", "name"}:
                add("P1", "caminho-local", i + 1, f"Caminho de usuário local ({nome}).", "Troque por um caminho genérico ou variável (%USERPROFILE%, ~).")
    def linha_de(padrao, so_titulos=False) -> int:
        """Primeira linha de prosa que casa com o padrão (1 se não achar)."""
        regex = padrao if hasattr(padrao, "search") else re.compile(padrao)
        for i, l in enumerate(linhas):
            if prosa(i) and regex.search(l):
                return i + 1
        return 1

    emails = set(re.findall(r"[\w.+-]+@[\w-]+\.[\w.-]+", corpo))
    emails = {e for e in emails if "noreply" not in e and not e.endswith((".png", ".jpg", ".svg"))}
    if emails:
        add("P1", "email", linha_de(r"[\w.+-]+@[\w-]+\.[\w.-]+"), f"E-mail(s) no texto: {', '.join(sorted(emails))[:80]}.", "Confirme que a exposição é intencional (spam e coleta por robôs).")

    # --- P0: definição, caminho para obter, licença ---
    definicao = None
    for i in range(min(n, 40)):
        if not prosa(i):
            continue
        l = linhas[i].strip()
        if not l or re.match(r"^#{1,6}\s", l) or re.match(r"^</?\w+[^>]*>$", l):
            continue
        t = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", l)
        t = re.sub(r"<[^>]+>", "", t)
        t = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", t)
        t = re.sub(r"[*_`>]", "", t).strip(" |·-")
        if len(t) < 12 or re.match(r"^[\W\d_]*$", t) or re.fullmatch(r"([\w ]+[|·]\s*)+[\w ]+", t) and len(t) < 40:
            continue
        definicao = (i + 1, t)
        break
    if definicao is None:
        add("P0", "sem-definicao", 1, "Não há frase de definição perto do topo.", "Logo após o título, diga em uma frase o que é, para quem e o diferencial.")
    else:
        ln, t = definicao
        if len(t) > 160:
            add("P1", "definicao-longa", ln, f"Definição com {len(t)} caracteres.", "Reduza para ~120 caracteres e mova o resto para 'Por que existe'.")
        elif len(t) > 120:
            add("P2", "definicao-longa", ln, f"Definição com {len(t)} caracteres.", "Alvo: até 120 caracteres, igual ao About do repositório.")

    obter = next((i for i, nv, t in titulos if RE_OBTER.search(t)), None)
    util = max(1, n)
    if obter is None:
        add("P0", "sem-caminho-para-obter", 1, "Nenhuma seção de instalação, download ou início rápido.", "Adicione 'Instalação' ou 'Baixar' com comando copiável ou link de Releases.")
    elif n > 40 and obter > util * 0.5:
        add("P0", "obter-tarde", obter + 1, "O caminho para obter/instalar só aparece depois da metade do arquivo.", "Suba Instalação/Baixar para logo depois da definição e da prova visual.")
    apoio = next((i for i, nv, t in titulos if RE_APOIO.search(t)), None)
    if apoio is not None and (obter is None or apoio < obter):
        add("P1", "apoio-antes-do-download", apoio + 1, "Seção de apoio/patrocínio vem antes de instalar/baixar.", "Mova apoio, anúncios e merch para depois da definição, do download e de contribuir.")

    licenca = next((p for p in raiz.iterdir() if p.is_file() and re.match(r"(?i)^(licen[cs]e|copying|unlicense)(\..*)?$", p.name)), None) if raiz.is_dir() else None
    if tipo != "awesome":
        if licenca is None:
            add("P0", "sem-licenca", 1, "Não há arquivo LICENSE na raiz do repositório.", "Adicione LICENSE (escolha em choosealicense.com) e cite a licença no README.")
        elif not re.search(r"(?i)licen[cs]e|licen[çc]a", corpo):
            add("P1", "licenca-nao-citada", n, "LICENSE existe, mas o README não a menciona.", "Adicione badge ou seção curta de licença (SPDX).")

    # --- P1: prova visual, alt, badges, html ---
    topo_limite = (obter if obter is not None else 60) + 1
    if tipo in ("app", "jogo", "mod", "extensao"):
        if not any(ln <= max(topo_limite, 40) for ln, _, _ in visuais) and not videos:
            add("P1", "sem-prova-visual", 1, f"Projeto do tipo '{tipo}' sem imagem ou vídeo antes da instalação.", "Adicione um screenshot/GIF da tela principal acima da dobra (ou um marcador PENDENTE).")
    elif tipo == "cli" and not visuais and not videos:
        add("P2", "sem-demo", 1, "CLI sem GIF/captura de terminal.", "Considere um GIF curto (VHS) com o comando e o resultado.")
    elif tipo is None and not visuais and not videos:
        add("P2", "sem-midia", 1, "Nenhuma imagem ou vídeo. Informe --tipo para saber se isso importa.", "Para projetos com interface, inclua screenshot ou GIF.")

    for ln, alt, src in visuais:
        a = alt.strip().lower()
        if not a:
            add("P1", "alt-vazio", ln, f"Imagem sem texto alternativo: {src[:50]}", "Descreva o que a imagem mostra em uma frase curta.")
        elif a in ALT_GENERICO or re.fullmatch(r"[\w-]+\.(png|jpe?g|gif|svg|webp)", a):
            add("P1", "alt-generico", ln, f"Alt genérico ('{alt}').", "Diga o que a imagem mostra (ex.: 'Captura de tela da lista de tarefas com filtro ativo').")
        elif re.match(r"(?i)^(imagem|image|foto|picture) (de|of)\b", a):
            add("P2", "alt-redundante", ln, f"Alt começa com 'imagem de': '{alt[:40]}'.", "Leitores de tela já anunciam 'imagem'; descreva direto o conteúdo.")
    for ln, alt, src in badges:
        if not alt.strip():
            add("P2", "badge-sem-alt", ln, "Badge sem texto alternativo.", "Use alt como 'Licença MIT', 'Última versão', 'Build'.")

    if len(badges) > 8:
        add("P1", "muralha-de-badges", badges[0][0], f"{len(badges)} badges (teto sugerido: 8).", "Mantenha 3 a 5 que respondam: funciona? qual versão? posso usar? é mantido?")
    elif len(badges) > 5:
        add("P2", "muitos-badges", badges[0][0], f"{len(badges)} badges (alvo: até 5).", "Remova os que não informam algo útil ao leitor.")
    vistos = {}
    for ln, _, src in badges:
        if src in vistos:
            add("P1", "badge-duplicado", ln, "Badge repetido.", "Remova a duplicata.")
        vistos[src] = ln
        if re.search(r"shields\.io/github/workflow/status", src):
            add("P1", "badge-rota-aposentada", ln, "Rota /github/workflow/status do shields.io foi aposentada.", "Use /github/actions/workflow/status/OWNER/REPO/ARQUIVO.yml.")

    for i, l in enumerate(linhas):
        if not prosa(i):
            continue
        for tag in HTML_REMOVIDO:
            if re.search(rf"<\s*{tag}\b", l, re.I):
                add("P1", "html-removido", i + 1, f"Tag <{tag}> é removida ou escapada pelo GitHub.", "Use Markdown ou o subconjunto permitido (align, width, details, picture).")
        if re.search(r"<[a-zA-Z][^>]*\s(style|class)\s*=", l):
            add("P1", "html-atributo-removido", i + 1, "Atributo style/class é removido pelo GitHub.", "Use align/width ou remova.")
        if re.search(r"<\s*video\b", l, re.I):
            add("P1", "video-bruto", i + 1, "<video> não é renderizado em README de repositório.", "Arraste o vídeo no editor do GitHub e cole a URL user-attachments em linha própria, ou use GIF.")
        if re.search(r"#gh-(dark|light)-mode-only", l):
            add("P2", "fragmento-gh-depreciado", i + 1, "#gh-*-mode-only está depreciado.", "Use <picture> com prefers-color-scheme.")
    for ln, texto_link, alvo in links:
        if texto_link.strip().lower().strip(".:") in LINK_VAGO:
            add("P1", "link-nao-descritivo", ln, f"Texto de link vago: '{texto_link}'.", "Use um texto que diga o destino ('Guia de instalação').")

    # --- P1: início rápido ---
    for i, nv, t in titulos:
        if RE_INICIO_RAPIDO.search(t):
            fim = next((j for j, nv2, _ in titulos if j > i and nv2 <= nv), n)
            bloco = next(((a, b) for a, b, _ in blocos if i < a < fim), None)
            if bloco and (bloco[1] - bloco[0] - 1) > 20:
                add("P1", "inicio-rapido-longo", bloco[0] + 1, f"Bloco de início rápido com {bloco[1] - bloco[0] - 1} linhas.", "Corte para ~15 linhas e leve o resto para 'Uso' ou docs/.")
            break

    # --- P1: contribuir/suporte, idiomas ---
    if not re.search(r"(?i)contribu|issues|pull request|reportar|report (a )?bug|suporte|support|ajuda|help", corpo):
        add("P1", "sem-contribuicao-nem-suporte", n, "Não diz como contribuir nem onde pedir ajuda.", "Adicione 2 a 3 linhas: onde abrir issue e se aceita PR.")
    irmaos = sorted(p for p in readme.parent.iterdir()
                    if p.is_file() and p != readme and re.match(r"(?i)^readme[._-][\w-]+\.md$", p.name))
    if irmaos:
        cabeca = "\n".join(linhas[:20])
        faltam = [p.name for p in irmaos if p.name.lower() not in cabeca.lower()]
        if faltam:
            add("P1", "seletor-de-idiomas", 1, f"Sem link no topo para: {', '.join(faltam)}.", "Coloque o mesmo seletor de idiomas no topo de todos os arquivos.")

    # --- P2: polimento ---
    if n < 12:
        add("P1", "muito-curto", 1, f"README com {n} linhas.", "Cubra: o que é, por que existe, instalação, uso, licença.")
    elif n > 500:
        add("P2", "muito-longo", 1, f"README com {n} linhas.", "Mova referência e explicação para docs/ e deixe o essencial.")
    if n > 100 and sum(1 for _, _, a in links if a.startswith("#")) < 3:
        add("P2", "sem-toc", 1, "Arquivo longo sem sumário.", "Adicione sumário (o GitHub também gera o Outline).")
    n_emoji_tit = sum(1 for _, _, t in titulos if EMOJI.search(t))
    n_emoji = len(EMOJI.findall(corpo))
    if n_emoji_tit:
        ln_tit = next(i + 1 for i, _, t in titulos if EMOJI.search(t))
        add("P2", "emoji-em-titulo", ln_tit, f"{n_emoji_tit} título(s) com emoji.", "Remova emoji decorativo; leitores de tela leem o nome de cada um.")
    elif n_emoji > 10:
        add("P2", "muito-emoji", linha_de(EMOJI), f"{n_emoji} emojis no texto.", "Mantenha só os funcionais (ex.: tabela de compatibilidade).")
    padrao_shortcode = re.compile(r"(?<![\w:/]):[a-z0-9_+-]{3,}:(?![\w:/])")
    if padrao_shortcode.search(re.sub(r"https?://\S+", "", corpo)):
        add("P2", "shortcode-emoji", linha_de(padrao_shortcode), "Há shortcodes de emoji (:rocket:).", "Evite: não renderizam em PyPI/npm e não ajudam a leitura.")
    hype = HYPE.findall(corpo) if tipo != "awesome" else []
    if hype:
        add("P2", "adjetivo-vazio", linha_de(HYPE), f"Adjetivos de marketing: {len(hype)} ocorrência(s).", "Troque por fato mensurável (número, comparação, recurso concreto).")
    if CARA_DE_IA.search(corpo):
        add("P2", "cara-de-ia", linha_de(CARA_DE_IA), "Expressões típicas de texto gerado por IA.", "Reescreva em frases diretas, com nomes e números reais.")
    if corpo.count("\u2014") > 8:
        add("P2", "travessao", linha_de(r"\u2014"), f"{corpo.count(chr(0x2014))} travessões (—).", "Use vírgula, ponto ou dois-pontos; excesso lembra texto de IA.")
    m_fixa = CONTAGEM_FIXA.search(corpo)
    if m_fixa:
        add("P2", "contagem-fixa", linha_de(CONTAGEM_FIXA), f"Número fixo envelhece: '{m_fixa.group(0)}'.", "Use badge dinâmico ou remova.")
    if VERSAO_FIXA.search(corpo):
        add("P2", "versao-fixa", linha_de(VERSAO_FIXA), "Versão escrita à mão no texto.", "Use badge de release ou o permalink latest.")
    for a, b, lang in blocos:
        if lang == "mermaid":
            primeira = next((x.strip() for x in linhas[a + 1:b] if x.strip() and not x.strip().startswith("%%")), "")
            tipo_m = re.split(r"[\s;]", primeira, maxsplit=1)[0].lower() if primeira else ""
            if tipo_m == "zenuml":
                add("P1", "mermaid-nao-suportado", a + 1, "zenuml não é suportado no GitHub.", "Use sequenceDiagram.")
            elif tipo_m and tipo_m not in MERMAID_TIPOS:
                add("P1", "mermaid-tipo-desconhecido", a + 1, f"Tipo Mermaid não reconhecido: '{tipo_m}'.", "Use flowchart, sequenceDiagram, classDiagram, stateDiagram, erDiagram, gantt, pie...")
            elif tipo_m.endswith("-beta"):
                add("P2", "mermaid-beta", a + 1, f"Tipo '{tipo_m}' é beta e pode mudar.", "Prefira tipos clássicos.")
    if not re.search(r"(?i)status|ativo|manuten|experimental|arquivad|maintained|deprecated|\bbeta\b|\balpha\b|\bwip\b|est[aá]vel|stable", corpo):
        add("P2", "sem-status", 1, "Não declara o status do projeto.", "Uma linha: ativo, em manutenção, experimental ou arquivado.")

    resumo = {
        "arquivo": str(readme), "linhas": n, "titulos": len(titulos), "imagens": len(visuais),
        "badges": len(badges), "videos": len(set(videos)), "blocos_de_codigo": len(blocos),
        "pendencias": len(pendencias), "tipo": tipo or "não informado",
    }
    return achados, resumo, pendencias


def formatar(achados, resumo, pendencias) -> str:
    cont = {p: sum(1 for a in achados if a.prio == p) for p in ("P0", "P1", "P2")}
    out = [f"# Auditoria do README: {Path(resumo['arquivo']).name}", ""]
    out.append(
        f"**P0: {cont['P0']} · P1: {cont['P1']} · P2: {cont['P2']} · pendências: {resumo['pendencias']}**  "
        f"(linhas {resumo['linhas']}, imagens {resumo['imagens']}, badges {resumo['badges']}, tipo {resumo['tipo']})"
    )
    rotulos = {"P0": "P0 — bloqueia a publicação", "P1": "P1 — degrada compreensão ou confiança", "P2": "P2 — polimento"}
    for p in ("P0", "P1", "P2"):
        itens = [a for a in achados if a.prio == p]
        if not itens:
            continue
        out += ["", f"## {rotulos[p]}", "", "| Linha | Código | Problema | Como corrigir |", "|---|---|---|---|"]
        for a in sorted(itens, key=lambda a: a.linha):
            out.append(f"| {a.linha} | `{a.codigo}` | {a.problema} | {a.correcao} |")
    if pendencias:
        out += ["", "## Pendências marcadas (preencher antes de publicar)", ""]
        out += [f"- linha {ln}: {t}" for ln, t in pendencias]
    if not achados and not pendencias:
        out += ["", "Nenhum problema mecânico encontrado. Leia o texto com olhos de quem nunca viu o projeto: ainda vale conferir o que o script não vê (clareza da definição, honestidade das promessas)."]
    out += ["", "_Checagem mecânica: não substitui a leitura do texto contra o repositório._"]
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("readme")
    ap.add_argument("--raiz")
    ap.add_argument("--tipo", choices=["app", "jogo", "mod", "cli", "biblioteca", "api", "awesome", "extensao"])
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    readme = Path(args.readme).resolve()
    if not readme.is_file():
        print(f"Arquivo não encontrado: {readme}", file=sys.stderr)
        return 2
    if args.raiz:
        raiz = Path(args.raiz).resolve()
    else:
        raiz = readme.parent.parent if readme.parent.name.lower() in (".github", "docs") else readme.parent

    achados, resumo, pend = auditar(readme, raiz, args.tipo)
    if args.json:
        print(json.dumps({"resumo": resumo, "achados": [a.dict() for a in achados],
                          "pendencias": [{"linha": l, "texto": t} for l, t in pend]}, ensure_ascii=False, indent=2))
    else:
        print(formatar(achados, resumo, pend))
    return 1 if any(a.prio == "P0" for a in achados) else 0


if __name__ == "__main__":
    sys.exit(main())
