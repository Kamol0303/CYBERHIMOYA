# AGENTS.md

## Cursor Cloud specific instructions

### What this repository is

This repo is **documentation-only**. It contains an IEEE 830-style **SRS + SDD**
specification (in Uzbek) for the planned "Cyber Guardian AI" / "CYBERHIMOYA"
defensive-cybersecurity product. All tracked files are Markdown under
`docs/cyber-guardian-ai/` (index: `docs/cyber-guardian-ai/README.md`).

There is **no application source code, no package manifest, no lockfile, no
build system, no automated tests, and no services** to run. There is nothing to
compile, lint (no linter is configured), or unit-test. The "product" is the
specification text itself. Work here means editing/reviewing Markdown.

### Editing conventions (from the docs' own acceptance criteria)

- Requirements must use the `FR-xxx` / `NFR-xxx` numbering format.
- Diagrams must be valid **Mermaid** fenced code blocks (```` ```mermaid ````).
  GitHub renders these natively in the PR/preview.
- Open questions/ambiguities belong only in
  `docs/cyber-guardian-ai/assumptions-and-open-questions.md`.
- Content must stay defensive-only (detect/warn/block); no offensive/exploit
  material. See the "Himoya-only nizom" section in the docs README.

### Previewing the docs locally (optional, not required)

No renderer is committed to the repo. If you want a live local preview with
tables + rendered Mermaid diagrams, render the Markdown to HTML and serve it
(GitHub already renders these files on push). Any rendering tooling is a local
convenience only — do **not** add it to the update script or commit it, since it
is not part of the codebase.
