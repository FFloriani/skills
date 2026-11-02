#!/usr/bin/env python3
"""Roda Gitleaks, OSV-Scanner e Semgrep num projeto e junta o resultado em resumo.json.

Não altera o projeto: os relatórios ficam fora dele. Ferramenta que falha, estoura o
tempo ou não tem o que ler sai como "falhou" ou "nao_checado", nunca como "nada achado".

Uso: python vistoria.py <pasta> [--modo completa|rapida|mudanca] [--base <ref>] [--saida <pasta>]

Configuração opcional em ~/.config/vistoria/config.json:
  {"base": "<pasta das ferramentas e dos relatórios>", "dono_github": "<sua conta do GitHub>"}
Sem ela, a base é ~/.vistoria, as ferramentas vêm do PATH e e_do_dono fica nulo em repositório com remoto.
"""
import argparse
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path


def config_local():
    try:
        dados = json.loads((Path.home() / ".config" / "vistoria" / "config.json").read_text(encoding="utf-8-sig"))
    except (OSError, ValueError):
        return {}
    return dados if isinstance(dados, dict) else {}


CONFIG = config_local()
BASE = Path(CONFIG["base"]).expanduser() if CONFIG.get("base") else Path.home() / ".vistoria"
BIN_PADRAO = BASE / "ferramentas" / "bin"
SAIDA_PADRAO = BASE / "vistorias"
DONO_GITHUB = str(CONFIG.get("dono_github") or "").lower()

PASTAS_GERADAS = {
    ".git", "node_modules", "target", "dist", "build", "out", ".next", ".nuxt", "vendor",
    "__pycache__", ".venv", "venv", "Library", "Temp", "obj", "Logs", ".godot", "Binaries",
    "Intermediate", "Saved", "DerivedDataCache", "rastro",
}
LINGUAGENS = {
    ".js": "javascript", ".jsx": "javascript", ".mjs": "javascript", ".cjs": "javascript",
    ".ts": "typescript", ".tsx": "typescript", ".py": "python", ".rs": "rust", ".go": "go",
    ".java": "java", ".kt": "kotlin", ".swift": "swift", ".cs": "csharp", ".c": "c", ".h": "c",
    ".cpp": "c", ".cc": "c", ".hpp": "c", ".php": "php", ".rb": "ruby", ".lua": "lua",
    ".luau": "luau", ".gd": "gdscript", ".sh": "bash", ".ps1": "powershell", ".tf": "terraform",
    ".vue": "javascript", ".svelte": "javascript", ".html": "html", ".sql": "sql",
}
# Conjuntos que existem no registro do Semgrep (conferidos com --validate em 02/11/2026).
REGRAS_BASE = ["p/owasp-top-ten", "p/security-audit", "p/secrets"]
REGRAS_LINGUAGEM = {
    "javascript": ["p/javascript", "p/nodejs"], "typescript": ["p/typescript", "p/nodejs"],
    "python": ["p/python"], "rust": ["p/rust"], "go": ["p/golang"], "java": ["p/java"],
    "kotlin": ["p/kotlin"], "swift": ["p/swift"], "csharp": ["p/csharp"], "c": ["p/c"],
    "php": ["p/php"], "ruby": ["p/ruby"], "terraform": ["p/terraform"],
}
REGRAS_BIBLIOTECA = {
    "express": "p/expressjs", "react": "p/react", "next": "p/nextjs",
    "flask": "p/flask", "django": "p/django",
}
SEM_REGRAS_SEMGREP = {"lua", "luau", "gdscript", "powershell"}
LOCKFILES = {
    "package-lock.json", "npm-shrinkwrap.json", "yarn.lock", "pnpm-lock.yaml", "bun.lock",
    "Cargo.lock", "poetry.lock", "uv.lock", "Pipfile.lock", "pdm.lock", "go.sum", "go.mod",
    "composer.lock", "Gemfile.lock", "pom.xml", "gradle.lockfile", "packages.lock.json",
    "requirements.txt", "pubspec.lock", "mix.lock", "conan.lock",
}
# Manifesto sem a lista travada ao lado: não dá para saber a versão instalada.
MANIFESTO_PEDE = {
    "package.json": {"package-lock.json", "npm-shrinkwrap.json", "yarn.lock", "pnpm-lock.yaml", "bun.lock"},
    "Cargo.toml": {"Cargo.lock"},
    "pyproject.toml": {"poetry.lock", "uv.lock", "pdm.lock", "requirements.txt"},
    "Pipfile": {"Pipfile.lock"},
    "composer.json": {"composer.lock"},
    "Gemfile": {"Gemfile.lock"},
}
ARQUIVOS_QUE_ESCONDEM = {
    ".gitleaksignore": "Gitleaks", ".semgrepignore": "Semgrep", "osv-scanner.toml": "OSV-Scanner",
    ".osv-scanner.toml": "OSV-Scanner",
}
ORDEM_SEVERIDADE = {"critico": 0, "alto": 1, "medio": 2, "baixo": 3}


