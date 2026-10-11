# Assets e modelos: extrair para estudar, criar o seu do zero

Asset é qualquer arquivo de conteúdo do jogo: modelo 3D (a malha, ou *mesh*, feita de triângulos),
textura (imagem aplicada sobre o modelo), sprite (imagem 2D de personagem ou objeto), animação e
som. Aqui o asset extraído serve de referência de estudo: dele saem números e observações técnicas
que guiam o asset que o usuário cria do zero ou a partir de uma base licenciada.

## Sumário

1. Regras antes de abrir qualquer arquivo
2. Extrair por engine
3. Abrir no Blender
4. Ficha de referência visual
5. Como medir cada campo
6. Usar a referência do jeito certo
7. Por que alterar o asset extraído não o torna seu
8. O atalho legítimo: partir de uma base licenciada

## 1. Regras antes de abrir qualquer arquivo

- Trabalhe na cópia em `estudo/<jogo>/copia/` e mande a saída para `estudo/<jogo>/extraido/`.
  Nunca aponte a ferramenta para a pasta de instalação.
- Use só abrir, visualizar e exportar. Nada de salvar por cima, *patch* ou *replace*.
- Não ponha nada extraído dentro do projeto do jogo do usuário, nem como placeholder: placeholder
  esquecido acaba no build. No projeto entram só a ficha (números e anotações) e assets próprios
  ou licenciados.
- Nada extraído é publicado nem enviado: fórum, Discord, nuvem compartilhada, conversor online ou
  gerador de imagem online.
- Pacote cifrado: siga "Escopo e limites" do SKILL.md.

## 2. Extrair por engine

Para descobrir a engine, use "Passo 1 — Triagem" do SKILL.md.

| Engine | Ferramenta | Versão | Melhor para | Saída |
|---|---|---|---|---|
| Unity | AssetRipper | 2.0.0 (verificado em 2026-10-11), Unity 3.5 a 6000.4 | tudo de uma vez | modelos `.glb`, imagens, áudio; ou projeto Unity |
| Unity | AssetStudioMod | v0.19.0 (verificado em 2026-10-11), Unity 1.7 a 6000.2 | personagem já com animação | FBX com animação, OBJ, PNG, WAV/OGG |
| Unity | UnityPy | 1.25.4 (verificado em 2026-10-11) | extração em lote por script | PNG, OBJ, WAV |
| Unreal | FModel | aug-2026 (verificado em 2026-10-11) | modelos, texturas, animações | `.psk`/`.pskx`, `.glb`, `.uemodel`, `.usda`; PNG/TGA/WebP |
| Godot | GDRE Tools | 2.7.4 (verificado em 2026-10-11) | projeto inteiro | projeto Godot com recursos nos formatos de importação originais |

### Unity com AssetRipper (padrão)

1. Baixe em github.com/AssetRipper/AssetRipper › Releases e rode. A interface abre no navegador,
   mas quem trabalha é o programa no seu PC, não um site.
2. `File › Open Folder` e escolha a cópia do jogo.
3. Nas configurações (Settings), ponha `Mesh Export Format` em `GLB`, que abre direto no Blender,
   e confira `Image Export Format`.
4. `Export › Export All Files` › `Export Primary Content`, com destino `estudo/<jogo>/extraido/`.
   Você deve ver arquivos `.glb`, imagens e áudio.
5. `Export Unity Project` gera um projeto para abrir num editor Unity separado, com malhas em
   YAML. Nunca o abra dentro do projeto do seu jogo.

Parte da decompilação de shaders é recurso Premium pago; para estudar modelos não faz falta.

### Unity com AssetStudioMod

Use quando quiser o personagem com a animação já presa ao esqueleto (Animator vira FBX com o
AnimationClip). Ele só vai até a Unity 6000.2 (Unity 6.2): em jogo feito em Unity 6.3 ou mais nova,
use o AssetRipper. A interface é só para Windows; há versão de linha de comando para Windows, Linux e
Mac. Carregue a pasta da cópia, filtre por tipo (`Texture2D`, `Mesh`, `Animator`, `AudioClip`) e
exporte os selecionados para `estudo/<jogo>/extraido/`.

### Unity com UnityPy (script)

Bom para extrair em lote e repetir depois. Fixe a versão: o README avisa que "breaking changes can
happen" em versões menores. Use só as funções de leitura do exemplo; não use `save()`, `patch()`
nem `set_raw_data()`, que servem para alterar os dados do jogo.

