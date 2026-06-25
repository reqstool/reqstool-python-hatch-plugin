# Contributing to reqstool-python-hatch-plugin

Thank you for your interest in contributing!

For DCO sign-off, commit conventions, and code review process, see the organization-wide [CONTRIBUTING.md](https://github.com/reqstool/.github/blob/main/CONTRIBUTING.md).

## Prerequisites

- Python 3.13+
- [Hatch](https://hatch.pypa.io/) (`pip install hatch`)
- [reqstool](https://github.com/reqstool/reqstool-client) (`pipx install reqstool`)
- [OpenSpec](https://github.com/Fission-AI/OpenSpec) (`npm install -g @fission-ai/openspec`)

## Setup

```bash
git clone https://github.com/reqstool/reqstool-python-hatch-plugin.git
cd reqstool-python-hatch-plugin
hatch env create
```

If using Claude Code, opening this repo will prompt you to confirm adding the `reqstool-ai`
marketplace and enabling the `reqstool`/`reqstool-openspec` plugins (configured in
`.claude/settings.json`) — accept the prompt.

Then regenerate the `opsx` slash commands and OpenSpec skills
(`.claude/commands/opsx/`, `.claude/skills/openspec-*`) — they're CLI-generated tool scaffolding,
not committed to the repo:

```bash
openspec update   # or: openspec init --tools claude --force
```

## Build & Test

```bash
hatch build
hatch run test
```

## Self-applied traceability (`docs/reqstool/`)

This project dogfoods itself: `hatch run dev:python scripts/generate_annotations.py` scans its
own `src`/`tests/unit`/`tests/e2e` for `@Requirements`/`@SVCs` decorators and writes
`build/reqstool/annotations.yml`. Check status with:

```bash
hatch build --target wheel && hatch run dev:pytest && hatch run dev:python scripts/generate_annotations.py
reqstool status --check-all-reqs-met local -p docs/reqstool
```
