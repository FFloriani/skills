# skills

Skills que eu criei para o Claude (Claude Code e claude.ai). Cada skill fica na sua própria pasta dentro de `skills/`.

| Skill | O que faz | Como chamar |
|---|---|---|
| [datamine](skills/datamine/) | Estuda jogos instalados no PC para aprender como foram feitos: identifica a engine, extrai assets e tabelas, decompila, desofusca e decifra uma cópia só para leitura, e documenta mecânicas e fórmulas para você criar o seu jogo. Conteúdo em português. | `/datamine` |
| [skillsmp-search](skills/skillsmp-search/) | Busca skills prontas no marketplace [SkillsMP](https://skillsmp.com) por palavra-chave, categoria, profissão ou idioma. | `/skillsmp-search` |

## Como instalar

**Claude Code**: copie a pasta da skill para `~/.claude/skills/`.

```bash
git clone https://github.com/FFloriani/skills.git
cp -r skills/skills/datamine ~/.claude/skills/
```

Depois é só digitar `/datamine` (ou pedir normalmente, que o Claude aciona sozinho).

**claude.ai**: compacte a pasta da skill em `.zip` e envie na área de Skills das configurações.

## Configuração extra

- **skillsmp-search** precisa de uma chave da API do SkillsMP (crie em skillsmp.com). Coloque em uma variável de ambiente `SKILLSMP_API_KEY` ou num arquivo `~/.config/skillsmp/key` com a chave numa linha só.
- **datamine** usa Python 3 só para os scripts opcionais em `scripts/`.

## Estrutura

```
skills/
  <nome-da-skill>/
    SKILL.md        instruções que o Claude lê
    references/     material de apoio, lido só quando precisa
    scripts/        programas que o Claude pode rodar
```