```python
# pip install UnityPy==1.25.4
# uso: python -I extrair_unity.py estudo/<jogo>/copia estudo/<jogo>/extraido
import os, re, sys
import UnityPy

origem, destino = (os.path.abspath(p) for p in sys.argv[1:3])
if destino == origem or destino.startswith(origem + os.sep):
    sys.exit("A pasta de saída não pode ficar dentro da cópia do jogo.")
os.makedirs(destino, exist_ok=True)

def seguro(nome):
    # o nome vem do jogo: troca barras e caracteres inválidos para não gravar fora de destino
    return re.sub(r"[^\w.-]", "_", str(nome))[:100] or "sem_nome"

for raiz, _, arquivos in os.walk(origem):
    for nome in arquivos:
        try:
            env = UnityPy.load(os.path.join(raiz, nome))
        except Exception:
            continue  # não é arquivo da Unity
        for obj in env.objects:
            tipo = obj.type.name
            if tipo not in ("Texture2D", "Sprite", "Mesh", "AudioClip"):
                continue
            try:
                dado = obj.parse_as_object()
                base = os.path.join(destino, f"{seguro(dado.m_Name)}_{obj.path_id}")
                if tipo in ("Texture2D", "Sprite"):
                    dado.image.save(base + ".png")
                elif tipo == "Mesh":
                    with open(base + ".obj", "wt", newline="") as f:
                        f.write(dado.export())
                else:
                    for amostra, wav in dado.samples.items():
                        with open(f"{base}_{seguro(amostra)}", "wb") as f:
                            f.write(wav)
            except Exception as erro:
                print(f"pulei {tipo} em {nome}: {erro}")
```

O `path_id` no nome evita que dois assets com o mesmo nome se sobrescrevam. O script só lê a cópia
e só grava dentro da pasta de saída.

### Unreal com FModel

1. Baixe em github.com/4sval/FModel › Releases.
2. No seletor de diretório, aponte para `Content/Paks` da cópia e escolha a versão da engine do
   jogo (por exemplo `GAME_UE5_3`). Se os assets não abrirem (pacote cifrado) ou vierem sem nomes
   de propriedades (falta o arquivo de mapeamento `.usmap`), pare e siga a linha do Unreal em
   "Passo 1 — Triagem" do SKILL.md; pacote cifrado segue também "Escopo e limites".
3. Em Settings, mude a pasta de saída para `estudo/<jogo>/extraido/` e escolha o formato de modelo:
   `ActorX (psk / pskx)` para personagem com esqueleto e animação, `glTF 2.0 (binary)` para
   objetos, `UEFormat (uemodel)` se for usar o add-on UEFormat. Textura em PNG.
4. Clique com o botão direito no asset e use as opções de salvar ou exportar, ou junte modelo,
   textura, animação e dados brutos num lote em `Views › Export Session`. Áudio e propriedades
   (`.json`) saem fora da sessão.

### Godot com GDRE Tools

1. Baixe em github.com/GDRETools/gdsdecomp › Releases.
2. Recupere o projeto a partir da cópia (o `.pck`, ou o `.exe` quando os dados estão embutidos):

   ```
   gdre_tools --headless --recover="estudo/<jogo>/copia/<jogo>.pck" --output="estudo/<jogo>/extraido/"
   ```

3. O GDRE converte os recursos importados de volta aos formatos de importação originais. Modelos
   de jogos em Godot 2.x ainda não são convertidos.
4. Abra os modelos no Blender, ou o projeto recuperado num editor Godot separado.

## 3. Abrir no Blender

Blender 5.2.2 LTS (verificado em 2026-10-11). Salve o `.blend` em `estudo/<jogo>/`, nunca na pasta
do projeto do seu jogo.

| Arquivo | Como importar |
|---|---|
| `.glb` / `.gltf` | `File › Import › glTF 2.0` (nativo) |
| `.fbx` | `File › Import › FBX` (nativo) |
| `.obj` | `File › Import › Wavefront (.obj)` (nativo) |
| `.usda` | `File › Import › Universal Scene Description` (nativo) |
| `.psk` / `.psa` | add-on io_scene_psk_psa 9.1.3, Blender 5.0 ou mais novo (verificado em 2026-10-11): importe o `.psk` e depois, com o esqueleto selecionado, o `.psa` |
| `.uemodel` | add-on do UEFormat, Blender 4.2 ou mais novo (verificado em 2026-10-11); as texturas podem precisar ser ligadas à mão |

- Escala errada é comum: o Unreal trabalha em centímetros e a Unity em metros. Compare com um cubo
  de 1 m antes de medir.
- Ossos tortos depois de importar glTF são comuns e não mudam as contagens.

## 4. Ficha de referência visual

Preencha uma ficha por asset em `estudo/<jogo>/fichas/<asset>.md`. Marque cada valor com status:
`confirmado` (lido no arquivo extraído), `medido-jogando` (medido em gravação do jogo),
`inferido` (estimado por screenshot, texto ou nome) ou `localizado-não-expandido` (achou o arquivo,
ainda não abriu). Apague as seções que não se aplicam.

