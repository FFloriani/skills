#!/usr/bin/env python3
"""Gera um mapa interativo (um arquivo HTML) a partir de pontos num CSV.

CSV com colunas x,y e, opcionalmente, categoria, nome, descricao. x e y já no plano do mapa
visto de cima. O HTML tem zoom (roda do mouse), arrastar, filtro por categoria e busca por nome.

Uso:
    python mapa.py pontos.csv --saida mapa.html
    python mapa.py pontos.csv --saida mapa.html --fundo minimapa.png --limites xmin,ymin,xmax,ymax
    python mapa.py pontos.csv --saida mapa.html --y-para-baixo   (Godot 2D, GameMaker, RPG Maker)

--limites diz a que coordenadas do mundo correspondem os cantos da imagem de fundo.
Sem --y-para-baixo, y maior fica mais para cima (norte), como em Unity (X,Z) e Unreal (X,Y).
"""
from __future__ import annotations

import argparse
import base64
import csv
import html
import json
import mimetypes
import sys
from pathlib import Path

CORES = ["#e6194b", "#3cb44b", "#4363d8", "#f58231", "#911eb4", "#42d4f4", "#f032e6",
         "#9a6324", "#469990", "#800000", "#808000", "#000075", "#bfef45", "#fabed4"]


def configurar_saida() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            if stream.isatty():
                stream.reconfigure(errors="replace")
            else:
                stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def numero(texto: str) -> float:
    return float(str(texto).strip().replace(",", "."))


def main(argv: list[str]) -> int:
    configurar_saida()
    ap = argparse.ArgumentParser(description="Mapa interativo a partir de pontos (CSV).")
    ap.add_argument("csv")
    ap.add_argument("--saida", required=True)
    ap.add_argument("--titulo", default=None)
    ap.add_argument("--fundo", help="imagem do minimapa ou mapa-múndi (PNG/JPG)")
    ap.add_argument("--limites", help="xmin,ymin,xmax,ymax do mundo nos cantos da imagem (ou da área do mapa)")
    ap.add_argument("--y-para-baixo", action="store_true", help="y maior fica mais para baixo")
    args = ap.parse_args(argv)

    pontos = []
    with open(args.csv, newline="", encoding="utf-8-sig") as f:
        for i, linha in enumerate(csv.DictReader(f), 2):
            try:
                pontos.append({"x": numero(linha["x"]), "y": numero(linha["y"]),
                               "cat": (linha.get("categoria") or "outros").strip() or "outros",
                               "nome": (linha.get("nome") or "").strip(),
                               "desc": (linha.get("descricao") or "").strip()})
            except (KeyError, ValueError):
                print(f"  linha {i} ignorada: x/y inválidos", file=sys.stderr)
    if not pontos:
        print("Nenhum ponto válido no CSV (precisa das colunas x e y).", file=sys.stderr)
        return 2

    if args.limites:
        xmin, ymin, xmax, ymax = (numero(v) for v in args.limites.split(","))
    else:
        xs, ys = [p["x"] for p in pontos], [p["y"] for p in pontos]
        mx = (max(xs) - min(xs)) * 0.05 or 10
        my = (max(ys) - min(ys)) * 0.05 or 10
        xmin, xmax, ymin, ymax = min(xs) - mx, max(xs) + mx, min(ys) - my, max(ys) + my
    largura, altura = xmax - xmin, ymax - ymin
    if largura <= 0 or altura <= 0:
        print("Limites inválidos.", file=sys.stderr)
        return 2

    def tela(p):
        sx = p["x"] - xmin
        sy = (p["y"] - ymin) if args.y_para_baixo else (ymax - p["y"])
        return sx, sy

    categorias = sorted({p["cat"] for p in pontos})
    cor = {c: CORES[i % len(CORES)] for i, c in enumerate(categorias)}
    raio = max(largura, altura) / 250

    fundo = ""
    if args.fundo:
        img = Path(args.fundo)
        dados = img.read_bytes()
        if len(dados) > 15 * 1024 * 1024:
            print("Aviso: imagem de fundo grande; o HTML vai ficar pesado.", file=sys.stderr)
        tipo = mimetypes.guess_type(img.name)[0] or "image/png"
        uri = f"data:{tipo};base64,{base64.b64encode(dados).decode()}"
        fundo = f'<image href="{uri}" x="0" y="0" width="{largura}" height="{altura}" preserveAspectRatio="none"/>'

    marcas = []
    for p in pontos:
        sx, sy = tela(p)
        dica = html.escape(f"{p['nome']} ({p['cat']})" + (f" — {p['desc']}" if p["desc"] else "")
                           + f"  [x={p['x']:g}, y={p['y']:g}]")
        marcas.append(f'<circle class="p" data-cat="{html.escape(p["cat"])}" data-nome="{html.escape(p["nome"].lower())}" '
                      f'cx="{sx:.3f}" cy="{sy:.3f}" r="{raio:.3f}" fill="{cor[p["cat"]]}"><title>{dica}</title></circle>')

    legenda = "".join(
        f'<label><input type="checkbox" checked data-cat="{html.escape(c)}"> '
        f'<span style="color:{cor[c]}">&#9679;</span> {html.escape(c)} '
        f'({sum(1 for p in pontos if p["cat"] == c)})</label>'
        for c in categorias)
    titulo = html.escape(args.titulo or Path(args.csv).stem)

    pagina = f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titulo}</title>
