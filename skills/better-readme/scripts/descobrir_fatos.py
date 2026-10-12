#!/usr/bin/env python3
"""Levanta, só lendo, os fatos de um repositório que servem de base para o README.

Uso:
    python descobrir_fatos.py [PASTA] [--max-arquivos 20000]

Imprime um JSON (UTF-8) com: git, manifestos, tipo provável do projeto (com as
evidências), licença, README atual, mídia, workflows, arquivos de comunidade,
FUNDING.yml, README traduzidos, sinais de "portátil" e comandos prontos.

Não altera nada e usa só a biblioteca padrão. O resultado é um ponto de partida:
confira no código tudo o que for entrar no README.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

try:
    import tomllib  # Python 3.11+
except ImportError:  # pragma: no cover
    tomllib = None

IGNORAR_DIRS = {
    ".git", "node_modules", ".venv", "venv", "env", "__pycache__", "dist", "build",
    "target", "obj", ".idea", ".vs", ".next", ".nuxt", ".gradle", "vendor", "Pods",
    ".tox", ".mypy_cache", ".pytest_cache", "coverage", ".cache", "Library", "Temp",
}
EXT_MIDIA = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".mp4", ".webm", ".mov"}
EXT_CODIGO = {
    ".py", ".cs", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".java", ".kt", ".cpp",
    ".c", ".h", ".hpp", ".lua", ".gd", ".rb", ".php", ".swift", ".ps1", ".bat",
}
DIRS_MIDIA = {"docs", "doc", "assets", "images", "img", "screenshots", "media", "art", "imgs"}
LIMITE_GITHUB_IMAGEM = 10 * 1024 * 1024

LICENCAS = [
    (r"GNU AFFERO GENERAL PUBLIC LICENSE", "AGPL-3.0"),
    (r"GNU LESSER GENERAL PUBLIC LICENSE", "LGPL"),
    (r"GNU GENERAL PUBLIC LICENSE[\s\S]{0,200}Version 3", "GPL-3.0"),
    (r"GNU GENERAL PUBLIC LICENSE[\s\S]{0,200}Version 2", "GPL-2.0"),
    (r"Apache License[\s\S]{0,100}Version 2\.0", "Apache-2.0"),
    (r"Mozilla Public License[\s\S]{0,60}2\.0", "MPL-2.0"),
    (r"This is free and unencumbered software", "Unlicense"),
    (r"CC0 1\.0 Universal|Creative Commons Zero", "CC0-1.0"),
    (r"Permission to use, copy, modify, and/or distribute", "ISC"),
    (r"Permission is hereby granted, free of charge", "MIT"),
    (r"Neither the name of[\s\S]{0,400}nor the names of its", "BSD-3-Clause"),
    (r"Redistribution and use in source and binary forms", "BSD-2-Clause/3-Clause"),
]


def ler(caminho: Path, limite: int = 300_000) -> str:
    try:
        with open(caminho, "rb") as f:
            return f.read(limite).decode("utf-8", errors="replace")
    except OSError:
        return ""


def git(raiz: Path, *args: str) -> str | None:
    try:
        r = subprocess.run(
            ["git", "-C", str(raiz), *args], capture_output=True, text=True,
            timeout=15, encoding="utf-8", errors="replace",
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout.strip() if r.returncode == 0 else None


def listar_arquivos(raiz: Path, limite: int):
    arquivos: list[Path] = []
    for atual, dirs, nomes in os.walk(raiz):
        dirs[:] = [d for d in dirs if d not in IGNORAR_DIRS]
        for n in nomes:
            arquivos.append(Path(atual) / n)
            if len(arquivos) >= limite:
                return arquivos, True
    return arquivos, False


def rel(raiz: Path, p: Path) -> str:
    return p.relative_to(raiz).as_posix()


def toml_ou_none(caminho: Path):
    if not tomllib:
        return None
    try:
        return tomllib.loads(ler(caminho))
    except Exception:
        return None


def campo_toml(texto: str, chave: str) -> str | None:
    m = re.search(rf'^\s*{re.escape(chave)}\s*=\s*"([^"]+)"', texto, re.M)
    return m.group(1) if m else None


def info_git(raiz: Path) -> dict:
    if git(raiz, "rev-parse", "--is-inside-work-tree") != "true":
        return {"repositorio_git": False}
    remoto = git(raiz, "remote", "get-url", "origin")
    dono = repo = None
    if remoto:
        m = re.search(r"github\.com[:/]+([^/]+)/([^/]+?)(?:\.git)?/?$", remoto)
        if m:
            dono, repo = m.group(1), m.group(2)
    ramo = git(raiz, "symbolic-ref", "--short", "refs/remotes/origin/HEAD")
    ramo = ramo.split("/", 1)[1] if ramo and "/" in ramo else git(raiz, "branch", "--show-current")
    tags = (git(raiz, "tag", "--sort=-v:refname") or "").splitlines()[:5]
    alteracoes = (git(raiz, "status", "--porcelain") or "").splitlines()
    a_frente = atras = None
    if ramo and git(raiz, "rev-parse", "--verify", "--quiet", f"origin/{ramo}"):
        cont = git(raiz, "rev-list", "--left-right", "--count", f"HEAD...origin/{ramo}")
        if cont and len(cont.split()) == 2:
            a_frente, atras = (int(x) for x in cont.split())
    return {
        "repositorio_git": True,
        "remoto": remoto,
        "owner": dono,
        "repo": repo,
        "owner_repo": f"{dono}/{repo}" if dono and repo else None,
        "ramo_padrao": ramo,
        "ultimo_commit": git(raiz, "log", "-1", "--format=%cI"),
        "tags_recentes": tags,
        "sujo": bool(alteracoes),
        "arquivos_alterados": [l.strip() for l in alteracoes[:12]],
        "commits_a_frente_do_remoto": a_frente,
        "commits_atras_do_remoto": atras,
    }


def detectar_licenca(raiz: Path) -> dict:
    achados = [p for p in raiz.iterdir()
               if p.is_file() and re.match(r"(?i)^(licen[cs]e|copying|unlicense)(\..*)?$", p.name)]
    if not achados:
        return {"arquivo": None, "spdx_provavel": None}
    arq = achados[0]
    texto = ler(arq, 40_000)
    for padrao, spdx in LICENCAS:
        if re.search(padrao, texto, re.I):
            return {"arquivo": arq.name, "spdx_provavel": spdx}
    return {"arquivo": arq.name, "spdx_provavel": None}


def analisar_manifestos(raiz: Path, arquivos: list[Path]) -> tuple[dict, Counter, dict, list[str]]:
    """Retorna (manifestos, pontos_de_tipo, evidencias, comandos)."""
    man: dict = {}
    pontos: Counter = Counter()
    ev: dict = defaultdict(list)
    comandos: list[str] = []

    def marca(tipo: str, peso: int, motivo: str) -> None:
        pontos[tipo] += peso
        ev[tipo].append(motivo)

    nomes = {rel(raiz, p): p for p in arquivos}
    por_nome = defaultdict(list)
    for r, p in nomes.items():
        por_nome[p.name].append(p)

    # package.json (raiz)
    pj = raiz / "package.json"
    if pj.exists():
        try:
            d = json.loads(ler(pj))
        except json.JSONDecodeError:
            d = {}
        deps = {**d.get("dependencies", {}), **d.get("devDependencies", {})}
        man["package.json"] = {
            k: d.get(k) for k in
            ("name", "version", "description", "license", "bin", "main", "module",
             "engines", "homepage", "repository", "keywords", "private")
            if d.get(k) is not None
        }
        if d.get("bin"):
            marca("cli", 3, "package.json tem 'bin'")
        elif d.get("main") or d.get("module") or d.get("exports"):
            marca("biblioteca", 2, "package.json exporta main/module/exports")
        if any(k in deps for k in ("electron", "electron-builder", "@tauri-apps/api")):
            marca("app-desktop", 3, "dependência electron/tauri")
        if any(k in deps for k in ("express", "fastify", "koa", "@nestjs/core", "hono")):
            marca("api-servico", 2, "framework de servidor nas dependências")
        if any(k in deps for k in ("react", "vue", "svelte", "next", "nuxt", "astro")):
            marca("app-web", 2, "framework web nas dependências")
        for chave in ("start", "dev", "build", "test", "lint"):
            if chave in d.get("scripts", {}):
                comandos.append(f"npm run {chave}" if chave not in ("start", "test") else f"npm {chave}")

    # pyproject / setup.py
    pp = raiz / "pyproject.toml"
    if pp.exists():
        texto = ler(pp)
        dados = toml_ou_none(pp) or {}
        proj = dados.get("project", {})
        poetry = dados.get("tool", {}).get("poetry", {})
        man["pyproject.toml"] = {
            "name": proj.get("name") or poetry.get("name") or campo_toml(texto, "name"),
            "version": proj.get("version") or poetry.get("version") or campo_toml(texto, "version"),
            "description": proj.get("description") or poetry.get("description") or campo_toml(texto, "description"),
            "requires-python": proj.get("requires-python") or campo_toml(texto, "requires-python"),
            "scripts": list((proj.get("scripts") or poetry.get("scripts") or {}).keys()),
        }
        if man["pyproject.toml"]["scripts"] or re.search(r"\[(project|tool\.poetry)\.scripts\]", texto):
            marca("cli", 3, "pyproject define scripts de linha de comando")
        else:
            marca("biblioteca", 2, "pyproject sem scripts de CLI")
        if re.search(r"(?i)fastapi|flask|django|starlette", texto):
            marca("api-servico", 2, "framework web Python no pyproject")
        if re.search(r"(?i)pyside|pyqt|tkinter|customtkinter|kivy|wxpython|pyinstaller", texto):
            marca("app-desktop", 3, "framework de GUI ou PyInstaller")
    elif (raiz / "setup.py").exists() or (raiz / "requirements.txt").exists():
        man["python"] = {"setup.py": (raiz / "setup.py").exists(),
                         "requirements.txt": (raiz / "requirements.txt").exists()}
        texto_req = ler(raiz / "requirements.txt")
        if re.search(r"(?i)pyside|pyqt|customtkinter|kivy|wxpython", texto_req):
            marca("app-desktop", 3, "framework de GUI em requirements.txt")

    # Cargo
    ct = raiz / "Cargo.toml"
    if ct.exists():
        texto = ler(ct)
        dados = toml_ou_none(ct) or {}
        pac = dados.get("package", {})
        man["Cargo.toml"] = {
            "name": pac.get("name") or campo_toml(texto, "name"),
            "version": pac.get("version") or campo_toml(texto, "version"),
            "description": pac.get("description") or campo_toml(texto, "description"),
            "license": pac.get("license") or campo_toml(texto, "license"),
        }
        if (raiz / "src" / "main.rs").exists() or "[[bin]]" in texto:
            marca("cli", 2, "Cargo com binário (src/main.rs ou [[bin]])")
        if (raiz / "src" / "lib.rs").exists():
            marca("biblioteca", 2, "Cargo com src/lib.rs")
        if re.search(r"(?i)tauri", texto):
            marca("app-desktop", 3, "dependência tauri")

    # Go
    gm = raiz / "go.mod"
    if gm.exists():
        texto = ler(gm)
        m_mod = re.search(r"^module\s+(\S+)", texto, re.M)
        m_go = re.search(r"^go\s+(\S+)", texto, re.M)
        man["go.mod"] = {"module": m_mod.group(1) if m_mod else None,
                         "go": m_go.group(1) if m_go else None}
        if (raiz / "main.go").exists() or (raiz / "cmd").is_dir():
            marca("cli", 2, "Go com main.go ou cmd/")
        else:
            marca("biblioteca", 2, "módulo Go sem main.go/cmd")

    # .NET
    csprojs = [p for p in arquivos if p.suffix.lower() == ".csproj"][:6]
    if csprojs:
        itens = []
        for p in csprojs:
            t = ler(p, 60_000)
            tf = re.findall(r"<TargetFrameworks?>([^<]+)</", t)
            saida = re.search(r"<OutputType>([^<]+)</OutputType>", t)
            itens.append({
                "arquivo": rel(raiz, p), "target": tf[0] if tf else None,
                "output": saida.group(1) if saida else None,
                "wpf_winforms": bool(re.search(r"<Use(WPF|WindowsForms)>\s*true", t, re.I)),
            })
            if re.search(r"<OutputType>\s*WinExe", t, re.I) or re.search(r"<Use(WPF|WindowsForms)>\s*true", t, re.I):
                marca("app-desktop", 3, f"{p.name}: WinExe/WPF/WinForms")
            elif re.search(r"<OutputType>\s*Exe", t, re.I):
                marca("cli", 2, f"{p.name}: OutputType Exe")
            elif "Microsoft.NET.Sdk.Web" in t:
                marca("api-servico", 2, f"{p.name}: SDK Web")
            else:
                marca("biblioteca", 1, f"{p.name}: biblioteca .NET")
            if re.search(r"(?i)BepInEx|MelonLoader|HarmonyLib|0Harmony|Assembly-CSharp", t):
                marca("jogo-ou-mod", 3, f"{p.name}: referências de mod loader/jogo")
        man["dotnet"] = itens

    # Engines de jogo e mods
    sinais_jogo = [
        ("project.godot", "projeto Godot"),
        ("default.project.json", "projeto Rojo/Roblox"),
        ("wally.toml", "pacote Wally/Roblox"),
        ("fxmanifest.lua", "recurso FiveM"),
        ("fabric.mod.json", "mod Fabric"),
        ("mods.toml", "mod Forge"),
        ("plugin.yml", "plugin Bukkit/Spigot"),
    ]
    for nome, motivo in sinais_jogo:
        if nome in por_nome:
            marca("jogo-ou-mod", 4, motivo)
    if (raiz / "ProjectSettings" / "ProjectVersion.txt").exists():
        marca("jogo-ou-mod", 4, "projeto Unity (ProjectSettings/ProjectVersion.txt)")
        man["unity"] = ler(raiz / "ProjectSettings" / "ProjectVersion.txt", 400).strip()
    if any(p.suffix.lower() in (".uproject", ".rbxl", ".rbxlx", ".rbxm", ".toc") for p in arquivos):
        marca("jogo-ou-mod", 4, "arquivo de projeto de engine (.uproject/.rbxl/.toc)")

    # Extensão de navegador
    for p in por_nome.get("manifest.json", [])[:3]:
        if '"manifest_version"' in ler(p, 20_000):
            marca("extensao-navegador", 4, f"{rel(raiz, p)} com manifest_version")
            break

    # API / serviço
    if any(re.match(r"(?i)^(openapi|swagger)\.(ya?ml|json)$", p.name) for p in arquivos):
        marca("api-servico", 3, "arquivo OpenAPI/Swagger")
    if "Dockerfile" in por_nome:
        marca("api-servico", 1, "Dockerfile presente")
        man["docker"] = True
    if any(re.match(r"(?i)^(docker-)?compose\.ya?ml$", p.name) for p in arquivos):
        marca("api-servico", 1, "docker compose presente")
        man["docker_compose"] = True

    # Empacotadores de app
    if "tauri.conf.json" in por_nome:
        marca("app-desktop", 3, "tauri.conf.json")
    if any(p.suffix.lower() in (".iss", ".wxs") for p in arquivos):
        marca("app-desktop", 3, "script de instalador (Inno Setup/WiX)")
    if any(p.suffix.lower() == ".spec" and "Analysis(" in ler(p, 5000) for p in arquivos[:3000]):
        marca("app-desktop", 2, "spec do PyInstaller")

    # Makefile
    mk = raiz / "Makefile"
    if mk.exists():
        alvos = re.findall(r"^([A-Za-z][\w.-]*):(?!=)", ler(mk), re.M)
        comandos += [f"make {a}" for a in alvos[:8]]

    return man, pontos, ev, comandos


def tipo_awesome(raiz: Path) -> tuple[bool, str]:
    if raiz.name.lower().startswith("awesome"):
        return True, "nome da pasta começa com 'awesome'"
    readme = next((p for p in raiz.iterdir() if re.match(r"(?i)^readme\.md$", p.name)), None)
    if readme:
        linhas = [l for l in ler(readme).splitlines() if l.strip()]
        itens = [l for l in linhas if re.match(r"^\s*[-*]\s+\[[^\]]+\]\(http", l)]
        if len(linhas) > 30 and len(itens) / len(linhas) > 0.5:
            return True, "mais da metade das linhas do README são itens de link"
    return False, ""


def info_readme(raiz: Path, arquivos: list[Path]) -> dict:
    candidatos = []
    for p in arquivos:
        r = rel(raiz, p)
        if re.match(r"(?i)^(\.github/|docs/)?readme(\.[\w-]+)?\.(md|markdown|rst|txt)$", r) or re.match(r"(?i)^readme$", r):
            candidatos.append(p)
    if not candidatos:
        return {"existe": False}
    principal = sorted(candidatos, key=lambda p: (len(rel(raiz, p)), rel(raiz, p)))[0]
    texto = ler(principal)
    linhas = texto.splitlines()
    h1 = next((l.lstrip("# ").strip() for l in linhas if re.match(r"^#\s+\S", l)), None)
    gerador = re.search(r"(?i)readme-ai|generated (by|with)|auto-?generated|gerado (por|com|automaticamente)", texto)
    conhecidos = {rel(raiz, p) for p in candidatos}
    derivados = [
        rel(raiz, p) for p in arquivos
        if re.match(r"(?i)^readme(\.[\w-]+)?\.(md|markdown|rst|txt)$", p.name) and rel(raiz, p) not in conhecidos
    ][:15]
    for extra in ("docs/index.md", "docs/index.rst"):
        if (raiz / extra).exists():
            derivados.append(extra)
    return {
        "existe": True,
        "principal": rel(raiz, principal),
        "outros": [rel(raiz, p) for p in candidatos if p != principal],
        "possiveis_documentos_derivados": derivados,
        "linhas": len(linhas),
        "bytes": len(texto.encode("utf-8")),
        "h1": h1,
        "imagens": len(re.findall(r"!\[[^\]]*\]\(|<img\b", texto)),
        "indicio_de_gerador": gerador.group(0) if gerador else None,
        "pendencias_marcadas": len(re.findall(r"(?i)TODO|PENDENTE|em breve|coming soon", texto)),
    }


def readme_fixado_por_testes(raiz: Path, arquivos: list[Path]) -> list[str]:
    """Linhas de testes, CI e automações que citam README/CONTRIBUTING.

    Projetos às vezes fixam em teste o texto do README (títulos exatos, lista de
    arquivos, frases obrigatórias). Reestruturar sem saber disso quebra o CI.
    """
    achados: list[str] = []
    for p in arquivos:
        r = rel(raiz, p)
        em_pasta_de_teste = re.search(r"(^|/)(tests?|__tests__|specs?|e2e|\.github/workflows)/", r)
        nome_de_teste = re.search(r"(^test_.*\.py$|_test\.(go|py)$|\.(test|spec)\.(js|ts|tsx|jsx)$|Tests?\.cs$)", p.name)
        automacao = p.name in ("Makefile", ".pre-commit-config.yaml", "package.json", "tox.ini", "noxfile.py")
        if not (em_pasta_de_teste or nome_de_teste or automacao):
            continue
        try:
            if p.stat().st_size > 300_000:
                continue
        except OSError:
            continue
        for i, linha in enumerate(ler(p).splitlines(), 1):
            if re.search(r"README|CONTRIBUTING", linha):
                achados.append(f"{r}:{i}")
                break
        if len(achados) >= 12:
            break
    return achados


def info_traducoes(raiz: Path, arquivos: list[Path]) -> list[str]:
    achados = []
    for p in arquivos:
        r = rel(raiz, p)
        if re.match(r"(?i)^(readme[._-][A-Za-z]{2,3}([_-][A-Za-z]{2,4})?\.md|[\w./-]*(i18n|translations?)/[\w./-]*readme[\w.-]*\.md)$", r):
            achados.append(r)
    return achados[:20]


def info_midia(raiz: Path, arquivos: list[Path]) -> dict:
    itens = []
    grandes = []
    por_pasta: Counter = Counter()
    for p in arquivos:
        if p.suffix.lower() in EXT_MIDIA:
            r = rel(raiz, p)
            partes = [x.lower() for x in Path(r).parts[:-1]]
            relevante = any(x in DIRS_MIDIA or "screenshot" in x for x in partes) or len(partes) == 0
            tamanho = p.stat().st_size
            if relevante:
                itens.append({"arquivo": r, "kb": round(tamanho / 1024)})
                por_pasta[Path(r).parent.as_posix()] += 1
            if tamanho > LIMITE_GITHUB_IMAGEM and p.suffix.lower() != ".mp4":
                grandes.append(r)
    return {
        "total_relevante": len(itens),
        "por_pasta": dict(por_pasta.most_common(8)),
        "amostra": itens[:25],
        "acima_de_10mb": grandes[:10],
    }


def info_workflows(raiz: Path) -> list[dict]:
    pasta = raiz / ".github" / "workflows"
    if not pasta.is_dir():
        return []
    saida = []
    for p in sorted(pasta.iterdir()):
        if p.suffix.lower() not in (".yml", ".yaml"):
            continue
        t = ler(p, 50_000)
        nome = re.search(r"^name:\s*(.+)$", t, re.M)
        saida.append({
            "arquivo": p.name,
            "nome": nome.group(1).strip(" '\"") if nome else None,
            "release": bool(re.search(r"(?i)action-gh-release|gh release|goreleaser|electron-builder|tauri-action|create-release|softprops", t)),
            "testes": bool(re.search(r"(?i)pytest|npm (run )?test|cargo test|go test|dotnet test|jest|vitest", t)),
            "publica_pacote": bool(re.search(r"(?i)pypi|npm publish|cargo publish|docker/build-push|nuget", t)),
        })
    return saida


def info_comunidade(raiz: Path) -> dict:
    def existe(*caminhos: str) -> str | None:
        for c in caminhos:
            if (raiz / c).exists():
                return c
        return None

    funding_gh = raiz / ".github" / "FUNDING.yml"
    funding_raiz = next((p for p in raiz.iterdir() if p.name.lower() in ("funding.yml", "funding.yaml")), None)
    chaves = []
    alvo = funding_gh if funding_gh.exists() else funding_raiz
    if alvo:
        chaves = [m.group(1) for m in re.finditer(r"^\s*([a-z_]+)\s*:", ler(alvo), re.M)]
    return {
        "CONTRIBUTING": existe("CONTRIBUTING.md", ".github/CONTRIBUTING.md", "docs/CONTRIBUTING.md"),
        "CODE_OF_CONDUCT": existe("CODE_OF_CONDUCT.md", ".github/CODE_OF_CONDUCT.md"),
        "SECURITY": existe("SECURITY.md", ".github/SECURITY.md"),
        "CHANGELOG": existe("CHANGELOG.md", "CHANGELOG", "HISTORY.md", "docs/CHANGELOG.md"),
        "CITATION": existe("CITATION.cff"),
        "AGENTS": existe("AGENTS.md"),
        "CLAUDE": existe("CLAUDE.md"),
        "issue_templates": existe(".github/ISSUE_TEMPLATE", ".github/ISSUE_TEMPLATE.md"),
        "funding": {
            "arquivo": rel(raiz, alvo) if alvo else None,
            "chaves": chaves,
            "no_lugar_certo": bool(funding_gh.exists()),
        },
    }


PADROES_PORTATIL = {
    "appdata_ou_pasta_do_usuario": r"APPDATA|LOCALAPPDATA|SpecialFolder\.(ApplicationData|LocalApplicationData|CommonApplicationData|MyDocuments)|os\.homedir\(|expanduser\(['\"]~|XDG_CONFIG_HOME|Path\.home\(\)",
    "registro_do_windows": r"HKEY_|winreg|Registry\.(CurrentUser|LocalMachine|ClassesRoot)|RegistryKey",
    "menciona_portable": r"(?i)\bportable\b|\bport[aá]til\b",
}


def sinais_portatil(raiz: Path, arquivos: list[Path]) -> dict:
    contagem: Counter = Counter()
    amostras: dict = defaultdict(list)
    lidos = 0
    for p in arquivos:
        if p.suffix.lower() not in EXT_CODIGO:
            continue
        try:
            if p.stat().st_size > 400_000:
                continue
        except OSError:
            continue
        lidos += 1
        if lidos > 3000:
            break
        for i, linha in enumerate(ler(p).splitlines(), 1):
            for nome, padrao in PADROES_PORTATIL.items():
                if re.search(padrao, linha):
                    contagem[nome] += 1
                    if len(amostras[nome]) < 6:
                        amostras[nome].append(f"{rel(raiz, p)}:{i}")
    return {
        "arquivos_de_codigo_lidos": lidos,
        "contagens": dict(contagem),
        "amostras": dict(amostras),
        "nota": "Ausência de sinais não prova que o app seja portátil: teste de verdade antes de prometer 'portátil' no README.",
    }


def linguagens(arquivos: list[Path]) -> dict:
    mapa = {".py": "Python", ".js": "JavaScript", ".ts": "TypeScript", ".tsx": "TypeScript", ".jsx": "JavaScript",
            ".cs": "C#", ".go": "Go", ".rs": "Rust", ".java": "Java", ".kt": "Kotlin", ".cpp": "C++", ".c": "C",
            ".h": "C/C++", ".lua": "Lua", ".gd": "GDScript", ".rb": "Ruby", ".php": "PHP", ".swift": "Swift",
            ".ps1": "PowerShell", ".bat": "Batch", ".html": "HTML", ".css": "CSS"}
    c = Counter(mapa[p.suffix.lower()] for p in arquivos if p.suffix.lower() in mapa)
    return dict(c.most_common(6))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pasta", nargs="?", default=".")
    ap.add_argument("--max-arquivos", type=int, default=20000)
    args = ap.parse_args()

    raiz = Path(args.pasta).resolve()
    if not raiz.is_dir():
        print(f"Pasta não encontrada: {raiz}", file=sys.stderr)
        return 2
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    arquivos, truncado = listar_arquivos(raiz, args.max_arquivos)
    manifestos, pontos, evid, comandos = analisar_manifestos(raiz, arquivos)

    eh_awesome, motivo_awesome = tipo_awesome(raiz)
    if eh_awesome:
        pontos["lista-awesome"] += 4
        evid["lista-awesome"].append(motivo_awesome)
    if not manifestos and not pontos:
        md = [p for p in arquivos if p.suffix.lower() == ".md"]
        if len(md) >= 3:
            pontos["documentacao"] += 2
            evid["documentacao"].append("só Markdown, sem manifesto de código")

    ranking = [(t, n) for t, n in pontos.most_common() if n > 0]
    if ranking:
        topo, nota = ranking[0]
        folga = nota - (ranking[1][1] if len(ranking) > 1 else 0)
        confianca = "alta" if nota >= 4 and folga >= 2 else "média" if nota >= 2 else "baixa"
    else:
        topo, confianca = "desconhecido", "baixa"

    licenca = detectar_licenca(raiz)
    readme = info_readme(raiz, arquivos)
    comunidade = info_comunidade(raiz)
    dados_git = info_git(raiz)
    fixado = readme_fixado_por_testes(raiz, arquivos)
    avisos = []
    if dados_git.get("sujo") and readme.get("existe"):
        avisos.append("Árvore com alterações não commitadas: o README pode carregar trabalho do autor. Não sobrescreva; confirme antes.")
    if dados_git.get("commits_atras_do_remoto"):
        avisos.append(f"A branch está {dados_git['commits_atras_do_remoto']} commit(s) atrás de origin: o README remoto pode ser diferente.")
    if fixado:
        avisos.append("Testes, CI ou automações citam README/CONTRIBUTING: confira o que está fixado antes de reestruturar.")
    if not licenca["arquivo"]:
        avisos.append("Sem arquivo LICENSE na raiz (P0 na auditoria).")
    if comunidade["funding"]["arquivo"] and not comunidade["funding"]["no_lugar_certo"]:
        avisos.append("FUNDING.yml fora de .github/: o GitHub só o lê em .github/FUNDING.yml.")
    if readme.get("indicio_de_gerador"):
        avisos.append("README atual parece gerado por ferramenta: edite o gerador, não o arquivo.")
    if truncado:
        avisos.append(f"Varredura limitada a {args.max_arquivos} arquivos.")

    saida = {
        "pasta": str(raiz),
        "git": dados_git,
        "tipo_provavel": topo,
        "confianca_do_tipo": confianca,
        "candidatos_de_tipo": [{"tipo": t, "pontos": n, "evidencias": evid[t]} for t, n in ranking],
        "manifestos": manifestos,
        "linguagens": linguagens(arquivos),
        "comandos_encontrados": comandos,
        "licenca": licenca,
        "readme_atual": readme,
        "readme_citado_em_testes_ou_ci": fixado,
        "readmes_traduzidos": info_traducoes(raiz, arquivos),
        "midia": info_midia(raiz, arquivos),
        "workflows": info_workflows(raiz),
        "comunidade": comunidade,
        "sinais_de_portatil": sinais_portatil(raiz, arquivos),
        "avisos": avisos,
    }
    print(json.dumps(saida, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
