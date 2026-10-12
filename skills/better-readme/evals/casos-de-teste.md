# Casos de teste da skill better-readme

Use para conferir se a skill se comporta como deve depois de mudar `SKILL.md`, `references/` ou `scripts/`. Cada caso diz o pedido, o estado do repositório e o que **precisa** acontecer. Rode o caso numa cópia do repositório, nunca no original.

## 1. CLI Python sem README

**Pedido:** "faz um README pra esse projeto, vou publicar hoje"
**Estado:** `pyproject.toml` com `[project.scripts]`, `src/`, `tests/`, sem README, sem LICENSE.
**Deve:**
- Rodar `descobrir_fatos.py` antes de perguntar qualquer coisa; tipo = CLI.
- Perguntar no máximo 5 coisas (para quem/dor, idioma, quer apoio?, aceita contribuição?, qual licença) e **não** perguntar nome, comando de instalação nem versão.
- Usar o esqueleto CLI com comandos reais do `pyproject` e do `--help`.
- Avisar que falta LICENSE (P0) sem escolher uma por conta própria.
- Rodar a auditoria e entregar sem P0 de placeholder/link; listar pendências (GIF, chave, etc.).
**Não deve:** inventar comparação com alternativas, badge de CI sem workflow, emoji, número de estrelas.

## 2. App WPF com release portátil

**Pedido:** "preciso de um README bom pro meu app, tem instalador e portable no release"
**Estado:** `.csproj` WinExe, workflow de release com `Inno Setup`, `gh release` com 2 assets.
**Deve:**
- Montar a tabela **Baixar** com os nomes reais dos assets e o link `latest/download`; pedir cópia sem versão se o nome tiver versão.
- Procurar `AppData`/registro no código; se achar, **não** prometer "portátil sem rastros" e dizer por quê.
- Incluir o `<details>` de SmartScreen se o executável não é assinado (perguntar).
- Pôr screenshot (ou marcador PENDENTE) acima da instalação.
**Não deve:** prometer winget/scoop sem pacote existente; pôr apoio antes do download.

## 3. README existente, ruim

**Pedido:** "melhora meu README"
**Estado:** README com badges demais, emoji em título, `TODO`, link quebrado, token de exemplo real.
**Deve:**
- Perguntar "sobrescrever, mesclar ou só auditar?" (ou assumir "mesclar" e dizer) **antes** de escrever.
- Reportar os P0 (segredo, placeholder, link) primeiro; **não repetir o segredo** no relatório.
- Preservar o conteúdo factual do autor (funcionalidades, histórico) ao reescrever.
**Não deve:** apagar seções sem avisar; reaproveitar o token.

## 4. Mod de jogo

**Pedido:** "README pro meu mod de <jogo>"
**Estado:** projeto C# com BepInEx, release em zip.
**Deve:**
- Incluir **Compatibilidade** (versão do jogo e do mod loader a confirmar com o usuário), **Instalação do mod** (pasta de destino) e **Aviso legal** (sem afiliação, permissões de assets).
- Perguntar a versão do jogo testada em vez de supor.
**Não deve:** usar logo/nome do jogo como se fosse oficial; afirmar compatibilidade não testada.

## 5. Apoio com Pix

**Pedido:** "coloca uma parte pra doação, aceito Pix e Buy Me a Coffee"
**Deve:**
- Pedir a **chave Pix** (e o "copia e cola"/QR); **não inventar**; deixar marcador PENDENTE se o usuário não passar.
- Criar `.github/FUNDING.yml` (não na raiz) só com chaves documentadas; `buy_me_a_coffee: <usuário que ele informou>`; Pix por `custom:` ou seção.
- Perguntar se a conta do Buy Me a Coffee recebe no Brasil (não confirmado).
- Pôr a seção **depois** de baixar e contribuir, curta, sem cobrança.

## 6. README em dois idiomas

**Pedido:** "quero em inglês e português"
**Deve:**
- `README.md` (inglês) + `README.pt-BR.md`; seletor idêntico no topo dos dois; comandos e URLs literais; títulos e alt traduzidos; marca de sincronização.
- Rodar a auditoria nos dois arquivos (`seletor-de-idiomas` limpo).

## 7. "Faz meu projeto ganhar estrela"

**Pedido:** "melhora o README pra eu ganhar mais estrelas"
**Deve:**
- Dizer, sem sermão, que nenhum estudo mostra README causando estrelas; focar em clareza para quem chega.
- Entregar README + texto de About e topics (sem aplicar).
**Não deve:** prometer resultado; pôr "⭐ Star this repo" insistente.

## 8. Repositório sem sinais claros

**Estado:** pasta com scripts soltos, sem manifesto, sem git.
**Deve:** `descobrir_fatos.py` devolve tipo `desconhecido` com confiança baixa; a skill **pergunta** o que é o projeto em vez de adivinhar, e propõe a pasta mínima (LICENSE, .gitignore) antes do README.

## 9. Auditoria apenas

**Pedido:** "audita esse README, não mexe"
**Deve:** relatório P0/P1/P2 com veredito em uma linha; **nenhum arquivo alterado**; lista do que não foi possível checar.

## 10. Lista awesome

**Pedido:** "README pra minha lista de recursos de <tema>"
**Deve:** esqueleto awesome (Contents, `link - Descrição.`, sem seção de licença, sem badge de CI), `--tipo awesome` na auditoria; sem frase de marketing.
