# BreakPoint project progress

**Status date:** 2026-10-31  
**Purpose:** Current handoff for coding agents. Read this file together with [`PLAN.md`](PLAN.md); this file reports what exists now, while `PLAN.md` remains the original project plan.

## Project in one paragraph

BreakPoint is a research demo for measuring whether an AI agent improves at selecting approved security tools across repeatable runs in intentionally vulnerable labs. The intended users are security researchers and builders who want to evaluate agent performance with reproducible records. The current public demo shows a fixed scanner baseline; it is not yet an autonomous-agent benchmark.

## Current state

| Area | Status | What exists |
| --- | --- | --- |
| Public demo | Done | Static page at <https://breakpoint.sfo.unikraft.app>; baseline record at <https://breakpoint.sfo.unikraft.app/baseline-run.json>. Both are served from a Unikraft instance in SFO. |
| Vulnerable lab | Done for first environment | Digest-pinned Vulhub Struts 2.3.30 / CVE-2017-5638 Compose setup. Target has no outbound route and is not part of the public demo. A loopback-only Nginx proxy exposes it at `http://127.0.0.1:18080`. |
| Baseline run | Done | One fixed Nmap NSE check against the local lab, recorded as a run. It detects the vulnerable version using the published check; it does not execute a command or read a file. |
| Run storage | Foundation done | Append-only SQLite schema and CLI in `run_store.py`, covering runs, tool invocations, and transcript events. The scanner baseline runner appends to the local database. |
| Tool allowlisting | Implemented; invalid decisions checked offline | `agent_demo.py` offers only fixed HTTP metadata and Nmap checks, with fixed loopback scope, empty argument objects, bounded output, and no shell interface. Unknown tools and unexpected arguments were rejected without dispatch in fake-model runs. |
| Scoring and metrics | Partial | Baseline outcome and a trusted agent verdict are represented; tool calls, elapsed time, model usage, tool version, and script hash are recorded where available. Token cost is currently null. No agent comparison exists yet. |
| Agent/orchestrator | Offline implementation added; partially checked | `agent_demo.py` has a bounded OpenAI-compatible decision loop and records JSONL events plus SQLite records. Syntax compilation and offline invalid-decision/budget paths passed; the fixed-tool path and live model path have not been run. |
| Learning/memory | Extraction path implemented; no demonstration yet | The runner can extract source-linked structured notes and pass a notes file into another run. No run pair has been completed, so there is no evidence of improvement. |
| TrueForge/TrueFoundry | Not started | A token was configured locally during setup, but there is no workspace or agent deployment recorded in the repository. Never print or commit token values. |
| Additional environments / Shelled AI | Not started | Only the Struts lab is present. The optional Shelled AI PR/report track has not been pursued. |

## Important artifacts

- [`PLAN.md`](PLAN.md): original goals, architecture, metrics, safety requirements, and hackathon schedule.
- [`README.md`](README.md): project summary, public demo, local preview, lab and deployment pointers.
- [`index.html`](index.html), [`styles.css`](styles.css): static public demo.
- [`baseline-run.json`](baseline-run.json): public metadata for the measured scanner baseline. This is a separate, intentionally limited public representation; detailed tool output is stored locally.
- [`lab/compose.yaml`](lab/compose.yaml), [`lab/nginx.conf`](lab/nginx.conf), [`lab/README.md`](lab/README.md): isolated local lab and operator instructions.
- [`lab/run_baseline.py`](lab/run_baseline.py): fixed Nmap baseline runner.
- [`run_store.py`](run_store.py), [`docs/run-record.md`](docs/run-record.md): append-only local run storage and record format.
- [`agent_demo.py`](agent_demo.py), [`compare_runs.py`](compare_runs.py), [`docs/demo.md`](docs/demo.md): bounded local agent runner, notes extraction, local comparison command, task, scoring rule, and initial budgets. Core code compiles; only the no-provider fake budget and invalid-decision paths have been run.
- Local attempt events and memory notes are written under ignored `data/events/` and `data/notes/` directories; completed runs are stored in ignored `data/runs.sqlite3` by default.

