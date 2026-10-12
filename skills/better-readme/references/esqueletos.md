# Esqueletos de README por tipo de projeto

Escolha o esqueleto pelo que o repositório é, não pelo que o usuário acha que ele é. `scripts/descobrir_fatos.py` devolve `tipo_provavel` com as evidências; confirme com o usuário quando a confiança for baixa ou houver dois candidatos fortes.

Convenções: `<...>` é conteúdo a preencher a partir do registro de fatos. Seção marcada como opcional só entra se o fato existir. O idioma dos títulos segue a decisão de idioma do usuário (aqui, em português).

Os esqueletos são síntese das fontes estudadas (standard-readme, makeareadme, Write the Docs, Google, GitHub Docs) e de 36 READMEs reais lidos. Nenhuma fonte prova que uma ordem aumenta adoção: apresente como boa prática.

## Como decidir o tipo

| Sinais no repositório | Tipo | Observação |
|---|---|---|
| `bin` no package.json, `[project.scripts]`, `src/main.rs`, `cmd/`, projeto .NET `Exe` | CLI | Se também exporta módulo, trate como CLI + biblioteca: CLI primeiro |
| `main`/`exports`, `src/lib.rs`, `pyproject` sem scripts, projeto .NET biblioteca | Biblioteca | |
| `WinExe`/WPF/WinForms, Electron, Tauri, PySide/PyQt/Tk, script Inno Setup/WiX | App desktop | Usuário final: o download vem antes de tudo |
| `project.godot`, `ProjectSettings/`, `.uproject`, `default.project.json` (Roblox), `fxmanifest.lua`, `fabric.mod.json`, BepInEx/MelonLoader | Jogo ou mod | Acrescente compatibilidade e aviso legal |
| `openapi.*`, framework de servidor, Dockerfile, `docker-compose` | API ou serviço | Pergunte se é para consumir ou para hospedar |
| `manifest.json` com `manifest_version` | Extensão de navegador | Trate como app: prova visual e link da loja |
| Nome `awesome-*` ou README feito de itens de link | Lista awesome | Regras próprias, ver abaixo |
| Só Markdown, sem manifesto | Documentação, tutorial ou lista | |
| Repositório com o nome do usuário, ou `.github/profile/README.md` | Perfil ou organização | Vitrine curta |

## Contrato da primeira tela (todos os tipos)

1. Logo ou banner, opcional, no máximo um, com alt.
2. **H1 com o nome** do projeto (um só).
3. **Frase de definição** de até 120 caracteres: o que é, para quem, o diferencial. Igual ao About do repositório e à `description` do manifesto.
4. Linha de navegação, opcional: `Baixar · Documentação · Reportar problema`.
5. 3 a 5 badges, em uma linha, só de coisas que existem.
6. **Prova visual** quando houver interface (screenshot ou GIF curto); em CLI, uma demo curta.
7. **Caminho para obter**: comando de instalação ou link de Releases.

Apoio, anúncios, merch, patrocinadores, história do projeto e créditos nunca vêm antes de 3 e 7.

## Regras de ordem depois da primeira tela

- "Por que existe" (3 a 5 linhas) vem logo depois, antes de detalhes técnicos.
- **Instalação trivial** (um comando) se junta ao uso num único "Início rápido". **Instalação cara** (build, runtime, drivers) mostra a demo ou o resultado antes. **App de usuário final** põe o download antes de qualquer explicação.
- Funcionalidades, depois uso e configuração, depois compatibilidade e problemas conhecidos.
- Contribuir, apoiar e créditos perto do fim; **Licença por último** (com badge ou linha no topo).
- Referência longa (API completa, todas as flags, FAQ extensa) vai para `docs/` e o README linka.
- Arquivo com mais de 100 linhas ganha sumário (o GitHub também gera um Outline automático).

---

## Biblioteca

````markdown
# NomeDaBiblioteca

<frase de definição, até 120 caracteres>

[badge release] [badge build] [badge licença]        <!-- 3 a 5, uma linha -->

## Por que existe
<dor do público em 1-2 linhas> · <o que as alternativas não resolvem> · <o que muda aqui> · <o que NÃO faz>

## Instalação
<um comando por gerenciador; versão mínima do runtime>

## Início rápido
<até ~15 linhas executáveis + a saída esperada>

## Uso
<do caso simples ao complexo; 2 a 3 exemplos; link para docs/>

## API
<link para a referência gerada; só o essencial aqui>

## Compatibilidade
<versões de runtime e de linguagem testadas>

## Contribuindo
<onde perguntar, se aceita PR, link para CONTRIBUTING.md>

## Licença
<SPDX> © <nome>
````

## CLI

````markdown
# nome-do-cli

<frase de definição, até 120 caracteres>

[badge release] [badge build] [badge licença]

![Demo: <comando> mostrando <resultado>](docs/img/demo.gif)   <!-- GIF curto (VHS) + o comando e a saída em texto logo abaixo -->

## Instalação
<binário pré-compilado por SO primeiro (releases/latest/download); depois só os gerenciadores que existem: winget, scoop, brew, cargo, npm, pip>

## Início rápido
<2 a 4 comandos com a saída esperada>

## Uso
<trecho do --help; flags mais comuns; subcomandos>

## Configuração
<arquivo, variáveis de ambiente, precedência>

## Comparação com alternativas       <!-- opcional: tabela de 3 a 5 linhas, critérios verificáveis -->
## Solução de problemas              <!-- 3 a 5 erros reais com causa e correção -->
## Contribuindo
## Licença
````

## App desktop (inclui jogo e mod com download e versão portable)

````markdown
<p align="center"><img src="docs/img/logo.png" alt="Logotipo do NomeDoApp" width="120"></p>

