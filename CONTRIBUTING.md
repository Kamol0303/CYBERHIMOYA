# Contributing (short)

1. Branch: `CURSOR/<name>-b1ff` (cloud) or feature branch off `main`.
2. Defensive-only: no exploit/C2/active probing code.
3. Before PR: `make test` (lint, extension validate, API pytest, web build, smoke).
4. Useful targets: `make feed`, `make feed-keys`, `make docker-up`, `make api-dev`.
5. Do not invent AQ-039 official IIV/UZCERT endpoints — use env templates only.
6. Prefer small, reviewable commits.
7. Current platform version: **0.2.1** (`apps/api`, `apps/web`, extension).