def ambiente(pasta_bin):
    env = os.environ.copy()
    env.update({
        "SEMGREP_SEND_METRICS": "off", "PYTHONUTF8": "1", "GIT_TERMINAL_PROMPT": "0",
        "GIT_OPTIONAL_LOCKS": "0",
        # Vale também para o git que o Gitleaks chama: pasta com dono antigo do Windows
        # continua legível e o repositório não dispara programa pelo fsmonitor.
        "GIT_CONFIG_COUNT": "2",
        "GIT_CONFIG_KEY_0": "core.fsmonitor", "GIT_CONFIG_VALUE_0": "false",
        "GIT_CONFIG_KEY_1": "safe.directory", "GIT_CONFIG_VALUE_1": "*",
    })
    if pasta_bin:
        env["PATH"] = str(pasta_bin) + os.pathsep + env.get("PATH", "")
    return env


def achar_ferramentas():
    """VISTORIA_BIN troca a pasta das ferramentas; com ele, nada vem do PATH."""
    forcada = os.environ.get("VISTORIA_BIN")
    pasta = Path(forcada) if forcada else BIN_PADRAO
    achadas = {}
    for nome in ("gitleaks", "osv-scanner", "semgrep"):
        exe = pasta / (nome + (".exe" if os.name == "nt" else ""))
        if exe.exists():
            achadas[nome] = str(exe)
        elif not forcada and shutil.which(nome):
            achadas[nome] = shutil.which(nome)
    return achadas, pasta


def rodar(cmd, cwd, env, limite):
    """Devolve (código, saída, erro). Código None quer dizer que estourou o tempo."""
    criar = subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
    try:
        p = subprocess.Popen(
            cmd, cwd=cwd, env=env, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace", creationflags=criar,
        )
    except OSError as e:
        return -1, "", str(e)
    try:
        out, err = p.communicate(timeout=limite)
        return p.returncode, out, err
    except subprocess.TimeoutExpired:
        if os.name == "nt":
            subprocess.run(["taskkill", "/T", "/F", "/PID", str(p.pid)], capture_output=True)
        else:
            p.kill()
        p.communicate()
        return None, "", ""


def git(pasta, env, *args):
    r = subprocess.run(
        ["git", "-C", str(pasta), *args], env=env, capture_output=True, text=True,
        encoding="utf-8", errors="replace", stdin=subprocess.DEVNULL,
    )
    return r.returncode, r.stdout, r.stderr


def relativo(caminho, pasta):
    c = str(caminho).replace("\\", "/")
    p = str(pasta).replace("\\", "/").rstrip("/")
    if c.lower().startswith(p.lower() + "/"):
        c = c[len(p) + 1:]
    return c[2:] if c.startswith("./") else c


