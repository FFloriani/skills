#!/usr/bin/env python3
"""Audita a descoberta de um repositório público do GitHub (metadados, não o README).

Uso:
    python auditar_descoberta.py OWNER/REPO [--termo "gerenciador de tarefas"] [--json]
    python auditar_descoberta.py --pasta CAMINHO [--termo ...]   # lê o owner/repo do git remote

--termo  o termo que as pessoas usariam para achar o projeto. Verifica se ele
         aparece no nome, na descrição (About) ou nos topics: são os campos da
         busca padrão do GitHub (o README só entra com `in:readme`).

Faz de 3 a 4 requisições GET públicas: api.github.com (repositório, perfil da
comunidade, último release) e a página github.com/OWNER/REPO (para saber se há
imagem de social preview própria). Só lê; não altera nada. Se existir a variável
de ambiente GITHUB_TOKEN ou GH_TOKEN, ela é enviada apenas a api.github.com
(necessária para repositório privado e para evitar o limite de 60 req/h).

Código de saída: 1 se houver P0, senão 0. Prioridades como em auditar_readme.py.
Os limiares (ex.: 5 a 10 topics, About até 160 caracteres) são heurísticas, não
regras do GitHub.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import unicodedata
import urllib.error
import urllib.request

API = "https://api.github.com"
UA = "better-readme-skill/1.0 (+https://github.com/FFloriani/skills)"
GENERICOS = {"app", "project", "projeto", "test", "teste", "demo", "my-app", "myapp", "untitled",
             "repo", "repository", "code", "src", "main", "tool", "tools", "utils", "stuff", "sandbox"}
PADRAO_FALLBACK_OG = "by creating an account on GitHub"
EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿⭐✅❌✨⚠]")


def requisitar(url: str, token: str | None = None, aceitar_json: bool = True):
    cab = {"User-Agent": UA}
    if aceitar_json:
        cab["Accept"] = "application/vnd.github+json"
    if token and url.startswith(API):
        cab["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=cab)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            corpo = r.read().decode("utf-8", errors="replace")
            return r.status, corpo
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace") if e.fp else ""
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        return 0, str(e)


def normalizar(t: str) -> str:
    t = unicodedata.normalize("NFKD", t.lower())
    return "".join(c for c in t if not unicodedata.combining(c))


def tokens(t: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", normalizar(t))


def sem_plural(p: str) -> str:
    return p[:-1] if len(p) > 3 and p.endswith("s") else p


def owner_repo_da_pasta(pasta: str) -> str | None:
    try:
        r = subprocess.run(["git", "-C", pasta, "remote", "get-url", "origin"], capture_output=True,
                           text=True, timeout=10, encoding="utf-8", errors="replace")
    except (OSError, subprocess.SubprocessError):
        return None
    m = re.search(r"github\.com[:/]+([^/]+)/([^/]+?)(?:\.git)?/?$", r.stdout.strip())
    return f"{m.group(1)}/{m.group(2)}" if m else None


def auditar(owner_repo: str, termo: str | None, token: str | None):
    achados: list[tuple[str, str, str, str]] = []  # prioridade, codigo, problema, correcao
    info: dict = {"repo": owner_repo}

    def add(prio, codigo, problema, correcao):
        achados.append((prio, codigo, problema, correcao))

    status, corpo = requisitar(f"{API}/repos/{owner_repo}", token)
    if status == 404:
        return None, {"erro": f"Repositório não encontrado ou privado: {owner_repo} (para privado, defina GITHUB_TOKEN)."}
    if status == 403 and "rate limit" in corpo.lower():
        return None, {"erro": "Limite de requisições da API atingido (60/h sem token). Defina GITHUB_TOKEN ou tente mais tarde."}
    if status != 200:
        return None, {"erro": f"Falha ao ler o repositório (HTTP {status}): {corpo[:120]}"}
    repo = json.loads(corpo)
    nome = repo.get("name") or ""
    desc = (repo.get("description") or "").strip()
    topics = repo.get("topics") or []
    info.update({
        "descricao": desc, "topics": topics, "homepage": repo.get("homepage"),
        "estrelas": repo.get("stargazers_count"), "fork": repo.get("fork"),
        "arquivado": repo.get("archived"), "licenca": (repo.get("license") or {}).get("spdx_id"),
        "ramo_padrao": repo.get("default_branch"), "ultimo_push": repo.get("pushed_at"),
    })

    # --- nome ---
    if normalizar(nome) in GENERICOS or len(nome) < 3:
        add("P2", "nome-generico", f"Nome '{nome}' é genérico e compete com milhares de homônimos na busca.",
            "Prefira um nome curto que contenha o termo principal. Renomear mantém estrelas e links, mas quebra Pages e Actions: faça antes de divulgar.")
    if repo.get("fork"):
        add("P1", "fork-fora-da-busca", "É um fork: fica escondido por padrão na busca de repositórios e herda o About do original.",
            "Se o projeto evoluiu por conta própria, reescreva o About e avalie desvincular do original (confirme o procedimento no GitHub antes).")
    if repo.get("archived"):
        add("P2", "arquivado", "Repositório arquivado (continua aparecendo na busca padrão, mas sinaliza projeto parado).",
            "Se ainda é mantido, desarquive; se não, deixe isso explícito no README.")

    # --- About ---
    if not desc:
        add("P1", "sem-descricao", "Sem descrição (About): o GitHub usa o texto genérico 'Contribute to ... development by creating an account on GitHub' no link e no Google.",
            "Escreva o About: termo principal + benefício, ≤ 160 caracteres se possível (limite visto em teste: 350).")
    else:
        if len(desc) < 25:
            add("P2", "descricao-curta", f"Descrição muito curta ({len(desc)} caracteres).", "Diga o que é, para quem e em qual plataforma.")
        if len(desc) > 160:
            add("P2", "descricao-longa", f"Descrição com {len(desc)} caracteres: cartões e resultados costumam cortar perto de 160 (heurística).",
                "Deixe o termo principal e o benefício no começo; o resto vai para o README.")
        if EMOJI.search(desc):
            add("P2", "emoji-na-descricao", "Emoji na descrição entra no <title> e nos cartões de compartilhamento.", "Remova.")
        if normalizar(desc) == normalizar(nome):
            add("P1", "descricao-igual-ao-nome", "A descrição repete o nome e não diz o que o projeto faz.", "Escreva o que é + para quem.")

    # --- topics ---
    if not topics:
        add("P1", "sem-topics", "Sem topics: não aparece em `topic:` nem nas páginas de topic, e só o nome o casa.",
            "Adicione 5 a 10 topics precisos (linguagem, domínio, tipo, plataforma), em minúsculas e hífen.")
    elif len(topics) < 5:
        add("P2", "poucos-topics", f"{len(topics)} topic(s). Heurística: 5 a 10 precisos (limite do GitHub: 20).",
            "Acrescente linguagem, domínio, tipo e plataforma. Topics são atômicos: use o nome exato (`machine-learning`, não `machine` + `learning`).")

    # --- termo de busca ---
    if termo:
        tk = [sem_plural(t) for t in tokens(termo)]
        slug = "-".join(tokens(termo))
        no_nome = bool(tk) and all(t in normalizar(nome) or sem_plural(t) in normalizar(nome) for t in tk)
        tk_desc = {sem_plural(t) for t in tokens(desc)}
        na_desc = bool(tk) and all(t in tk_desc for t in tk)
        nos_topics = slug in {normalizar(t) for t in topics} or (len(tk) == 1 and tk[0] in {normalizar(t) for t in topics})
        info["termo"] = {"termo": termo, "no_nome": no_nome, "na_descricao": na_desc, "nos_topics": nos_topics}
        if not (no_nome or na_desc or nos_topics):
            add("P1", "termo-ausente",
                f"O termo '{termo}' não aparece no nome, na descrição nem nos topics: a busca padrão do GitHub (que ignora o README) não vai casá-lo.",
                "Coloque o termo na primeira frase do About e, se existir, como topic exato; considere-o no nome em projetos novos.")
        elif not na_desc and desc:
            add("P2", "termo-fora-da-descricao", f"O termo '{termo}' casa pelo nome ou topics, mas não está na descrição.",
                "Inclua o termo no começo do About: a descrição vira título e cartão em buscadores.")

    # --- website, licença ---
    if not (repo.get("homepage") or "").strip():
        add("P2", "sem-website", "Campo Website vazio.", "Aponte para a documentação, o site ou a página de Releases.")
    if not repo.get("license"):
        add("P0", "sem-licenca", "O GitHub não detectou licença (sem LICENSE, ou arquivo complexo demais para a detecção).",
            "Adicione um LICENSE simples (choosealicense.com). Sem licença, ninguém pode reutilizar o código legalmente.")

    # --- perfil da comunidade ---
    status_c, corpo_c = requisitar(f"{API}/repos/{owner_repo}/community/profile", token)
    if status_c == 200:
        perfil = json.loads(corpo_c)
        files = perfil.get("files") or {}
        faltam = [rot for chave, rot in (("code_of_conduct", "CODE_OF_CONDUCT"), ("contributing", "CONTRIBUTING"),
                                         ("issue_template", "template de issue"), ("pull_request_template", "template de PR"))
                  if not files.get(chave)]
        info["saude_da_comunidade"] = perfil.get("health_percentage")
        if faltam:
            add("P2", "perfil-da-comunidade", f"Perfil da comunidade em {perfil.get('health_percentage')}%: faltam {', '.join(faltam)}.",
                "É um checklist de arquivos (não ranking). CONTRIBUTING deve cobrir 'como escolher uma tarefa' e 'como falar com a comunidade'.")

    # --- release ---
    status_r, _ = requisitar(f"{API}/repos/{owner_repo}/releases/latest", token)
    info["tem_release"] = status_r == 200
    if status_r == 404:
        add("P2", "sem-release", "Nenhum release publicado: quem não é desenvolvedor não tem o que baixar.",
            "Publique um release com o instalador e/ou o zip portátil (links `releases/latest/download/...`).")

    # --- social preview ---
    status_p, html = requisitar(f"https://github.com/{owner_repo}", None, aceitar_json=False)
    if status_p == 200:
        m = re.search(r'<meta[^>]+property="og:image"[^>]+content="([^"]+)"', html) or \
            re.search(r'<meta[^>]+content="([^"]+)"[^>]+property="og:image"', html)
        if m:
            custom = "repository-images.githubusercontent.com" in m.group(1)
            info["social_preview_personalizado"] = custom
            if not custom:
                add("P2", "sem-social-preview", "Sem imagem de social preview própria: os links compartilhados usam o cartão automático 1200x600.",
                    "Suba uma imagem PNG/JPG < 1 MB, 1280x640, em Settings > Social preview (opcional se o cartão automático já bastar).")
        m_desc = re.search(r'<meta[^>]+property="og:description"[^>]+content="([^"]+)"', html)
        if m_desc and PADRAO_FALLBACK_OG in m_desc.group(1) and desc:
            info["observacao"] = "og:description usa o sufixo padrão do GitHub; normal."

    return achados, info


def formatar(achados, info) -> str:
    cont = {p: sum(1 for a in achados if a[0] == p) for p in ("P0", "P1", "P2")}
    out = [f"# Auditoria de descoberta: {info['repo']}", ""]
    out.append(f"**P0: {cont['P0']} · P1: {cont['P1']} · P2: {cont['P2']}**  "
               f"(estrelas {info.get('estrelas')}, topics {len(info.get('topics') or [])}, "
               f"licença {info.get('licenca') or 'não detectada'}, release {'sim' if info.get('tem_release') else 'não'})")
    out += ["", f"- Descrição: {info.get('descricao') or '(vazia)'}",
            f"- Topics: {', '.join(info.get('topics') or []) or '(nenhum)'}",
            f"- Website: {info.get('homepage') or '(vazio)'}"]
    rot = {"P0": "P0 — bloqueia", "P1": "P1 — atrapalha a descoberta", "P2": "P2 — polimento"}
    for p in ("P0", "P1", "P2"):
        itens = [a for a in achados if a[0] == p]
        if not itens:
            continue
        out += ["", f"## {rot[p]}", "", "| Código | Problema | Como corrigir |", "|---|---|---|"]
        out += [f"| `{c}` | {pr} | {co} |" for _, c, pr, co in itens]
    if not achados:
        out += ["", "Nenhum problema de metadados encontrado."]
    out += ["", "_Isto mede elegibilidade (campos que a busca usa) e higiene. Não prevê posição nem estrelas: o único sinal de ranking documentado são as estrelas._"]
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("repo", nargs="?", help="OWNER/REPO")
    ap.add_argument("--pasta")
    ap.add_argument("--termo")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    for fluxo in (sys.stdout, sys.stderr):
        if hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(encoding="utf-8")

    alvo = args.repo
    if not alvo and args.pasta:
        alvo = owner_repo_da_pasta(args.pasta)
    if not alvo or not re.fullmatch(r"[\w.-]+/[\w.-]+", alvo):
        print("Informe OWNER/REPO ou --pasta com um git remote do GitHub.", file=sys.stderr)
        return 2
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    achados, info = auditar(alvo, args.termo, token)
    if achados is None:
        print(info["erro"], file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps({"info": info, "achados": [dict(prioridade=p, codigo=c, problema=pr, correcao=co) for p, c, pr, co in achados]},
                         ensure_ascii=False, indent=2))
    else:
        print(formatar(achados, info))
    return 1 if any(a[0] == "P0" for a in achados) else 0


if __name__ == "__main__":
    sys.exit(main())