<style>
 body{{margin:0;font-family:system-ui,sans-serif;display:flex;height:100vh;background:#1b1d21;color:#e8e8e8}}
 #lado{{width:240px;padding:12px;overflow:auto;background:#24272d;box-sizing:border-box}}
 #lado label{{display:block;margin:4px 0;cursor:pointer}}
 #busca{{width:100%;padding:6px;box-sizing:border-box;margin:8px 0;background:#1b1d21;color:#e8e8e8;border:1px solid #444}}
 svg{{flex:1;cursor:grab;background:#2c3038}}
 circle.p{{stroke:#000;stroke-width:{raio * 0.25:.3f}}} circle.oculto{{display:none}}
 circle.achado{{stroke:#fff;stroke-width:{raio * 0.6:.3f}}}
 small{{color:#9aa}}
</style></head><body>
<div id="lado"><b>{titulo}</b><br><small>{len(pontos)} pontos · roda do mouse: zoom · arraste para mover</small>
<input id="busca" placeholder="buscar por nome">{legenda}</div>
<svg id="mapa" viewBox="0 0 {largura} {altura}" xmlns="http://www.w3.org/2000/svg">{fundo}{''.join(marcas)}</svg>
<script>
const svg=document.getElementById('mapa');let vb={json.dumps([0, 0, largura, altura])};
function aplicar(){{svg.setAttribute('viewBox',vb.join(' '));}}
svg.addEventListener('wheel',e=>{{e.preventDefault();const r=svg.getBoundingClientRect();
 const fx=(e.clientX-r.left)/r.width,fy=(e.clientY-r.top)/r.height,k=e.deltaY<0?0.8:1.25;
 const nw=vb[2]*k,nh=vb[3]*k;vb=[vb[0]+(vb[2]-nw)*fx,vb[1]+(vb[3]-nh)*fy,nw,nh];aplicar();}},{{passive:false}});
let arr=null;svg.addEventListener('mousedown',e=>{{arr=[e.clientX,e.clientY];svg.style.cursor='grabbing';}});
window.addEventListener('mouseup',()=>{{arr=null;svg.style.cursor='grab';}});
window.addEventListener('mousemove',e=>{{if(!arr)return;const r=svg.getBoundingClientRect();
 vb[0]-=(e.clientX-arr[0])*vb[2]/r.width;vb[1]-=(e.clientY-arr[1])*vb[3]/r.height;arr=[e.clientX,e.clientY];aplicar();}});
const pts=[...document.querySelectorAll('circle.p')];
function filtrar(){{const on=new Set([...document.querySelectorAll('#lado input[type=checkbox]')].filter(c=>c.checked).map(c=>c.dataset.cat));
 const q=document.getElementById('busca').value.trim().toLowerCase();
 pts.forEach(p=>{{const vis=on.has(p.dataset.cat);p.classList.toggle('oculto',!vis);p.classList.toggle('achado',vis&&q!==''&&p.dataset.nome.includes(q));}});}}
document.querySelectorAll('#lado input').forEach(i=>i.addEventListener('input',filtrar));
</script></body></html>"""
    Path(args.saida).write_text(pagina, encoding="utf-8")
    print(f"Mapa com {len(pontos)} pontos em {len(categorias)} categorias gravado em {Path(args.saida).resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