def config_git_perigosa(raiz):
    """Linhas do .git/config que fariam o git executar programa só por ler o repositório."""
    suspeitas = []
    try:
        texto = (Path(raiz) / ".git" / "config").read_text(encoding="utf-8", errors="replace")
    except OSError:
        return suspeitas
    for linha in texto.splitlines():
        m = re.match(r"\s*(fsmonitor|textconv|clean|smudge|process|external|command)\s*=\s*(.*)", linha, re.I)
        if m and m.group(2).strip().lower() not in {"true", "false"} and "git-lfs" not in m.group(2):
            suspeitas.append(linha.strip())
    return suspeitas


def listar_arquivos(pasta, eh_git, env):
    if eh_git:
        cod, out, _ = git(pasta, env, "ls-files", "-co", "--exclude-standard", "-z")
        if cod == 0:
            return [a for a in out.split("\0") if a and not (set(Path(a).parts) & PASTAS_GERADAS)]
    arquivos = []
    for raiz, pastas, nomes in os.walk(pasta):
        pastas[:] = [p for p in pastas if p not in PASTAS_GERADAS]
        arquivos += [relativo(Path(raiz) / n, pasta) for n in nomes]
    return arquivos


def detectar_jogo(arquivos):
    nomes = {a.lower().rsplit("/", 1)[-1] for a in arquivos if a.count("/") <= 3}
    if any(a.lower().endswith((".luau", ".rbxl", ".rbxlx")) for a in arquivos) or \
            any(n.endswith(".project.json") for n in nomes) or "wally.toml" in nomes:
        return "roblox"
    if "projectversion.txt" in nomes and any(a.lower().endswith(".cs") for a in arquivos):
        return "unity"
    if "project.godot" in nomes:
        return "godot"
    if any(n.endswith(".uproject") for n in nomes):
        return "unreal"
    return None


def ler_projeto(pasta, env):
    cod, out, _ = git(pasta, env, "rev-parse", "--show-toplevel")
    eh_git = cod == 0
    info = {"git": eh_git, "raiz_git": out.strip() if eh_git else None, "commits": False,
            "remoto": None, "dono_remoto": None, "e_do_dono": None}
    if eh_git:
        info["commits"] = git(pasta, env, "rev-parse", "--verify", "-q", "HEAD")[0] == 0
        _, remotos, _ = git(pasta, env, "remote", "-v")
        origem = re.search(r"^origin\s+(\S+)", remotos, re.M) or re.search(r"^\S+\s+(\S+)", remotos, re.M)
        if origem:
            url = origem.group(1)
            # Tira usuário e token que a URL possa trazer.
            info["remoto"] = re.sub(r"//[^/@]+@", "//", url)
            dono = re.search(r"[:/]([^/:]+)/[^/]+?(?:\.git)?/?$", url)
            info["dono_remoto"] = dono.group(1) if dono else None
            # Sem conta configurada não dá para saber de quem é: nulo, não falso.
            info["e_do_dono"] = (info["dono_remoto"] or "").lower() == DONO_GITHUB if DONO_GITHUB else None
        else:
            info["e_do_dono"] = True  # repositório só local
    else:
        info["e_do_dono"] = True  # pasta sem git, sem remoto de ninguém

    arquivos = listar_arquivos(pasta, eh_git, env)
    linguagens, linhas, de_codigo = {}, 0, 0
    for a in arquivos:
        lang = LINGUAGENS.get(Path(a).suffix.lower())
        if not lang:
            continue
        linguagens[lang] = linguagens.get(lang, 0) + 1
        de_codigo += 1
        try:
            alvo = Path(pasta) / a
            if alvo.stat().st_size < 2_000_000:
                linhas += alvo.read_bytes().count(b"\n")
        except OSError:
            pass
    info.update({
        "arquivos": len(arquivos), "arquivos_de_codigo": de_codigo, "linhas_de_codigo": linhas,
        "linguagens": dict(sorted(linguagens.items(), key=lambda kv: -kv[1])),
        "jogo": detectar_jogo(arquivos),
        # Corte que o próprio Claude Security usa: "alguns centos" de arquivos dá para ler inteiro.
        "tamanho": "pequeno" if de_codigo <= 300 else "grande",
    })
    return info, arquivos


