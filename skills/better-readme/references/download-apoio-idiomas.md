# Download, portátil, apoio e idiomas

Módulos opcionais do README. Cada um tem uma regra de ouro: **só entra o que o usuário realmente tem** (arquivo publicado, canal de apoio, tradução mantida). Nada inventado.

## Baixar (releases e versão portátil)

### O que verificar antes de escrever

- **Existe release?** `gh release list` / `gh release view` ou `git tag`. Sem release, a seção "Baixar" vira "Compilar do código" e o checklist avisa que falta publicar.
- **Nomes reais dos assets**: do release publicado, do workflow (`.github/workflows/*.yml`) ou do empacotador (Inno Setup, electron-builder, tauri.conf). Nunca invente o nome do arquivo.
- **Portátil de verdade?** `scripts/descobrir_fatos.py` mostra `sinais_de_portatil`: se o código escreve em `%APPDATA%`, `%LOCALAPPDATA%`, `Documents` ou no registro do Windows, o app **não é** portátil no sentido de "não deixa rastros". Só escreva "dados na pasta `data` ao lado do programa" se isso estiver no código ou o usuário garantir. Ausência de sinais não prova nada: pergunte.

### Link estável

```
https://github.com/OWNER/REPO/releases/latest/download/NOME-DO-ASSET
```

O link `latest/download` usa o **nome literal** do arquivo. Para o link não quebrar a cada versão, publique também uma cópia **sem versão no nome** (`NomeDoApp-windows-x64-portable.zip`, além de `NomeDoApp-1.4.0-windows-x64-portable.zip`). Confira no repositório que `latest` aponta para release estável (pré-lançamentos e rascunhos não contam como "latest").

Convenção de nome: `<Projeto>-<so>-<arquitetura>-<tipo>.<ext>` (ex.: `TaskPane-windows-x64-setup.exe`, `TaskPane-windows-x64-portable.zip`, `taskpane-linux-x64.tar.gz`). O GoReleaser usa projeto, versão, SO e arquitetura, com `tar.gz` e `zip` no Windows.

### Bloco modelo

````markdown
## Baixar