# NomeDoApp

<frase de definição, até 120 caracteres, em linguagem do usuário, não do desenvolvedor>

[Baixar](#baixar) · [Documentação](docs/) · [Reportar problema](../../issues)

![Captura de tela da tela principal mostrando <o que aparece>](docs/img/principal.png)

> [!NOTE]
> Requer <runtime, versão do jogo ou mod loader>.      <!-- no máximo 1 ou 2 alertas no documento -->

## Baixar
| Quero | Arquivo | Observação |
|---|---|---|
| Instalar | [NomeDoApp-windows-x64-setup.exe](https://github.com/OWNER/REPO/releases/latest/download/NomeDoApp-windows-x64-setup.exe) | <atalho, desinstalador> |
| Usar sem instalar (portátil) | [NomeDoApp-windows-x64-portable.zip](https://github.com/OWNER/REPO/releases/latest/download/NomeDoApp-windows-x64-portable.zip) | Descompacte e execute; dados na pasta `data` ao lado do programa |

SHA-256 em `SHA256SUMS.txt` · Versões anteriores em [Releases](../../releases)

<details>
<summary>O Windows mostrou "O Windows protegeu seu computador"</summary>

<explicação honesta: o app não é assinado e ainda não tem reputação; Mais informações, depois Executar assim mesmo; como conferir o hash com Get-FileHash>

</details>

## Principais recursos
<capacidade e resultado para o usuário; 1 imagem por recurso principal se o app for visual>

## Primeiros passos
1. <passo> 2. <passo> 3. <resultado esperado>

## Compatibilidade                    <!-- jogo ou mod -->
<versão do jogo testada, mod loader, conflitos conhecidos>

## Instalação do mod                  <!-- só mod -->
<pasta de destino, ordem de carga, como desinstalar>

## Problemas conhecidos e changelog
## Privacidade e atualizações         <!-- telemetria, auto-update; "o portátil não atualiza sozinho" se for o caso -->
## Compilar a partir do código        <!-- opcional -->
## Contribuir · Apoie o projeto · Créditos
## Aviso legal                        <!-- jogo ou mod: sem afiliação; permissões de assets -->
## Licença
````

A tabela de download e o bloco de SmartScreen seguem o padrão de Flow Launcher, ShareX e PowerToys. As seções de jogo e mod (compatibilidade, instalação do mod, aviso legal) são extrapolação do princípio de responder às perguntas do público; nenhuma fonte estudada trata README de jogo ou mod.

Detalhes do módulo Baixar, portátil, apoio e idiomas: `references/download-apoio-idiomas.md`.

## API ou serviço

````markdown
# NomeDaAPI

<frase de definição> · URL base: <https://...> · Status: <link ou nota>

## Início rápido
<requisição curl e resposta de exemplo>

## Autenticação
<como obter e enviar a credencial; nunca colocar chave real>

## Endpoints
<resumo e link para OpenAPI ou referência; não duplicar no README>

## Limites e erros
<rate limit, códigos de erro mais comuns>

## SDKs                               <!-- opcional -->
## Rodar localmente ou self-host      <!-- opcional: Docker, variáveis de ambiente, aviso de backup se mexe em dados -->
## Contribuindo
## Licença
````

## Extensão de navegador

Use o esqueleto de app: nome, definição, **link da loja** no lugar do download (ou ZIP para carregar sem empacotar), screenshot, permissões que a extensão pede e por quê, privacidade (o que lê e envia).

## Lista awesome

````markdown
# Awesome Nome da Lista [badge Awesome]      <!-- título em title case; repositório awesome-nome-da-lista -->

<descrição objetiva do escopo, sem slogan nem texto de marketing>

## Contents
- [Categoria A](#categoria-a)
- [Categoria B](#categoria-b)

## Categoria A
- [Nome do item](https://exemplo.com) - Descrição objetiva que diz o que é e por que entra na lista.

## Contributing
<link para contributing.md>

## Footnotes
````

Regras da lista awesome, aplicadas sem adaptar: `Contents` primeiro, com no máximo um nível de aninhamento; entradas no formato `link - Descrição.` com maiúscula inicial e ponto final; `Contributing` e `Footnotes` fora de Contents; badge Awesome ao lado do título; sem badge de CI; sem seção de licença no README (LICENSE na raiz, CC0 recomendado); novas entradas ao fim da categoria; esperar 30 dias antes de submeter a lista à lista principal; incluir só o que o autor ou outro colaborador recomenda pessoalmente.

## Template ou starter (inferência, sem fonte direta)

````markdown
# nome-do-template

<definição: stack + para qual caso de uso>

[Usar este template](../../generate)        <!-- botão "Use this template" do GitHub, se o repo for template -->

## O que vem pronto
## Como começar        <!-- 1. usar template  2. renomear  3. rodar -->
## Estrutura de pastas <!-- árvore comentada, curta -->
## O que mudar primeiro <!-- checklist -->
## Licença
````

## Tutorial ou curso (inferência)

````markdown
# Título

<o que a pessoa vai construir ou aprender, para quem, tempo estimado>

## Pré-requisitos
## Roteiro            <!-- lista numerada, cada item linka a parte -->
## Como rodar os exemplos
## Créditos e licença
````

## Perfil ou organização (inferência)

README de repositório com o nome do usuário (perfil) ou `.github/profile/README.md` (organização) é vitrine curta: quem é, no que trabalha, 3 a 5 projetos em destaque com uma linha cada, como contatar. Sem Install nem Usage. Evite painel pesado de estatísticas e mural de badges: é a mesma regra de "pouco e informativo".

## Só documentação

A standard-readme dispensa Install e Usage em repositório que só tem documentação. Mantenha definição, índice de conteúdo, como contribuir e licença.
