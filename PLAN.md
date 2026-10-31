# Technical Handoff: Self-Improving Security-Benchmark Agent

## Scope note
This document covers architecture, scoring, agent-memory design, and sandboxing only. The agent's "attack" capability is scoped to **invoking existing, published, pre-built security tools and PoCs** (e.g. Metasploit modules, public CVE PoC scripts) against **known-vulnerable target environments** (e.g. Vulhub, DVWA, Metasploitable). No exploit code is generated or authored as part of this project — the agent's intelligence is in *selecting, sequencing, and learning from* existing tools, not in creating new attack logic.

## Context
7-day hackathon, sponsor tracks: Base44, Fetch.ai, TrueFoundry/TrueForge, Shelled AI, Stranger Builds. Day-1 prize exists but 7-day build is the real focus.

- **TrueForge** (primary track): "Build a self-improving agent." Done when: repo + agent running on TrueForge + a later run that beats run 1.
- **Shelled AI** (secondary, optional): requires ≥2 PRs to their repo (≥1 merged) + an EDGE_CASES.md report. Only pursue if there's bandwidth for the PR overhead.

## System architecture

**Core unit: "a run."** Every run is a replayable, versioned record:
- `environment_id` + version (which Vulhub/DVWA container, which snapshot)
- `agent_config_id` + version (model, tool list, memory state at start)
- `tool_invocation_log` (ordered list of: tool selected, parameters, target, result)
- `transcript` (full agent reasoning/output log)
- `outcome` (success/fail, plus the scoring metrics below)

Store runs in a simple append-only table (Postgres is fine). This is the backbone both the day-1 demo and the day-5 self-improvement proof are built on — don't skip structuring this early.

**Components:**
1. **Orchestrator** — spins up the target environment, hands the agent a toolbelt (a fixed list of pre-approved, pre-built tools it can call), runs the loop, records the run.
2. **Agent** — given target + toolbelt + memory from prior runs, decides which tool to try, in what order, with what parameters. This is the part that "gets smarter."
3. **Scorer** — evaluates the run against the target's known success condition (e.g. "flag retrieved," "shell obtained," "specific file read") — binary or graded.
4. **Memory store** — see below.

## Scoring
Track per run, so trends are visible across runs:
- **Outcome**: success / partial / fail (define "partial" per environment, e.g. got RCE but not the flag)
- **Steps/tool-calls to outcome**
- **Wall-clock time**
- **Token cost** (prompt + completion tokens across the run)
- **Tool-selection efficiency**: did it pick the right tool first, or iterate through wrong ones?

Day-5 deliverable: a chart of these metrics across runs 1→N on the same or similar environments, showing improvement.

## Agent memory / self-improvement design
This is the part worth designing carefully — a few options, roughly in order of buildability:

1. **Raw transcript replay** (simplest): next run's prompt includes a summary of prior runs' transcripts for this environment. Low engineering effort, but noisy and expensive in tokens as runs accumulate.
2. **Extracted strategy notes** (recommended): after each run, a summarization step extracts structured notes — "tool X failed because Y," "tool Z succeeded when preceded by W" — and these notes, not the raw transcript, are what's fed into the next run's context. Keeps context small and signal-dense as runs accumulate.
3. **Tool-selection policy table**: track a simple score per (environment-type, tool) pair across runs, and bias the agent's tool choice toward historically successful pairings. More structured, closer to a real learning signal, good "harder problem" angle for judges.

Recommend starting with (2) for day 1–3, layering in (3) once multiple environments exist (days 4–5) so the agent can show *generalization* (does a strategy learned on environment A transfer to environment B?), which is a stronger story than just "faster on the same environment."

## Sandboxing (non-negotiable, build this before anything else)
- Target environments run in isolated containers with **no outbound network access** except what's explicitly required for the tool to function.
- Agent's tool-invocation layer should be an allowlist — it can only call the specific pre-approved tools in its toolbelt, not arbitrary shell commands.
- Separate the orchestrator's credentials/access from the sandboxed environment entirely — the agent should never have a path out of the sandbox.
- Log everything the agent does, not just final outcomes — needed both for the memory/strategy-notes step and for showing judges exactly what happened.

## 7-Day Plan
- **Day 1 (today):** one environment (Vulhub container), toolbelt of 1–3 existing public tools/PoCs for its known vuln, orchestrator + scorer running, one logged run. Submit for day-1 prize.
- **Days 2–3:** harden sandbox isolation, add 2–4 more environments, finalize scoring schema.
- **Days 4–5:** build strategy-notes memory layer, run repeated attempts, produce the run 1 vs run N improvement chart.
- **Days 6–7:** polish, EDGE_CASES.md (if pursuing Shelled), README, demo script, gather required outside-tester feedback.

## Today's concrete task
1. Stand up one Vulhub (or similar) container with a known, documented vulnerability.
2. Give the agent a toolbelt containing 1–3 existing public tools/scripts for that specific CVE — no custom exploit writing.
3. Build the orchestrator loop: agent picks a tool, invokes it, result is logged.
4. Score the run (success/fail + steps + time + tokens).
5. Submit — this is "run 1," the baseline for the self-improvement work later in the week.

## Open questions / next steps
- Finalize the toolbelt's initial tool set for day 1 (which public PoC/tool for which CVE).
- Decide memory representation format (plain text notes vs. structured JSON) for the strategy-notes layer.
- Confirm sandbox hosting (local Docker vs. a cloud sandbox provider) and lock down egress rules before day 1 run.