| Quero | Arquivo | Observação |
|---|---|---|
| Instalar | [NomeDoApp-windows-x64-setup.exe](https://github.com/OWNER/REPO/releases/latest/download/NomeDoApp-windows-x64-setup.exe) | Cria atalho e desinstalador |
| Usar sem instalar (portátil) | [NomeDoApp-windows-x64-portable.zip](https://github.com/OWNER/REPO/releases/latest/download/NomeDoApp-windows-x64-portable.zip) | Descompacte e execute. Não atualiza sozinho. |

Requer Windows 10 ou superior e <runtime> instalado. SHA-256 em `SHA256SUMS.txt`. Versões anteriores em [Releases](../../releases).

<details>
<summary>O Windows mostrou "O Windows protegeu seu computador"</summary>

O programa ainda não tem assinatura digital nem reputação no Windows SmartScreen, então o aviso aparece para qualquer arquivo novo. Clique em **Mais informações** e depois em **Executar assim mesmo**. Para conferir o arquivo, compare o hash:

```powershell
Get-FileHash .\NomeDoApp-windows-x64-setup.exe -Algorithm SHA256
```

</details>
````

### Regras

- Só uma tabela de download e uma linha de requisitos (runtime, versão do Windows, versão do jogo).
- **Gerenciadores de pacote** (winget, scoop, choco, brew) só se o pacote existir, cada um com o comando exato.
- **Aviso de assinatura**: se o executável não é assinado, diga com honestidade (o bloco acima). Não escreva "100% seguro". Assinatura de código para pessoa física tem requisitos e custos; confirme as opções na fonte antes de recomendar.
- **Checksum**: publique `SHA256SUMS.txt` no release. Atestado de build (`actions/attest`, `gh attestation verify`) é opcional e mais avançado.
- **Portátil** significa: zip que roda de qualquer pasta, sem instalar, com os dados ao lado do executável (padrão do modo portátil do VS Code: pasta `data` junto do programa). Explique **onde ficam os dados** e **que não atualiza sozinho**.
- Padrão de portátil em release veio de poucos projetos (PR aberto e issue de backlog) mais o VS Code, Flow Launcher, ShareX e yt-dlp como corroboração; apresente como boa prática, exigindo confirmar no código.
- Notas de release automáticas: `.github/release.yml` (categorias por label). Changelog: Keep a Changelog, com datas ISO e seção Unreleased.

## Apoio (donate / sponsor)

### FUNDING.yml (botão Sponsor do repositório)

Arquivo em **`.github/FUNDING.yml`** na branch padrão (fora de `.github/` o GitHub ignora). Só chaves documentadas:

```yaml
# .github/FUNDING.yml
github: [seu-usuario]               # até 4 usuários/organizações no GitHub Sponsors
ko_fi: seu_usuario
buy_me_a_coffee: seu_usuario
patreon: seu_usuario
liberapay: seu_usuario
open_collective: seu-projeto
polar: seu_usuario
thanks_dev: u/gh/seu-usuario
custom: ["https://seu-site.com/apoie", "https://pix.exemplo/aqui"]   # até 4 URLs; entre aspas
```

Chaves aceitas hoje: `github`, `community_bridge`, `issuehunt`, `ko_fi`, `liberapay`, `open_collective`, `patreon`, `tidelift` (formato `plataforma/pacote`), `polar`, `buy_me_a_coffee`, `thanks_dev` e `custom`. Um usuário ou pacote por plataforma externa. Não deixe chaves vazias (`patreon: ''`) como enfeite; use só as que o usuário tem. Uso proibido: publicidade e apoio a grupos políticos, comunitários ou de caridade (regra do GitHub).

### Disponibilidade (para o público brasileiro)

- **GitHub Sponsors** lista o Brasil entre as regiões que podem receber; exige 2FA, conta Stripe Connect e formulário fiscal (W-8BEN para quem não é residente nos EUA). A aprovação leva tempo: não prometa "em breve".
- **Ko-fi e Buy Me a Coffee**: não há fonte confirmando recebimento no Brasil. Peça ao usuário que confirme na própria conta antes de listar.
- **Pix** não é chave do FUNDING.yml: entra por `custom:` apontando para uma URL (página, seção do README ou link do banco). Se o GitHub aceita âncora em `custom` não foi verificado: teste.

### Seção no README (curta, perto do fim)

```markdown
## Apoie o projeto

O NomeDoApp é gratuito e mantido no meu tempo livre. Se ele te poupa trabalho, você pode ajudar:

- [GitHub Sponsors](https://github.com/sponsors/USUARIO)
- [Ko-fi](https://ko-fi.com/USUARIO)
- Pix (chave aleatória): `<chave que o usuário informou>`
```

- Posição: **depois** da definição, do download e de contribuir, perto do fim. Nada antes disso. Topo só em projeto com monetização direta (e mesmo assim é o ponto fraco mais citado nos READMEs lidos).
- Tom: curto, sem cobrança nem culpa. Não há estudo sobre a reação do leitor a seções de doação: é boa prática, não regra.
- **Pix**: a chave é dado pessoal e é do usuário; **nunca invente nem complete**. Peça a chave (de preferência aleatória, para não expor CPF/telefone) e o "copia e cola" gerado no app do banco. O QR code é imagem que o usuário fornece. O README mostra a chave em texto e, se houver, o QR com alt ("QR Code Pix para apoiar o NomeDoApp").
- Badges de apoio, se o usuário quiser (estáticos, shields): `https://img.shields.io/badge/Ko--fi-apoie-FF5E5B?logo=kofi&logoColor=white`, `.../badge/Buy%20Me%20a%20Coffee-apoie-FFDD00?logo=buymeacoffee&logoColor=black`, `.../badge/GitHub%20Sponsors-apoie-EA4AAA?logo=githubsponsors&logoColor=white`. Confira que o ícone renderiza. Contam para o limite de badges; prefira link de texto se já houver 5.

## Idiomas

- O GitHub **não escolhe** o README pelo idioma do visitante. Todos os idiomas são arquivos e o seletor é um link.
- Padrão: `README.md` + `README.<tag>.md` na raiz, com tag BCP 47 (`README.pt-BR.md`, `README.es.md`, `README.zh-CN.md`). `README.md` fica em **inglês** quando há mais de um idioma (spec standard-readme). Projeto só para brasileiros: `README.md` em português basta.
- **Seletor no topo de todos os arquivos**, idêntico, abaixo do título:

```markdown
**English** | [Português](README.pt-BR.md) | [Español](README.es.md)
```

- Traduza texto, títulos de seção e alt de imagem. **Não** traduza comandos, código, nomes de arquivo, nomes de flags nem URLs.
- **Traduza o sentido, não palavra por palavra.** Reescreva no ritmo de texto técnico do idioma de destino e reestruture frases à vontade; mapear frase a frase produz "traduzês". Mantenha em inglês os termos que a comunidade realmente usa em inglês (commit, pull request, token, build, endpoint, prompt) e traduza o que tem termo nativo.
- **Espelhe a estrutura**: mesmas seções, mesmas tabelas, mesmos links e **o mesmo número de títulos**, na mesma ordem. A paridade é verificável: `auditar_readme.py` compara níveis de título, blocos de código, tabelas e imagens entre `README.md` e `README.<tag>.md` (`paridade-traducao`).
- **Combine o tom** do produto: se os exemplos do produto são coloquiais, o README pode ser.
- **Âncoras mudam quando o título muda**: atualize os links `](#...)` do arquivo traduzido para os títulos traduzidos.
- Marca de sincronização em cada tradução: `<!-- Traduzido de README.md @ <commit curto> em <data> -->`. Tradução desatualizada deve avisar: "Esta versão pode estar atrás do README em inglês."
- Só ofereça tradução se houver público real **e** quem mantenha. 32 de 36 READMEs de projetos grandes não têm tradução; o mais comum é localizar a interface do app (Crowdin/Weblate), que é outra coisa.
- Pastas por idioma (`docs/pt-BR/`) valem para documentação extensa; o README só aponta.
- Não existe fonte que prove que README traduzido aumenta alcance ou busca: não prometa.

## Arquivos de comunidade e metadados do repositório

| Item | O que fazer |
|---|---|
| `LICENSE` | Obrigatório (P0 se faltar). Escolha em choosealicense.com; cite SPDX no README. Decisão do dono: não escolha por ele sem perguntar. |
| `CONTRIBUTING.md` | Só se aceita contribuição; linke do README. Cubra "como escolher uma tarefa" e "como conversar com a comunidade" (as barreiras mais esquecidas). |
| `CODE_OF_CONDUCT.md`, `SECURITY.md` | Opcionais; linke se existirem. SECURITY diz onde reportar vulnerabilidade. |
| `CHANGELOG.md` | Keep a Changelog; datas ISO. |
| `CITATION.cff` | Só projeto acadêmico. |
| `AGENTS.md` | No máximo uma linha no README, se o projeto aceita agentes de IA. Não há evidência de consumo de `llms.txt` por provedores: não coloque em README comum. |
| About (descrição) | Igual à frase de definição. |
| Topics | Até 20, minúsculas; ajudam a busca. |
| Social preview | 1280×640, < 1 MB. |

Alterar About, topics e social preview é ação do dono no repositório: **entregue o texto pronto, não aplique** sem pedido.
