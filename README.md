# skills

Skills I built for Claude (Claude Code and claude.ai). Each skill lives in its own folder under `skills/`.

| Skill | What it does | How to call it |
|---|---|---|
| [datamine](skills/datamine/) | Studies games installed on your PC to learn how they were made: identifies the engine, extracts assets and data tables, decompiles, deobfuscates and decrypts a copy for reading only, and documents mechanics and formulas so you can build your own game. Content is in Portuguese. | `/datamine` |
| [theorycraft](skills/theorycraft/) | For players: scans 100% of a game's installed files and builds a complete knowledge base (SQLite database, CSVs and docs): what every item, spell and skill does and where to get it, quest walkthroughs, interactive maps, enemy and boss movesets with frame data, best builds, combos and rotations, cheapest crafting routes, MMO daily routines, and patch diffs. Content is in Portuguese. | `/theorycraft` |
| [skillsmp-search](skills/skillsmp-search/) | Searches the [SkillsMP](https://skillsmp.com) marketplace for ready-made skills by keyword, category, occupation or language. Before any skill from the marketplace is installed it goes through a safety gate: quarantine, a static scanner for prompt injection, hidden characters, auto-run hooks, credential access and malicious scripts, a manual read, and a verdict you approve. | `/skillsmp-search` |
| [better-readme](skills/better-readme/) | Creates, improves, audits and translates GitHub READMEs. Reads the repository to find the real facts, picks the right skeleton for the project type (library, CLI, desktop app, game or mod, API, awesome list), and writes a README with value proposition, quick start, features, media and diagrams, a download section with portable build, sponsor links (GitHub Sponsors, Buy Me a Coffee, Ko-fi, Pix), translations and accessibility; then validates links, images and HTML (P0/P1/P2 audit). Content is in Portuguese. | `/better-readme` |

## Installation

**Claude Code**: copy the skill folder into `~/.claude/skills/`.

```bash
git clone https://github.com/FFloriani/skills.git
cp -r skills/skills/datamine ~/.claude/skills/
```

Then type `/datamine` (or just ask normally and Claude will pick it up).

**claude.ai**: zip the skill folder and upload it in the Skills section of your settings.

## Extra setup

- **skillsmp-search** needs a SkillsMP API key (create one at skillsmp.com). Put it in a `SKILLSMP_API_KEY` environment variable or in a file at `~/.config/skillsmp/key`, with the key on a single line. Python 3 runs both scripts (`search.py` and the `vet_skill.py` safety scanner); standard library only.
- **datamine** needs Python 3 only for the optional scripts in `scripts/`.
- **better-readme** needs Python 3 for the two scripts in `scripts/` (discover repository facts, audit a README). Standard library only, nothing to install.

## Structure

```
skills/
  <skill-name>/
    SKILL.md        instructions Claude reads
    references/     supporting material, loaded only when needed
    scripts/        programs Claude can run
```
