# skills

Skills I built for Claude (Claude Code and claude.ai). Each skill lives in its own folder under `skills/`.

| Skill | What it does | How to call it |
|---|---|---|
| [datamine](skills/datamine/) | Studies games installed on your PC to learn how they were made: identifies the engine, extracts assets and data tables, decompiles, deobfuscates and decrypts a copy for reading only, and documents mechanics and formulas so you can build your own game. Content is in Portuguese. | `/datamine` |
| [theorycraft](skills/theorycraft/) | For players: scans 100% of a game's installed files and builds a complete knowledge base (SQLite database, CSVs and docs): what every item, spell and skill does and where to get it, quest walkthroughs, interactive maps, enemy and boss movesets with frame data, best builds, combos and rotations, cheapest crafting routes, MMO daily routines, and patch diffs. Content is in Portuguese. | `/theorycraft` |
| [skillsmp-search](skills/skillsmp-search/) | Searches the [SkillsMP](https://skillsmp.com) marketplace for ready-made skills by keyword, category, occupation or language. | `/skillsmp-search` |

## Installation

**Claude Code**: copy the skill folder into `~/.claude/skills/`.

```bash
git clone https://github.com/FFloriani/skills.git
cp -r skills/skills/datamine ~/.claude/skills/
```

Then type `/datamine` (or just ask normally and Claude will pick it up).

**claude.ai**: zip the skill folder and upload it in the Skills section of your settings.

## Extra setup

- **skillsmp-search** needs a SkillsMP API key (create one at skillsmp.com). Put it in a `SKILLSMP_API_KEY` environment variable or in a file at `~/.config/skillsmp/key`, with the key on a single line.
- **datamine** needs Python 3 only for the optional scripts in `scripts/`.

## Structure

```
skills/
  <skill-name>/
    SKILL.md        instructions Claude reads
    references/     supporting material, loaded only when needed
    scripts/        programs Claude can run
```
