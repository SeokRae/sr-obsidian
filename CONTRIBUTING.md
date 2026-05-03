# Contributing to sr-obsidian

## What's welcome

- New skill proposals (e.g., skills for specific document types)
- Improvements to existing skill logic or templates
- Bug reports from real usage
- Documentation improvements
- Support for other vault structures beyond the PARA method

## How to contribute

1. Open an Issue first — describe what you want to change and why
2. Fork the repo and create a branch: `feature/{issue-number}-{description}`
3. Edit the relevant `skills/{skill-name}/SKILL.md`
4. Open a PR with `Closes #N` in the body

## Editing skills

Each skill lives in `skills/{skill-name}/SKILL.md`.

The frontmatter fields that matter most:

| Field | Effect |
|-------|--------|
| `description` | Controls when Claude auto-triggers this skill — most impactful |
| `allowed-tools` | Tools the skill can use — keep to minimum needed |
| `name` | Must match the directory name |

When proposing a change, include:
- Which skill and what version you tested against
- What problem you encountered with the current version
- What you changed and why
- How you verified the new behavior

## Adding a new skill

1. Create `skills/{skill-name}/SKILL.md` with required frontmatter
2. Add the skill path to `.claude-plugin/plugin.json` → `skills` array
3. Document the skill in `README.md` and `README.ko.md`
4. Test against at least one real Obsidian vault project

## Reporting issues

Open a GitHub Issue with:
- Which skill was involved
- What you expected to happen
- What actually happened
- Your vault folder structure (if relevant)

## Vault structure assumptions

This plugin assumes a PARA-based Obsidian vault with:
- Projects under `20-areas/payment/{project-id}/`
- Vault root at `/Users/sr/obsidian/sr-labs/` (absolute iframe paths — see known issue #TBD)

Contributions that make the vault root configurable are especially welcome.
