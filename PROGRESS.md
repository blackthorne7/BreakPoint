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
| Tool allowlisting | Implemented and exercised | `agent_demo.py` exposes only fixed HTTP metadata and Nmap checks on loopback, validates empty arguments and fixed IDs, caps output, and has no shell interface. Offline invalid-decision scenarios and the live fixed Nmap path have run. |
| Scoring and metrics | Working for the local demo | Both agent attempts have a trusted positive verdict, one tool call, elapsed time, and token counts. Provider cost was not returned, so cost remains unavailable. |
| Agent/orchestrator | Local illustrative demo complete | Two real TrueFoundry model runs used the bounded loop and wrote event logs and SQLite records. The hosted demo remains the static scanner-baseline page. |
| Learning/memory | Mechanism demonstrated; improvement not established | Notes were extracted from the first run, with source event IDs, and supplied to the second. Both attempts chose the same successful tool in one call; the second was about 1.45 seconds faster, which is not evidence of reliable improvement. |
| TrueForge deployment | Not started | The local TrueFoundry gateway was used for the two attempts above, but no agent/workspace deployment to the TrueForge sponsor platform is recorded. |
| Additional environments / Shelled AI | Not started | Only the Struts lab is present. The optional Shelled AI PR/report track has not been pursued. |

## Important artifacts

- [`PLAN.md`](PLAN.md): original goals, architecture, metrics, safety requirements, and hackathon schedule.
- [`README.md`](README.md): project summary, public demo, local preview, lab and deployment pointers.
- [`index.html`](index.html), [`styles.css`](styles.css): static public demo.
- [`baseline-run.json`](baseline-run.json): public metadata for the measured scanner baseline. This is a separate, intentionally limited public representation; detailed tool output is stored locally.
- [`lab/compose.yaml`](lab/compose.yaml), [`lab/nginx.conf`](lab/nginx.conf), [`lab/README.md`](lab/README.md): isolated local lab and operator instructions.
- [`lab/run_baseline.py`](lab/run_baseline.py): fixed Nmap baseline runner.
- [`run_store.py`](run_store.py), [`docs/run-record.md`](docs/run-record.md): append-only local run storage and record format.
- [`agent_demo.py`](agent_demo.py), [`compare_runs.py`](compare_runs.py), [`docs/demo.md`](docs/demo.md): bounded local agent runner, notes extraction, local comparison command, task, scoring rule, and budgets.
- Local attempt events and memory notes are written under ignored `data/events/` and `data/notes/` directories; completed runs are stored in ignored `data/runs.sqlite3` by default.

## Recorded baseline

The public baseline record has run ID `struts2-s2045-nmap-20261031T225353604818Z`. It reports:

- Environment: Vulhub Struts 2.3.30 image `vulhub/struts2@sha256:b992e080d8e5ad332bf526ae26124d28f56ca4fc9e0eaa91510dbee9870eb2c8`.
- Tool: Nmap 7.992 and its installed `http-vuln-cve2017-5638` NSE script, identified by the SHA-256 in `baseline-run.json`.
- Scope: `127.0.0.1:18080` only.
- Result: vulnerability detected; one tool call; 11,170 ms; token counts unavailable.

The `success` outcome means the vulnerability check found the expected vulnerable target. Do not present this as a model-agent success or as evidence of learning.

## Illustrative agent demonstration

This is the two-attempt Phase A demo from `LUNA_PLAN.md`, not a controlled evaluation:

| Attempt | Run ID | Outcome | Tool calls | Wall time | Input / output tokens | Memory |
| --- | --- | --- | ---: | ---: | ---: | --- |
| First, no memory | `struts2-agent-20261101T004643478104Z` | Confirmed vulnerable | 1 | 16,609 ms | 1,163 / 162 | No |
| Second, with extracted notes | `struts2-agent-20261101T004810839147Z` | Confirmed vulnerable | 1 | 15,163 ms | 1,635 / 201 | Yes |

Both used `tfy-managed/gpt-6-luna` and the fixed Nmap 7.992 `http-vuln-cve2017-5638` script (SHA-256 `af5ce476160bc9a68fe33b6c4d82e24eac2d3879c21af12975ae112ab0d17ab0`). The scanner returned a positive result, and the trusted evaluator accepted the model's cited invocation in both runs. The note extraction used 897 input and 239 output tokens. Cost was unavailable for all three requests. The second run was faster in this sample, but both runs selected the same tool in one call; do not claim learning or reliable improvement from this pair.

Two earlier attempts were also retained as failed infrastructure records: `struts2-agent-20261101T002837864300Z` failed DNS resolution in the sandbox; `struts2-agent-20261101T003029607552Z` was blocked by Cloudflare with error 1010 before model inference. After adding a descriptive User-Agent, a non-inference `/models` request returned HTTP 200 and listed the configured model. The subsequent two runs and extraction succeeded.

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
- The user configured `https://gateway.truefoundry.ai`, model `tfy-managed/gpt-6-luna`, and renamed the local PAT variable to `TRUEFOUNDRY_GPT_LUNA_TOKEN`. The runner uses the gateway's `/chat/completions` route and reads only that named token from `.env` (or `BREAKPOINT_MODEL_API_KEY` if explicitly set). Never print or commit token values.
- TrueFoundry initially returned Cloudflare 1010 to Python's default User-Agent; the runner now identifies itself as `BreakPoint-security-benchmark/1.0` and the model-list check plus inference succeeded.
- Syntax compilation passed. Offline fake `budget_exhaustion`, `unknown_tool`, and `unexpected_arguments` paths each stopped after five requests with zero tool calls. Two real bounded attempts and one notes extraction then completed; see the run table above.
- Detailed logs, notes, and SQLite records remain local under ignored `data/events/`, `data/notes/`, and `data/runs.sqlite3`. The public `baseline-run.json` and hosted page still describe only the scanner baseline.
- The hosted page has not been updated to describe the new local runner. Deployment remains deliberately separate.

## Recommended next work

1. Decide whether to publish a limited, clearly labeled export of the local two-run comparison on the static demo. Keep detailed transcripts private and scanner-baseline data separate.
2. Decide separately whether to begin Phase B evaluation. Before spending on more calls, set the cohort size, budget, reset procedure, and comparison protocol as described in [`LUNA_PLAN.md`](LUNA_PLAN.md).
3. Keep TrueForge deployment, additional environments, and the optional Shelled AI track deferred until explicitly prioritized.

The original plan also calls for more environments, a run 1 versus run N chart, and possibly the optional Shelled AI track; these remain later work, not completed deliverables.