```markdown
# Ficha visual: <asset> (jogo: <jogo>, versão: <versão>)
Fonte: <arquivo extraído> · ferramenta e versão: <...> · data: <AAAA-MM-DD>

## Modelo
- Triângulos (LOD0 / LOD1 / LOD2):            status:
- Altura em metros e proporções (cabeças de altura, ombro ÷ altura):
- Topologia (quads ou triângulos, loops nas articulações, onde há mais detalhe):
- Partes separadas (cabeça, corpo, acessórios):

## UV e texturas
- Layout de UV (nº de ilhas, espelhamento, sobreposição, margem entre ilhas):
- Mapas e resolução (cor, normal, máscaras, canais empacotados):
- Texel density (px/m):

## Rig e animação
- Nº de ossos (corpo / rosto / extras):
- Por animação: nome · quadros · fps · duração (s) · loop? · poses-chave:

## Material
- Nº de materiais / submalhas:
- Shader e recursos (transparência, emissivo, cor por vértice):

## Sprite (2D)
- Tamanho do quadro (px) · pixels por unidade · pivô:
- Quadros por animação · duração de cada quadro (ms):
- Paleta (nº de cores) · atlas e espaçamento:

## Áudio
- Formato no jogo e exportado · taxa de amostragem · canais · duração:
- Loudness integrada (LUFS) · pico real (dBTP) · ponto de loop:

## Para o meu asset
- Orçamento-alvo (triângulos, resolução, ossos, quadros):
- O que muda e por quê:
```

## 5. Como medir cada campo

- **Triângulos:** no Blender, `Viewport Overlays › Statistics`. Compare triângulos, não vértices:
  o jogo duplica vértices nas costuras de UV e nas arestas duras, então a contagem de vértices
  muda de ferramenta para ferramenta.
- **LOD** (*level of detail*, versões mais simples do mesmo modelo usadas longe da câmera):
  procure malhas com sufixo `_LOD1`, `_LOD2`.
- **Proporções:** dimensões no painel lateral (tecla N) ou a régua (Measure). Descreva em
  "cabeças de altura" e em razões, não em centímetros soltos.
- **Topologia** (como as faces se organizam na malha): modo Edit com wireframe. Veja os loops em
  cotovelo, joelho e boca, que deformam na animação, e onde a malha é mais densa.
- **UV** (o mapa que diz que parte da textura cobre cada face): aba UV Editing. Anote ilhas,
  espelhamento (metade da textura usada nos dois lados) e áreas sobrepostas.
- **Texel density** (quantos pixels de textura cobrem 1 metro da superfície), para textura
  quadrada: `px/m = resolução × √(fração da UV usada ÷ área da superfície em m²)`. Exemplo:
  textura de 2048, malha de 4 m², 80% da UV usada: 2048 × √(0,8 ÷ 4) ≈ 916 px/m.
- **Ossos** (o esqueleto, ou *rig*, que move a malha): selecione o esqueleto, entre em Pose Mode;
  Statistics mostra o total.
- **Animação:** Dope Sheet › Action Editor dá o quadro inicial e o final; o fps está em Output
  Properties. A exportação pode reamostrar para outro fps, então confira a duração em segundos,
  que não muda.
- **Sprite:** abra o PNG num editor de imagem e conte os quadros. Sem arquivo de animação, meça a
  duração dos quadros numa gravação do jogo (`medido-jogando`).
- **Material:** aba Material para o número de slots; aba Shading para os mapas ligados. Canal
  empacotado é quando cada canal de cor (R, G, B) guarda um mapa diferente, como oclusão,
  rugosidade e metálico.
- **Áudio:** `ffprobe som.wav` mostra formato, taxa e canais. Loudness (volume percebido, em LUFS):

  ```
  ffmpeg -hide_banner -i som.wav -af ebur128=peak=true -f null -
  ```

  No fim da saída, `I:` é a loudness integrada e `Peak:` o pico real.

## 6. Usar a referência do jeito certo

Faça:

- Deixe a referência em outra janela ou monitor, não como imagem de fundo para contornar.
- Comece de um blockout próprio (rascunho com formas simples, como cubos e cilindros) a partir do
  seu desenho ou concept.
- Mire o mesmo orçamento técnico: faixa de triângulos, resolução, número de ossos, número de
  quadros e ritmo da animação. São parâmetros técnicos, não o desenho.
- Copie proporções de categoria (por exemplo, "personagem estilizado de 4 cabeças"), não o desenho
  de um personagem específico.
- Anime do zero usando o timing anotado. Grave ou sintetize o som, ou use biblioteca licenciada,
  mirando a mesma loudness.

Não faça:

- Retopologia (refazer a malha por cima de outra) sobre o modelo extraído, com snap ou
  shrinkwrap, nem contornar renders dele: isso copia a forma.