def arquivos_mudados(pasta, base, env):
    """Arquivos diferentes da base, mais os novos ainda fora do git."""
    if git(pasta, env, "rev-parse", "--verify", "-q", "HEAD")[0] == 0:
        cod, out, err = git(pasta, env, "diff", "--name-only", "--no-renames", "-z", base, "--relative")
        if cod != 0:
            return None, err.strip()
        lista = out.split("\0")
    else:
        lista = git(pasta, env, "ls-files", "-z")[1].split("\0")
    lista += git(pasta, env, "ls-files", "-o", "--exclude-standard", "-z")[1].split("\0")
    return sorted({a for a in lista if a and (Path(pasta) / a).is_file()}), ""


def nova_ferramenta():
    return {"situacao": "pulou", "motivo": "", "tempo_s": 0, "achados": 0}


def falha(reg, motivo):
    reg["situacao"] = "falhou"
    reg["motivo"] = motivo


def resumir_erro(err, limite=400):
    err = re.sub(r"\x1b\[[0-9;]*m", "", err or "").strip()
    return err[-limite:]


def carregar_json(caminho):
    with open(caminho, encoding="utf-8", errors="replace") as f:
        return json.load(f)


def config_gitleaks(pasta_temp):
    pastas = "|".join(re.escape(p) for p in sorted(PASTAS_GERADAS - {".git", "rastro"}))
    caminho = Path(pasta_temp) / "gitleaks.toml"
    caminho.write_text(
        "[extend]\nuseDefault = true\n\n[allowlist]\n"
        'description = "pastas geradas"\n'
        f"paths = ['''(^|[\\\\/])({pastas})[\\\\/]''']\n",
        encoding="utf-8",
    )
    return str(caminho)


def rodar_gitleaks(exe, pasta, info, modo, base, mudados, config_perigosa, brutos, temp, env, limite):
    reg = nova_ferramenta()
    if not exe:
        falha(reg, "programa não encontrado")
        return reg, []
    inicio = time.time()
    cfg = config_gitleaks(temp)
    # Sem --exit-code 0 o programa usa o código 1 também para "achou"; assim, 0 é sempre "rodou".
    comum = ["--redact", "--no-banner", "--exit-code", "0", "--log-level", "error", "-f", "json"]
    tarefas = [("arquivos", [exe, "dir", ".", "-c", cfg, "--max-target-megabytes", "20", *comum])]
    avisos = []
    pode_historia = info["git"] and info["commits"] and not config_perigosa
    if pode_historia and modo != "mudanca":
        tarefas.append(("historia", [exe, "git", ".", *comum]))
    elif pode_historia and base != "HEAD":
        tarefas.append(("historia", [exe, "git", ".", "--log-opts", f"{base}..HEAD", *comum]))
    elif modo != "mudanca":
        if config_perigosa:
            avisos.append("história do git não lida: a configuração do repositório pode executar programa")
        elif not info["git"]:
            avisos.append("história não lida: a pasta não usa git")
        else:
            avisos.append("história não lida: o repositório ainda não tem commit")

    vistos = {}
    for rotulo, cmd in tarefas:
        saida = brutos / f"gitleaks-{rotulo}.json"
        cod, _, err = rodar([*cmd, "-r", str(saida)], pasta, env, limite)
        if cod is None:
            falha(reg, f"estourou o limite de {limite} s em {rotulo}")
            break
        if cod != 0:
            falha(reg, f"saiu com código {cod} em {rotulo}: {resumir_erro(err)}")
            break
        try:
            registros = carregar_json(saida)
        except (OSError, ValueError) as e:
            falha(reg, f"relatório ilegível em {rotulo}: {e}")
            break
        for r in registros:
            arquivo = relativo(r.get("File", ""), pasta)
            if modo == "mudanca" and rotulo == "arquivos" and arquivo not in mudados:
                continue
            chave = (r.get("RuleID"), arquivo, r.get("StartLine"))
            item = vistos.setdefault(chave, {
                "ferramenta": "gitleaks", "severidade": "alto", "arquivo": arquivo,
                "linha": r.get("StartLine"), "regra": r.get("RuleID"), "titulo": r.get("Description"),
                "onde": [], "commits": 0,
            })
            if rotulo not in item["onde"]:
                item["onde"].append(rotulo)
            if r.get("Commit"):
                item["commits"] += 1
                item["commit_exemplo"] = r["Commit"][:10]
    achados = list(vistos.values())
    for a in achados:
        a["ignorado_pelo_git"] = bool(info["git"]) and a["onde"] == ["arquivos"] and \
            git(pasta, env, "check-ignore", "-q", "--", a["arquivo"])[0] == 0
        if a["ignorado_pelo_git"]:
            # .env ignorado pelo git fica só na máquina: ainda é segredo, mas não vazou.
            a["severidade"] = "baixo"
    reg["tempo_s"] = round(time.time() - inicio, 1)
    reg["achados"] = len(achados)
    if reg["situacao"] != "falhou":
        reg["situacao"] = "ok"
    if avisos:
        reg["avisos"] = avisos
    return reg, achados