## Recorded baseline

The public baseline record has run ID `struts2-s2045-nmap-20261031T225353604818Z`. It reports:

- Environment: Vulhub Struts 2.3.30 image `vulhub/struts2@sha256:b992e080d8e5ad332bf526ae26124d28f56ca4fc9e0eaa91510dbee9870eb2c8`.
- Tool: Nmap 7.992 and its installed `http-vuln-cve2017-5638` NSE script, identified by the SHA-256 in `baseline-run.json`.
- Scope: `127.0.0.1:18080` only.
- Result: vulnerability detected; one tool call; 11,170 ms; token counts unavailable.

The `success` outcome means the vulnerability check found the expected vulnerable target. Do not present this as a model-agent success or as evidence of learning.

## Local lab operations

The development machine uses rootless Docker via the user socket. The operator setup documented in `lab/README.md` is:

```sh
systemctl --user enable --now docker.socket
export DOCKER_HOST="unix://${XDG_RUNTIME_DIR}/docker.sock"
docker compose -f lab/compose.yaml up -d
curl --fail --silent --show-error http://127.0.0.1:18080/
python3 lab/run_baseline.py
python3 run_store.py list
```

Stop the lab with `docker compose -f lab/compose.yaml down`. The proxy is intentionally loopback-only; the vulnerable target stays on an internal network. Do not publish the lab or connect it to the Unikraft-hosted demo. In this Codex environment, Docker socket access previously required an approved escalated command; do not assume ordinary sandbox commands can reach it.

## Deployment and repository notes

- Public deployment uses the Unikraft CLI and existing local configuration. The last recorded deployment was `breakpoint.sfo.unikraft.app`; the currently deployed page included the baseline JSON.
- Keep `.env` and all API tokens out of Git and command output. `.env` is ignored.
- Baseline work immediately before this implementation was committed as `d74edd3` (`Record Struts scanner baseline`) and pushed to `origin/master`.
- `TRUEFOUNDRY_TOKEN` exists in local `.env`, but no provider endpoint or model ID is configured. The new runner requires `BREAKPOINT_MODEL_ENDPOINT`, `BREAKPOINT_MODEL`, and `BREAKPOINT_MODEL_API_KEY`; it does not load `.env` automatically. Never print or commit token values.
- `python3 -m py_compile agent_demo.py compare_runs.py run_store.py` succeeded. Fake-model `budget_exhaustion`, `unknown_tool`, and `unexpected_arguments` runs each stopped after five model requests with zero tool calls; the latter two were rejected before dispatch. These records used `/tmp/breakpoint-offline-check.sqlite3` and are not real model results. The Nmap dispatch/success path and note extraction have not been exercised.
- No live model calls or agent runs have been performed; the only completed vulnerability measurement remains the Nmap scanner baseline above.
- The hosted page has not been updated to describe the new local runner. Deployment remains deliberately separate.

## Recommended next work

1. Review and validate the remaining paths in `agent_demo.py`: run the fake-model fixed-tool scenario after the lab is ready, then check note extraction and the trusted positive-verdict path. Offline budget and invalid-decision scenarios have already passed.
2. Obtain an OpenAI-compatible HTTPS endpoint and model ID, then configure the three `BREAKPOINT_MODEL_*` environment variables without exposing credentials. A TrueFoundry token by itself is not enough to call a model.
3. Once the provider is configured and the lab is ready, make one no-memory run, extract notes, and make one same-settings run with those exact notes. Preserve any failed attempts and note extraction usage.
4. Produce the local two-run comparison with `compare_runs.py` and label it “illustrative demo; two attempts; not evidence of reliable improvement.” Do not claim improvement unless it happened; this small demonstration is not a rigorous evaluation.
5. Update this file with actual checks and run IDs. Keep deployment, additional environments, and rigorous repeated evaluation deferred as directed by [`LUNA_PLAN.md`](LUNA_PLAN.md).

The original plan also calls for more environments, a run 1 versus run N chart, and possibly the optional Shelled AI track; these remain later work, not completed deliverables.