- Editar, repintar, recolorir ou filtrar a textura extraída, nem projetá-la ou fazer bake
  (transferir detalhe de uma malha para uma textura) dela para a sua malha.
- Reaproveitar o rig extraído ou fazer retargeting (transferir uma animação para outro esqueleto)
  das animações extraídas.
- Mudar tom, velocidade ou equalização de um som extraído.
- Passar asset extraído por IA (img2img, retexturização, "estilizar"): continua sendo
  transformação da obra.
- Redesenhar à mão, igual, um personagem ou objeto marcante do jogo: copiar o desenho à mão também
  é copiar.

## 7. Por que alterar o asset extraído não o torna seu

Modificar uma obra cria uma obra derivada, e fazer obra derivada depende do dono do original,
por mais que se mude.

- **Brasil:** a Lei 9.610/98, art. 5º, VIII, "g", define obra derivada como a que, "constituindo
  criação intelectual nova, resulta da transformação de obra originária". O art. 29 exige
  "autorização prévia e expressa do autor" para "a adaptação, o arranjo musical e quaisquer outras
  transformações" (inciso III).
  [planalto.gov.br](https://www.planalto.gov.br/ccivil_03/leis/l9610.htm)
- **EUA:** 17 U.S.C. §101 inclui em *derivative work* "editorial revisions, annotations,
  elaborations, or other modifications", e o §106(2) reserva ao titular o direito "to prepare
  derivative works based upon the copyrighted work".
  [§101](https://www.law.cornell.edu/uscode/text/17/101) · [§106](https://www.law.cornell.edu/uscode/text/17/106)
- **Não existe porcentagem que libere:** o Copyright Office dos EUA diz que não há regra que
  permita usar um "percentage of a work" e que não se pode reivindicar a obra de outro "no matter
  how much you change it" sem consentimento do dono.
  [FAQ](https://www.copyright.gov/help/faq/faq-fairuse.html)
- Num processo, compara-se o que ficou parecido, não o que mudou (Spry Fox v. Lolapps, 2012).

Quando o usuário quiser "usar de base e alterar", responda em uma frase e ofereça a seção 8:
"Alterar um asset extraído continua sendo obra derivada e precisa de autorização do dono, não
importa quanto mude; o atalho legal é partir de uma base licenciada e alterar essa."

## 8. O atalho legítimo: partir de uma base licenciada

A licença é a autorização que o art. 29 e o §106(2) exigem. Com ela, alterar é permitido nos termos
da licença. CC0 (domínio público) quer dizer que o autor abriu mão dos direitos até onde a lei
permite: dá para copiar, alterar e vender sem pedir permissão nem dar crédito.

| Site | O que tem | Licença (verificado em 2026-10-11) | Crédito |
|---|---|---|---|
| Kenney (kenney.nl) | pacotes 2D, 3D, interface, áudio | CC0 | opcional |
| Poly Haven (polyhaven.com) | HDRIs, texturas, modelos | CC0 | opcional |
| ambientCG (ambientcg.com) | materiais PBR, HDRIs, modelos | CC0 1.0 | opcional |
| Quaternius (quaternius.com) | personagens animados, bibliotecas de animação, cenários modulares | Quaternius Asset License v1.0: uso comercial livre, proíbe redistribuir os assets como pacote | opcional |
| OpenGameArt (opengameart.org) | 2D, 3D e áudio da comunidade | mista: CC0, CC-BY, CC-BY-SA, OGA-BY, GPL; filtre pela licença | obrigatório, exceto CC0 |
| Sketchfab (sketchfab.com) | modelos 3D | ative "Downloadable"; CC0, CC BY, CC BY-SA, CC BY-ND, CC BY-NC ou Standard, conforme o modelo | obrigatório, exceto CC0 |
| Lojas das engines (Unity Asset Store, Fab da Epic, Godot Asset Library) | pagos e gratuitos | licença da loja ou do item | conforme a licença |

O que cada sigla Creative Commons exige:

- **BY:** dê crédito (autor, título, licença, link). Pode alterar e vender.
- **SA:** a versão alterada sai com a mesma licença.
- **ND:** proíbe alterar; não serve para "usar de base".
- **NC:** proíbe uso comercial; não serve para jogo vendido ou monetizado.
- **GPL** em arte obriga a distribuir sob GPL; evite em jogo fechado.
- Se um item lista várias licenças, basta cumprir uma.

Ao usar uma base:

1. Leia a licença na página do item, não só na página inicial do site, e guarde um print com a data.
2. Registre em `CREDITOS.md`, no projeto do jogo: asset, autor, link, licença, data e o que mudou.
3. Item de loja: em geral a licença permite usar e alterar dentro do jogo e proíbe revender o
   asset solto; confira os termos do item.
4. Use a ficha de referência visual para levar a base ao orçamento e às proporções que você
   estudou.
