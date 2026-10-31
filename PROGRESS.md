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
| Tool allowlisting | Partial | The baseline runner fixes the target, port, and Nmap script in code. There is not yet an agent tool-dispatch layer or a general allowlist registry. |
| Scoring and metrics | Partial | Baseline outcome, one tool call, wall time, tool version, and script hash are recorded. Token use is unavailable for this non-agent run. No run comparison chart exists. |
| Agent/orchestrator | Not started | No model-driven selection loop, target lifecycle orchestrator, or agent transcript exists. The baseline runner invokes one predetermined tool. |
| Learning/memory | Not started | No strategy-note extraction, memory snapshots from prior agent runs, policy table, or repeated-run improvement demonstration. |
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
- Most recent recorded commit: `d74edd3` (`Record Struts scanner baseline`), pushed to `origin/master`.
- No test suite has been run or documented as required. If a future task explicitly asks for validation, distinguish automated tests from operational checks.

## Recommended next work

1. Define the agent-run success condition and scoring schema for the first environment. Keep scanner-baseline semantics distinct from agent-run semantics.
2. Build a small orchestrator around a model and a strictly fixed tool interface. Enforce the target scope and tool parameters in code, not only in the prompt; do not give the model arbitrary shell access.
3. Record each agent choice, invocation, result, transcript event, elapsed time, and available token usage through the existing run-store format.
4. Run repeated attempts against the same pinned lab and compare them. Begin with structured strategy notes as suggested in `PLAN.md`; only claim improvement if comparable runs show it.
5. Once the local loop and safety boundaries are clear, decide whether/how to deploy the agent on TrueForge. The public static demo can then link to real run-comparison data.

The original plan also calls for more environments, a run 1 versus run N chart, and possibly the optional Shelled AI track; these remain later work, not completed deliverables.
