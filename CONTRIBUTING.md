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
3. Bump the version in **both** `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` (see Versioning below)
4. Document the skill in `README.md` and `README.ko.md`
5. Test against at least one real Obsidian vault project

## Versioning

This project uses [Semantic Versioning](https://semver.org/) (`MAJOR.MINOR.PATCH`).

| Change type | Version segment | Example |
|-------------|----------------|---------|
| New skill added | `MINOR` | 0.1.0 → 0.2.0 |
| Existing skill behavior extended | `MINOR` | 0.2.0 → 0.3.0 |
| Bug fix, wording, doc only | `PATCH` | 0.2.0 → 0.2.1 |
| Skill removed or interface broken | `MAJOR` | 0.x.x → 1.0.0 |

**Rule**: version bump must be included in the **same PR** as the change — never as a separate follow-up PR.

Files to update together:

```
.claude-plugin/plugin.json      → "version"
.claude-plugin/marketplace.json → "metadata.version" + "plugins[0].version"
```

## Release workflow

After a PR is merged:

```bash
# 1. Pull latest main
git checkout main && git pull origin main

# 2. Create annotated tag
git tag -a v{version} -m "v{version}: {one-line summary}"

# 3. Push tag
git push origin v{version}

# 4. Create GitHub Release (auto-generates from tag)
gh release create v{version} --title "v{version}" --generate-notes
```

Example:
```bash
git tag -a v0.2.0 -m "v0.2.0: daily·weekly·retro 스킬 추가"
git push origin v0.2.0
gh release create v0.2.0 --title "v0.2.0" --generate-notes
```

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
