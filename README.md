# skills

Skills for Claude Code and claude.ai: study game files, find and vet community skills, write GitHub READMEs.

[![Last commit](https://img.shields.io/github/last-commit/FFloriani/skills)](https://github.com/FFloriani/skills/commits/main)

A skill is a folder with a `SKILL.md`. Claude loads it when your request matches its description, or when you type `/<skill-name>`.

## Which skill do you need?

| You want to | Skill | Call it |
|---|---|---|
| Learn how a game installed on your PC was made, to build your own | [datamine](skills/datamine/) | `/datamine` |
| Get exact answers about a game you play: items, bosses, builds, maps, crafting routes | [theorycraft](skills/theorycraft/) | `/theorycraft` |
| Find ready-made skills and install them only after a security check | [skillsmp-search](skills/skillsmp-search/) | `/skillsmp-search` |
| Write, improve or audit a GitHub README, and get About text, topics and a launch plan | [better-readme](skills/better-readme/) | `/better-readme` |

## What each one does

### datamine

Identifies the engine of a game installed on your PC, copies the files to a study folder, extracts assets and data tables, decompiles and deobfuscates, and decrypts a **copy** for reading only. The output is notes on mechanics and formulas (XP curves, drop rates, scaling) you can port to your own game.

- Read-only and local: nothing is written back to the game, and nothing extracted is published.
- Single-player or offline games only.
- Mechanics and formulas can be ported; assets, names, text and exact numbers are recreated, not copied.

### theorycraft

For players. Scans the installed files of a game and builds a knowledge base (SQLite database, CSVs and documents): what each item, spell and skill does and where to get it, quests, maps, boss movesets with frame data, best builds, combos, crafting routes, MMO daily routines and patch diffs.

- Read-only: no injection, memory reading or network interception.
- Online games: rules that run on the server are not in the files, so the skill marks them as measured in play or from a cited community source, never guessed.

### skillsmp-search

Searches two directories of community skills with one command: [skills.sh](https://skills.sh) (the one behind Vercel's `npx skills`; lists how many times each skill was installed, no key needed) and [SkillsMP](https://skillsmp.com) (filters by category, occupation and language). If one is down or has no key, the other still answers. Installing is a separate step behind a safety gate: quarantine, a static scanner for prompt injection, hidden characters, auto-run hooks, credential access and malicious scripts, a manual read, and a verdict you approve before anything reaches `~/.claude/skills/`.

### better-readme

Creates, improves, audits and translates GitHub READMEs. It reads the repository first to find the real facts, picks the skeleton for the project type (library, CLI, desktop app, game or mod, API, awesome list), and checks links, images and HTML afterwards. It also audits discoverability metadata (About, topics, search terms) and drafts a launch plan. It never promises stars or ranking, and never suggests buying them.

## Install

**Claude Code**: copy the skill folders you want into `~/.claude/skills/`.

```bash
git clone https://github.com/FFloriani/skills.git
cd skills
cp -r skills/datamine ~/.claude/skills/      # or theorycraft, skillsmp-search, better-readme
```

On Windows PowerShell:

```powershell
git clone https://github.com/FFloriani/skills.git
cd skills
Copy-Item -Recurse skills\datamine $HOME\.claude\skills\
```

Then type `/datamine`, or ask normally and Claude picks it up.

**claude.ai**: zip the skill folder and upload it in the Skills section of your settings.

## Requirements

| Skill | Needs |
|---|---|
| datamine | Python 3 for the optional scripts (standard library only). Engine tools such as AssetRipper, ILSpy, FModel or Il2CppDumper are installed separately; the skill says which one fits each engine. |
| theorycraft | Python 3 for the scripts. `openpyxl` is optional (`pip install openpyxl`) for `.xlsx` export; without it you get one CSV per table. |
| skillsmp-search | Python 3. skills.sh needs nothing else. For SkillsMP also add an API key (create one at skillsmp.com): set `SKILLSMP_API_KEY`, or put the key on a single line in `~/.config/skillsmp/key`. Without the key you still get skills.sh. |
| better-readme | Python 3 for the three scripts (standard library only). One of them reads the public GitHub API; `GITHUB_TOKEN` is optional (private repositories, rate limit). |

The instructions in datamine, theorycraft and better-readme are written in Portuguese; skillsmp-search is in English.

## Structure

```
skills/
  <skill-name>/
    SKILL.md        instructions Claude reads
    references/     supporting material, loaded only when needed
    scripts/        programs Claude can run
```

## Feedback

Built and maintained by [FFloriani](https://github.com/FFloriani). Found a bug or have a request? [Open an issue](https://github.com/FFloriani/skills/issues).

## License

[MIT](LICENSE) © 2026 FFloriani
