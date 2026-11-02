# skills

Skills for Claude Code and claude.ai: study game files, find and vet community skills, write GitHub READMEs, check a project for security flaws.

[![Last commit](https://img.shields.io/github/last-commit/FFloriani/skills)](https://github.com/FFloriani/skills/commits/main)

A skill is a folder with a `SKILL.md`. Claude loads it when your request matches its description, or when you type `/<skill-name>`.

## Which skill do you need?

| You want to | Skill | Call it |
|---|---|---|
| Learn how a game installed on your PC was made, to build your own | [datamine](skills/datamine/) | `/datamine` |
| Get exact answers about a game you play: items, bosses, builds, maps, crafting routes | [theorycraft](skills/theorycraft/) | `/theorycraft` |
| Find ready-made skills and install them only after a security check | [skillsmp-search](skills/skillsmp-search/) | `/skillsmp-search` |
| Write, improve or audit a GitHub README, and get About text, topics and a launch plan | [better-readme](skills/better-readme/) | `/better-readme` |
| Check a project, site, app or game for security flaws, or check what changed before a commit | [vistoria](skills/vistoria/) | `/vistoria` |

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

Searches two directories of community skills with one command: [skills.sh](https://skills.sh) (the one behind Vercel's `npx skills`; lists how many times each skill was installed, no key needed) and [SkillsMP](https://skillsmp.com) (filters by category, occupation and language). If one is down or has no key, the other still answers. Installing is a separate step behind a safety gate: quarantine, a static scanner for prompt injection, hidden characters, auto-run hooks, credential access and malicious scripts, a manual read, and nothing reaches `~/.claude/skills/` until you asked for it. A clean result installs right away; anything suspicious stops and waits for your yes.

### better-readme

Creates, improves, audits and translates GitHub READMEs. It reads the repository first to find the real facts, picks the skeleton for the project type (library, CLI, desktop app, game or mod, API, awesome list), and checks links, images and HTML afterwards. It also audits discoverability metadata (About, topics, search terms) and drafts a launch plan. It never promises stars or ranking, and never suggests buying them.

### vistoria

One command for a security review of your own code. It runs [Gitleaks](https://github.com/gitleaks/gitleaks) (leaked passwords and keys), [OSV-Scanner](https://github.com/google/osv-scanner) (dependencies with known flaws) and [Semgrep](https://github.com/semgrep/semgrep) (unsafe code), checks each finding in the code, and writes one report ordered by severity. In a game project it also checks the official Roblox and Unity rules on the server code.

| Command | What it does |
|---|---|
| `/vistoria` | The three tools, the check, its own reading of the entry points, then Claude Security if you confirm the cost |
| `/vistoria baixo`, `medio` or `alto` | The same, with that effort in Claude Security |
| `/vistoria rapida` | The three tools and the check |
| `/vistoria mudanca` | Only what changed, before a commit |

- It changes nothing in the project: the report stays outside it, and fixing is a separate request.
- A tool that did not run is reported as not run, never as "nothing found". Finding little does not prove the project is safe.
- No pentest: nothing is executed or tested live.
- Tested end to end on small projects with planted flaws, so this shows the command works, not how well it does on real code. The cost question and the medium and high efforts of Claude Security were not tested.

## Install

**Claude Code**: copy the skill folders you want into `~/.claude/skills/`.

```bash
git clone https://github.com/FFloriani/skills.git
cd skills
cp -r skills/datamine ~/.claude/skills/      # or theorycraft, skillsmp-search, better-readme, vistoria
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
| vistoria | Claude Code, Python 3 (standard library only), and `gitleaks`, `osv-scanner` and `semgrep` on your `PATH`. OSV-Scanner sends package names and versions to osv.dev, and Semgrep downloads its rules from semgrep.dev. The [Claude Security](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/claude-security) plugin is optional. Optional settings go in `~/.config/vistoria/config.json`: `base` (folder for tools and reports, default `~/.vistoria`) and `dono_github` (your GitHub account, so it knows which repositories are yours). |

The instructions in datamine, theorycraft, better-readme and vistoria are written in Portuguese; skillsmp-search is in English.

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