def severidade_cvss(nota):
    try:
        n = float(nota)
    except (TypeError, ValueError):
        return "medio"
    return "critico" if n >= 9 else "alto" if n >= 7 else "medio" if n >= 4 else "baixo"


def menor_correcao(vuln, pacote):
    versoes = []
    for afetado in vuln.get("affected", []):
        if afetado.get("package", {}).get("name") != pacote:
            continue
        for faixa in afetado.get("ranges", []):
            versoes += [e["fixed"] for e in faixa.get("events", []) if "fixed" in e]
    return versoes[0] if len(versoes) == 1 else sorted(set(versoes))[-3:] or None


def rodar_osv(exe, pasta, modo, mudados, arquivos, brutos, env, limite):
    reg = nova_ferramenta()
    if not exe:
        falha(reg, "programa não encontrado")
        return reg, []
    if modo == "mudanca" and not any(Path(a).name in LOCKFILES | set(MANIFESTO_PEDE) for a in mudados):
        reg["motivo"] = "nenhuma lista de dependências mudou"
        return reg, []
    nomes_por_pasta = {}
    for a in arquivos:
        p = Path(a)
        nomes_por_pasta.setdefault(str(p.parent), set()).add(p.name)
    sem_lista = [
        str(Path(d) / manifesto).replace("\\", "/")
        for d, nomes in nomes_por_pasta.items()
        for manifesto, pede in MANIFESTO_PEDE.items()
        if manifesto in nomes and not nomes & pede
    ]
    if sem_lista:
        reg["manifestos_sem_lista_travada"] = sem_lista

    inicio = time.time()
    saida = brutos / "osv.json"
    cod, _, err = rodar(
        [exe, "scan", "source", "-r", ".", "--format", "json", "--output-file", str(saida), "--verbosity", "error"],
        pasta, env, limite,
    )
    reg["tempo_s"] = round(time.time() - inicio, 1)
    if cod is None:
        falha(reg, f"estourou o limite de {limite} s")
        return reg, []
    if cod == 128:
        reg["situacao"] = "nao_checado"
        reg["motivo"] = "não achou lista de dependências que saiba ler"
        return reg, []
    if cod not in (0, 1):
        falha(reg, f"saiu com código {cod}: {resumir_erro(err)}")
        return reg, []
    try:
        dados = carregar_json(saida)
    except (OSError, ValueError) as e:
        falha(reg, f"relatório ilegível: {e}")
        return reg, []

    achados, fontes = [], set()
    for resultado in dados.get("results", []):
        fonte = relativo(resultado.get("source", {}).get("path", ""), pasta)
        fontes.add(fonte)
        for pacote in resultado.get("packages", []):
            info = pacote.get("package", {})
            vulns = {v.get("id"): v for v in pacote.get("vulnerabilities", [])}
            for grupo in pacote.get("groups", []):
                ids = grupo.get("ids", [])
                principal = vulns.get(ids[0], {}) if ids else {}
                achados.append({
                    "ferramenta": "osv-scanner",
                    "severidade": severidade_cvss(grupo.get("max_severity")),
                    "arquivo": fonte, "linha": None,
                    "regra": ids[0] if ids else None, "outros_ids": grupo.get("aliases", []),
                    "titulo": f"{info.get('name')} {info.get('version')}: {principal.get('summary') or 'falha conhecida'}",
                    "pacote": info.get("name"), "versao": info.get("version"),
                    "ecossistema": info.get("ecosystem"), "nota_cvss": grupo.get("max_severity") or None,
                    "corrigida_em": menor_correcao(principal, info.get("name")),
                })
    reg["listas_lidas"] = sorted(fontes)
    reg["achados"] = len(achados)
    reg["situacao"] = "ok"
    return reg, achados


