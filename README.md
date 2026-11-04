# skills

Skills for Claude Code and claude.ai: start a new project, review finished code, check a project for security flaws, study game files, find and vet community skills, write GitHub READMEs.

[![Last commit](https://img.shields.io/github/last-commit/FFloriani/skills)](https://github.com/FFloriani/skills/commits/main)

A skill is a folder with a `SKILL.md`. Claude loads it when your request matches its description, or when you type `/<skill-name>`. The exceptions are `revisar` and `vistoria`: they are slow and use many tokens, so they run only when you type the command.

## Which skill do you need?

| You want to | Skill | Call it |
|---|---|---|
| Learn how a game installed on your PC was made, to build your own | [datamine](skills/datamine/) | `/datamine` |
| Get exact answers about a game you play: items, bosses, builds, maps, crafting routes | [theorycraft](skills/theorycraft/) | `/theorycraft` |
| Find ready-made skills and install them only after a security check | [skillsmp-search](skills/skillsmp-search/) | `/skillsmp-search` |
| Write, improve or audit a GitHub README, and get About text, topics and a launch plan | [better-readme](skills/better-readme/) | `/better-readme` |
| Start a new app, site, game or tool: study the similar products, decide in one message, get version 0.1 running | [comecar](skills/comecar/) | `/comecar` |
| Have a fresh agent check that finished code does what was asked, proving each bug by reproducing it | [revisar](skills/revisar/) | `/revisar` |
| Check a project, site, app or game for security flaws, or check what changed before a commit | [vistoria](skills/vistoria/) | `/vistoria` |

## What each one does

### datamine

Identifies the engine of a game installed on your PC, copies the files to a study folder, extracts assets and data tables, decompiles and deobfuscates, and decrypts a **copy** for reading only. The output is notes on mechanics and formulas (XP curves, drop rates, scaling) you can port to your own game.

- Read-only and local: nothing is written back to the game, and nothing extracted is published.
- Single-player or offline games only.
- Mechanics and formulas can be ported; assets, names, text and exact numbers are recreated, not copied.

### theorycraft

For players. Scans the installed files of a game and builds a knowledge base (SQLite database, CSVs and documents): what each item, spell and skill does and where to get it, quests, maps, boss movesets with frame data, best builds, combos, crafting routes, MMO daily routines and patch diffs.

- Read-only: no injection, memory reading or automated traffic to game servers. Watching your own PC's traffic is fine.
- Online games: rules that run on the server are not in the files, so the skill marks them as measured in play or from a cited community source, never guessed.
- Compiled code: with the [REA](https://github.com/morluto/rea) (npm `rea-agents`) MCP server installed, it maps function names to addresses (Unity IL2CPP), reads class members (Unity Mono), finds a function by the text it uses (native) and keeps the evidence for every formula.
- Results go to a fixed games folder you choose, never into a git repository: what comes out of a game stays on your PC.

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

- Runs only when you type `/vistoria`: it is slow and uses many tokens, so Claude never starts it on its own.
- It changes nothing in the project: the report stays outside it, and fixing is a separate request.
- A tool that did not run is reported as not run, never as "nothing found". Finding little does not prove the project is safe.
- No pentest: nothing is executed or tested live.
- Tested end to end on small projects with planted flaws, so this shows the command works, not how well it does on real code. The cost question and the medium and high efforts of Claude Security were not tested.

### comecar

Starts a new project from an idea written the way you would say it. Before building, parallel agents study the similar products:
- what they do and what they get right;
- what their users complain about, counted by theme;
- what nobody solves;
- what breaks inside them (from their GitHub issues and API docs).

Then you get one message with 5 to 7 decisions, each with a recommendation drawn from that research: answer "yes" or the number you want changed. It writes a short SPEC.md with testable requirements and the project's CLAUDE.md, builds version 0.1 with the main screen working end to end, checks it, and tells you that `/revisar` and `/vistoria rapida` can check it more deeply when you want.

| Command | What it does |
|---|---|
| `/comecar <idea>` | Everything above |
| `/comecar rapido <idea>` | For small things: short research, decisions, build |
| `/comecar pesquisa <idea>` | Research, decisions and SPEC.md only, to judge an idea before building |

- No approval steps between stages: it stops only for the decisions message, spending money, publishing or installing outside the project.
- Used end to end once, on a real desktop tool: research, decisions, version 0.1 and a working app. The research stage alone was also tested on another project: 4 agents, about 7 minutes, 78 findings. There is no formal measurement yet.

### revisar

A fresh agent that never saw the conversation checks finished code against what was asked. It runs the tests and the program, writes a small reproduction for every suspicion and counts as a bug only what it reproduced. Before hunting rare cases, it opens the program the way a user does and runs the main flow end to end. It fixes each bug at the cause, keeps the reproduction as an automated test, and if it changed anything a second fresh reviewer checks only the fixes and what they touch (up to 3 rounds).

- Runs only when you type `/revisar`: it is slow and uses many tokens, so Claude never starts it on its own, not even to check its own work. It states the cost when it starts: a round takes 10 to 40 minutes, depending on the size of the project.
- `/revisar duplo` runs two independent reviewers for code that must not fail.
- A project in use (a live tool, like an MCP server other conversations rely on) is reviewed in an isolated copy. When the program reads data outside the repository, the review ends with a read-only check against the real data.
- The list of what was asked and the report stay in the project, in `docs/revisoes/<date>/`.
- No commit, no publishing; it runs project code, so use it on your own projects.
- Measured once: on the same game-server task, a lone agent scored 64 in a blind review and 84 with this reviewer added, which found a serious bug the author's tests missed, for about US$ 3.
- Blind test of this version, on game-server code with a known serious bug (an ID that repeats after a crash and locks the player out for good). The author's 58 tests pass with that bug in place:
  - An earlier version, which trusted thousands of single-operation crash tests, missed it.
  - After the reviewer was told to read what backs each guarantee first and break it with multi-step sequences, it found and fixed the bug in 2 of 2 runs. One run also found a second, planted bug.
  - Each run took 12 to 14 minutes and about US$ 3.50, with 2 reviewers.
  - That is one run per case, so read it as a sign, not proof.

## Install

**Claude Code**: copy the skill folders you want into `~/.claude/skills/`.

```bash
git clone https://github.com/FFloriani/skills.git
cd skills
cp -r skills/datamine ~/.claude/skills/      # or comecar, revisar, vistoria, theorycraft, skillsmp-search, better-readme
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
| theorycraft | Python 3 for the scripts. `openpyxl` is optional (`pip install openpyxl`) for `.xlsx` export; without it you get one CSV per table. The REA MCP server is optional, for reading compiled code. |
| skillsmp-search | Python 3. skills.sh needs nothing else. For SkillsMP also add an API key (create one at skillsmp.com): set `SKILLSMP_API_KEY`, or put the key on a single line in `~/.config/skillsmp/key`. Without the key you still get skills.sh. |
| better-readme | Python 3 for the three scripts (standard library only). One of them reads the public GitHub API; `GITHUB_TOKEN` is optional (private repositories, rate limit). |
| comecar | Claude Code with subagents and web search. A deep research tool is optional; `gh` helps with GitHub issues. Points you to `revisar` and `vistoria` at the end; install those to use the two commands. |
| revisar | Claude Code with subagents, and whatever the project needs to build and run its tests. |
| vistoria | Claude Code, Python 3 (standard library only), and `gitleaks`, `osv-scanner` and `semgrep` on your `PATH`. OSV-Scanner sends package names and versions to osv.dev, and Semgrep downloads its rules from semgrep.dev. The [Claude Security](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/claude-security) plugin is optional. Optional settings go in `~/.config/vistoria/config.json`: `base` (folder for tools and reports, default `~/.vistoria`) and `dono_github` (your GitHub account, so it knows which repositories are yours). |

The instructions in comecar, revisar, vistoria, datamine, theorycraft and better-readme are written in Portuguese; skillsmp-search is in English.

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
