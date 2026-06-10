# sr-obsidian

> A Claude Code plugin for managing Obsidian project documentation — hub notes, WBS, history, and folder structure, all in one place.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Plugin-blueviolet)](https://claude.ai/code)
[![Status](https://img.shields.io/badge/Status-Early%20Stage-orange)](.)

> English | [한국어](./README.ko.md)

---

## Why

Managing project documentation in Obsidian involves repetitive patterns:

- Every new project needs the same folder structure (hub, WBS, docs/, diagrams/)
- Hub notes drift out of sync as new files are added
- Architecture decisions scatter across notes with no ADR trail
- HTML visualizations end up in the wrong folder, breaking Obsidian iframes

sr-obsidian encodes a proven documentation pattern (extracted from the PSP project) into a set of skills that enforce consistency across all projects in your vault.

---

## Document Hierarchy

```
docs/reports/{report}.md     ← source of truth (full analysis, open questions)
        ↓ select
diagrams/{report}.html       ← full visualization (sr-obsidian:visualize)
        ↓ curate
diagrams/{report}-delivery.html  ← delivery version (for stakeholders)
```

---

## Skills

| Skill | Invoke | Purpose |
|-------|--------|---------|
| **sr-obsidian** | `/sr-obsidian` | **Workflow entry point** — orchestrates new project setup or existing project management |
| capture | `sr-obsidian:capture` | Fleeting note capture — keyword-only, no structure, saved to 00-inbox/ |
| study | `sr-obsidian:study` | Chapter literature note → permanent note extraction (2-phase: analyze → extract) |
| wiki | `sr-obsidian:wiki` | LLM Wiki term page creation — scan / create / index modes |
| scaffold | `sr-obsidian:scaffold` | Zettelkasten project scaffold — book study, knowledge area, or vault bootstrap |
| iss | `sr-obsidian:iss` | Create full ISS incident/issue structure (hub + WBS + steps/ + comms/) |
| hub | `sr-obsidian:hub` | Manage hub note links, KPIs, ISS references |
| wbs | `sr-obsidian:wbs` | WBS phase setup and progress tracking |
| history | `sr-obsidian:history` | ADR creation, decision log, meeting notes |
| visualize | `sr-obsidian:visualize` | MD → HTML via claude-visualize, saved to diagrams/ with paired MD |
| audit | `sr-obsidian:audit` | Validate project structure against the standard |
| migrate | `sr-obsidian:migrate` | Move non-standard files to the correct locations |
| daily | `sr-obsidian:daily` | Create or refresh today's daily note — Issue → branch → write → commit → PR automation |
| weekly | `sr-obsidian:weekly` | Weekly business report (Thu–Wed cycle) — collect daily notes, draft, full PR automation |
| retro | `sr-obsidian:retro` | Weekend retrospective (Mon–Fri cycle) — KPI and open-issue review, full PR automation |
| adr | `sr-obsidian:adr` | Record technical decisions as ADRs in 20-areas/{project}/adr/ |
| archive | `sr-obsidian:archive` | Batch-move completed ISS (closed hub + all steps done) to 40-archives/ |
| search | `sr-obsidian:search` | Natural-language vault search — returns related notes for any query |
| defuddle | `sr-obsidian:defuddle` | Clip a URL into a clean markdown fleeting note in 00-inbox/ |
| lint-wiki | `sr-obsidian:lint-wiki` | LLM Wiki quality checks — structural (orphan, dangling link) + semantic |
| canvas | `sr-obsidian:canvas` | Create/edit Obsidian .canvas files (JSON Canvas) — timelines, dependency maps, mindmaps |
| obsidian-bases | `sr-obsidian:obsidian-bases` | Create/edit Obsidian .base database views — filter, sort, aggregate vault notes |
| obsidian-markdown | `sr-obsidian:obsidian-markdown` | Obsidian Flavored Markdown syntax reference (wikilink, callout, Dataview, Mermaid) |

---

## Standard Folder Structure

```
{project}/
├── {project-id} 프로젝트 현황.md   ← hub (sr-obsidian:hub)
├── {project-id} WBS.md             ← WBS (sr-obsidian:wbs)
│
├── docs/
│   ├── specs/        ← component roles, interfaces, requirements
│   ├── architecture/ ← architecture analysis, expert reviews, constraints
│   ├── adr/          ← Architecture Decision Records (sr-obsidian:history)
│   ├── reports/      ← report source MD files
│   ├── runbook/      ← operational procedures (Phase 5+)
│   └── config/       ← infrastructure and environment config
│
├── diagrams/         ← HTML only (sr-obsidian:visualize output)
├── features/         ← FT-xxx feature development folders
├── phases/           ← phase step files
└── meetings/         ← meeting notes (sr-obsidian:history)
```

---

## Installation

```bash
# Add marketplace
claude plugins marketplace add SeokRae/sr-obsidian

# Install
claude plugins install sr-obsidian
```

Restart Claude Code, then verify:

```bash
claude plugins list
#   ❯ sr-obsidian@sr-obsidian
#     Version: 0.1.0
#     Scope: user
#     Status: ✔ enabled
```

---

## Reference Implementation

The PSP project (`20-areas/payment/psp/`) is the reference implementation for this plugin's patterns.

---

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md).

## License

MIT © SeokRae