def regras_semgrep(pasta, info, arquivos):
    regras = list(REGRAS_BASE)
    for lang in info["linguagens"]:
        regras += REGRAS_LINGUAGEM.get(lang, [])
    deps = ""
    for a in arquivos:
        if Path(a).name in {"package.json", "requirements.txt", "pyproject.toml", "Pipfile"}:
            try:
                deps += (Path(pasta) / a).read_text(encoding="utf-8", errors="replace").lower()
            except OSError:
                pass
    for biblioteca, regra in REGRAS_BIBLIOTECA.items():
        if re.search(rf"[\"'\s^]{re.escape(biblioteca)}[\"'\s=<>~!\[]", deps):
            regras.append(regra)
    if any(Path(a).name.lower().startswith("dockerfile") for a in arquivos):
        regras.append("p/dockerfile")
    if any(a.startswith(".github/workflows/") for a in arquivos):
        regras.append("p/github-actions")
    return list(dict.fromkeys(regras))


def rodar_semgrep(exe, pasta, info, modo, mudados, arquivos, config_perigosa, brutos, env, limite):
    reg = nova_ferramenta()
    if not exe:
        falha(reg, "programa não encontrado")
        return reg, []
    regras = regras_semgrep(pasta, info, arquivos)
    reg["regras"] = regras
    cmd = [exe, "scan", "--metrics=off", "--json", "--quiet", "--timeout", "30"]
    for r in regras:
        cmd += ["--config", r]
    if config_perigosa:
        cmd.append("--no-git-ignore")
    saida = brutos / "semgrep.json"
    cmd += ["--output", str(saida)]
    # Lista longa não cabe na linha de comando do Windows: lê tudo e filtra depois.
    if modo == "mudanca" and sum(len(a) + 3 for a in mudados) < 20000:
        cmd += ["--", *mudados]
    else:
        cmd.append(".")
    inicio = time.time()
    cod, _, err = rodar(cmd, pasta, env, limite)
    reg["tempo_s"] = round(time.time() - inicio, 1)
    if cod is None:
        falha(reg, f"estourou o limite de {limite} s")
        return reg, []
    if cod != 0:
        falha(reg, f"saiu com código {cod}: {resumir_erro(err)}")
        return reg, []
    try:
        dados = carregar_json(saida)
    except (OSError, ValueError) as e:
        falha(reg, f"relatório ilegível: {e}")
        return reg, []

    achados, vistos = [], set()
    nivel = {"ERROR": "alto", "WARNING": "medio", "INFO": "baixo"}
    for r in dados.get("results", []):
        arquivo = relativo(r.get("path", ""), pasta)
        linha = r.get("start", {}).get("line")
        chave = (r.get("check_id"), arquivo, linha)
        if chave in vistos or (modo == "mudanca" and arquivo not in mudados):
            continue
        vistos.add(chave)
        extra = r.get("extra", {})
        meta = extra.get("metadata", {}) or {}
        achados.append({
            "ferramenta": "semgrep", "severidade": nivel.get(extra.get("severity"), "medio"),
            "arquivo": arquivo, "linha": linha, "regra": r.get("check_id"),
            "titulo": re.sub(r"\s+", " ", extra.get("message", ""))[:400],
            "cwe": meta.get("cwe"), "confianca": meta.get("confidence"),
        })
    # O relatório cru traz a linha do código, que pode ser o próprio segredo.
    for r in dados.get("results", []):
        extra = r.get("extra", {})
        for campo in ("lines", "metavars", "fingerprint", "dataflow_trace"):
            extra.pop(campo, None)
    saida.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")

    lidos = dados.get("paths", {}).get("scanned", [])
    reg["arquivos_lidos"] = len(lidos)
    erros = dados.get("errors", [])
    if erros:
        reg["arquivos_com_erro"] = len(erros)
    reg["achados"] = len(achados)
    if lidos:
        reg["situacao"] = "ok"
    else:
        reg["situacao"] = "nao_checado"
        reg["motivo"] = "nenhum arquivo foi lido"
    return reg, achados


def pontos_sem_cobertura(info, ferramentas, arquivos, pasta):
    faltas = []
    for lang in info["linguagens"]:
        if lang in SEM_REGRAS_SEMGREP:
            faltas.append(f"{info['linguagens'][lang]} arquivo(s) em {lang}: o Semgrep não tem conjunto de regras dessa linguagem")
    nomes = {Path(a).name for a in arquivos}
    for nome, quem in ARQUIVOS_QUE_ESCONDEM.items():
        if nome in nomes:
            faltas.append(f"o projeto tem {nome}: o que estiver lá não aparece no {quem}")
    if (Path(pasta) / ".gitleaks.toml").exists():
        faltas.append("o projeto tem .gitleaks.toml: pode ter tirado regras da leitura da história")
    osv = ferramentas.get("osv-scanner", {})
    for m in osv.get("manifestos_sem_lista_travada", []):
        faltas.append(f"{m} não tem lista travada ao lado: as versões instaladas não foram conferidas")
    gl = ferramentas.get("gitleaks", {})
    faltas += gl.get("avisos", [])
    if info["git"]:
        faltas.append("commits desfeitos que ainda estão guardados na pasta .git não são lidos pelo Gitleaks")
    faltas.append("arquivos acima de 20 MB e pastas geradas (node_modules, target, dist...) ficam fora da leitura de segredos nos arquivos")
    faltas.append("pastas de teste e o que está no .semgrepignore padrão ficam fora do Semgrep")
    return faltas


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("pasta")
    ap.add_argument("--modo", choices=["completa", "rapida", "mudanca"], default="completa")
    ap.add_argument("--base", default="HEAD", help="no modo mudanca, a referência de comparação")
    ap.add_argument("--saida", help="pasta dos relatórios (padrão: <base>/vistorias)")
    ap.add_argument("--limite-seg", type=int, default=1800, help="limite de tempo por ferramenta")
    args = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    pasta = Path(args.pasta).resolve()
    if not pasta.is_dir():
        print(f"Pasta não existe: {pasta}", file=sys.stderr)
        return 2
    agora = datetime.datetime.now()
    saida = Path(args.saida) if args.saida else (
        SAIDA_PADRAO / pasta.name / f"{agora:%Y-%m-%d_%H%M%S}_{args.modo}")
    try:
        saida.resolve().relative_to(pasta)
        print("A pasta dos relatórios não pode ficar dentro do projeto.", file=sys.stderr)
        return 2
    except ValueError:
        pass
    brutos = saida / "brutos"
    brutos.mkdir(parents=True, exist_ok=True)

    exes, pasta_bin = achar_ferramentas()
    env = ambiente(pasta_bin if pasta_bin.exists() else None)
    info, arquivos = ler_projeto(pasta, env)
    perigosa = config_git_perigosa(info["raiz_git"]) if info["git"] else []

    resumo = {
        "quando": agora.isoformat(timespec="seconds"), "modo": args.modo, "pasta": str(pasta),
        "projeto": pasta.name, "saida": str(saida), "info": info, "ferramentas": {}, "achados": [],
    }
    if perigosa:
        resumo["config_git_perigosa"] = perigosa

    mudados = []
    if args.modo == "mudanca":
        if not info["git"]:
            resumo["erro"] = "o modo mudanca precisa de git, e esta pasta não usa"
        else:
            mudados, erro = arquivos_mudados(pasta, args.base, env)
            if mudados is None:
                resumo["erro"] = f"não consegui comparar com {args.base}: {erro}"
            else:
                resumo["base"] = args.base
                resumo["arquivos_mudados"] = mudados
                if not mudados:
                    resumo["erro"] = "nada mudou em relação à base"

    if "erro" not in resumo:
        with tempfile.TemporaryDirectory(prefix="vistoria-") as temp:
            passos = [
                ("gitleaks", lambda: rodar_gitleaks(exes.get("gitleaks"), pasta, info, args.modo, args.base,
                                                     set(mudados), perigosa, brutos, temp, env, args.limite_seg)),
                ("osv-scanner", lambda: rodar_osv(exes.get("osv-scanner"), pasta, args.modo, mudados, arquivos,
                                                  brutos, env, args.limite_seg)),
                ("semgrep", lambda: rodar_semgrep(exes.get("semgrep"), pasta, info, args.modo, mudados,
                                                  arquivos, perigosa, brutos, env, args.limite_seg)),
            ]
            for nome, passo in passos:
                try:
                    reg, achados = passo()
                except Exception as e:  # uma ferramenta não pode derrubar as outras
                    reg, achados = {"situacao": "falhou", "motivo": f"erro no script: {e}", "tempo_s": 0, "achados": 0}, []
                resumo["ferramentas"][nome] = reg
                resumo["achados"] += achados

        resumo["achados"].sort(key=lambda a: (ORDEM_SEVERIDADE.get(a["severidade"], 9), a["arquivo"], a.get("linha") or 0))
        for i, a in enumerate(resumo["achados"], 1):
            a["id"] = f"A{i}"
        por_linha = {}
        for a in resumo["achados"]:
            if a.get("linha"):
                por_linha.setdefault((a["arquivo"], a["linha"]), []).append(a["id"])
        for a in resumo["achados"]:
            mesma = [i for i in por_linha.get((a["arquivo"], a.get("linha")), []) if i != a["id"]]
            if mesma:
                a["mesma_linha"] = mesma
        resumo["nao_coberto"] = pontos_sem_cobertura(info, resumo["ferramentas"], arquivos, pasta)

    caminho = saida / "resumo.json"
    caminho.write_text(json.dumps(resumo, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"Projeto: {pasta.name} | modo: {args.modo} | {info['arquivos_de_codigo']} arquivos de código, {info['linhas_de_codigo']} linhas")
    if "erro" in resumo:
        print(f"Não rodou: {resumo['erro']}")
    for nome, reg in resumo["ferramentas"].items():
        nota = f" ({reg['motivo']})" if reg.get("motivo") else ""
        print(f"- {nome}: {reg['situacao']}, {reg['achados']} achado(s), {reg['tempo_s']} s{nota}")
    print(f"Resumo: {caminho}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
