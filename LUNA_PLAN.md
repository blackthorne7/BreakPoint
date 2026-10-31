# Implementation plan for Luna

## Objective and priorities

Build a fast, cheap proof of concept: an agent completes a bounded task in the existing Struts lab, records what happened, extracts strategy notes, and uses those notes on its next attempt.

This is an illustrative demo of the mechanism. It does not need to prove reliable improvement yet. Optimize for short runs, few model calls, small prompts, and reuse of existing code. Save proper repeated evaluation until the end of the week, after the rest of the demo is complete.

Read `PROGRESS.md` for current state and `PLAN.md` for original context. Follow this document for the immediate implementation sequence. The existing Nmap baseline remains a scanner reference; it is not an agent run.

Keep SQLite, the local lab, and the static demo. Avoid frameworks, additional environments, policy tables, elaborate migrations, and general-purpose orchestration. Do not deploy as part of this implementation task. Update `PROGRESS.md` with actual results and the next unfinished task.

## Phase A: cheap working demo — do this now

### 1. Define a tiny task and budget

Write a short `docs/demo.md`, not a research protocol. Use vulnerability detection on the fixed local endpoint as the task. Keep the existing published Nmap check as the evidence source; shell access, exploit execution, and file retrieval are unnecessary.

Specify the initial prompt, tool descriptions, success rule, and limits. Start with at most two useful tools: an HTTP metadata fetch and the existing vulnerability check. A one-tool integration smoke check is fine before adding the second tool. Do not add misleading choices or forced mistakes to make memory look helpful.

Use a structured final answer referencing the invocation that supports it. Success requires a positive tool result plus a supported agent conclusion, checked in trusted code. A missing positive result means unconfirmed, not safe. Treat the scanner result as evidence, not an independent ground-truth measurement.

Start with these configurable limits:

- At most three tool invocations and five model requests per attempt, including retries and invalid decisions.
- At most 120 seconds overall, with tool/provider timeouts bounded by the remaining time.
- Small tool observations, initially about 4 KB each; short model responses, initially about 512 output tokens per request; strategy notes capped at about 1 KB.
- One configured inexpensive model/provider for both the loop and note extraction. Use an already available suitable model; do not build a model-selection system. Record its identifier and configured limits.

These are ceilings, not targets. Stop as soon as sufficient evidence supports a final answer. Tune limits during development if necessary and record what the demo actually used. Avoid paid retries that add no information.

Acceptance: the task and stopping rule are clear, and one attempt has a small, bounded number of paid calls.

### 2. Implement the fixed tool interface

Reuse the baseline runner where practical and keep it independently usable. Implement small wrappers, not a general plugin framework.

- Trusted configuration fixes host, port, executable, and scanner script. The model selects a tool ID, not arbitrary targets or shell arguments.
- Reject unknown tools and unexpected arguments. Use subprocess argument arrays, never a shell.
- Enforce timeouts and bounded output capture. Disable HTTP redirects for the metadata tool.
- Keep credentials and Docker access outside model-visible context. Treat retrieved content as untrusted data, not instructions.
- Keep the vulnerable lab local and separate from the public demo.

Acceptance: focused offline checks confirm unknown tools/arguments are rejected before execution and timeouts/output limits are enforced. These boundaries remain required for the demo.

### 3. Connect the smallest agent loop and basic records

Use one provider integration, configured through environment variables. Do not print secrets. Build the loop: request a decision, validate it, run an approved tool, return the observation, and stop on a supported final answer or a budget/error.

Use the existing run-store format for completed attempts. Record the model, prompt/configuration, tool decisions and results, memory supplied, final answer, trusted verdict, termination reason, elapsed time, and available token usage. Leave unavailable usage or cost null. Keep scanner and agent run kinds distinguishable in configuration/metadata.

For crash visibility, append a simple local JSONL event log as events occur, including run start and finish. An unfinished log is sufficient to identify an interrupted attempt for now. Defer database lifecycle redesign, automatic recovery, and elaborate provenance. Never silently drop a failure.

Start the lab manually using the existing instructions and check readiness before running. For these non-destructive checks, reuse the running lab between demo attempts. Note that this is not a controlled reset protocol. Automatic container lifecycle management is deferred.

Acceptance: a fake-model check exercises tool dispatch, final-answer validation, and budget exhaustion without paid API calls. One real attempt produces a readable trace and a stored outcome. Failures and provider errors stop cleanly and remain inspectable. Do not run a large test matrix or repeated live attempts just to validate routine edits.

### 4. Demonstrate memory with two agent attempts

Run the following sequence once the offline checks pass:

1. Run one agent attempt without memory.
2. Use one short extraction request to turn its visible observations into compact structured notes: observation, recommended action, source run/invocation IDs, and limitations. Validate the note format and size. Do not inject hidden scorer answers.
3. Run one more attempt with those notes, keeping the task, model, toolbelt, and budgets the same.

Store the exact notes and source run ID. Notes cannot change tool permissions, targets, or budgets. Include extraction usage/cost in the demo totals when available.

Budget for two agent attempts and one extraction request initially. If a live integration failure requires another attempt, fix the specific issue first and retain the failed record. Do not run a sweep, hunt for a favorable pair, or collect repeated cohorts now.

Acceptance: the second attempt demonstrably receives notes from the first. It need not outperform the first. If the first attempt already chooses the best action, say so and show that the mechanism still works.

### 5. Make the demo understandable and stop

Produce a small local comparison table from the two stored runs: outcome, tool calls, elapsed time, available token usage/cost, and memory used. A chart is optional; a clear table and short trace are enough.

Update the local static demo and documentation with a limited export if useful. Keep detailed transcripts local by default and exclude secrets from public artifacts. Label the comparison “illustrative demo; two attempts; not evidence of reliable improvement.” Keep the deterministic scanner reference separate.

Document exact commands to run without memory, extract notes, and run with a specified notes file. Update `PROGRESS.md` with files changed, checks actually run, real run IDs/results, limitations, and deferred work. Deployment remains a separate task.

Phase A is complete when an agent acts within the fixed tool interface, records its outcome, and uses extracted notes on a second attempt, with an honest local presentation. Do not make rigorous evaluation a prerequisite for finishing or showing the demo.

If provider access is missing, finish the offline loop, dispatcher, recording, and commands, then identify the missing configuration. Do not fabricate live results.

## Phase B: proper evaluation — end of week, after the demo is complete

This phase is deferred. Do not automatically start spending on it after Phase A; include it as the next decision in the handoff. Choose the run count and spend budget when the rest of the project is ready.

Before interpreting improvement:

1. Freeze a versioned task, prompt, model/settings, toolbelt, evaluator, and budgets. Record code revision, runtime image/tool identities, exact memory snapshot and its provenance. Add a documented reset/readiness procedure for every attempt.
2. Separate exploratory development, memory training, and evaluation. Extract notes from training runs only and freeze them before evaluation.
3. Compare repeated attempts without memory against repeated attempts using the frozen notes, with randomized execution order and otherwise consistent settings. Set cohort sizes and retry rules before collecting results; a small pilot may start with five per condition if the agreed budget permits.
4. Preserve all attempts. Report failures and infrastructure errors explicitly, success counts/rates, calls to success, total calls, timings, and available usage/cost, including extraction overhead. Avoid presenting successful-only timings as overall performance.
5. Produce a machine-readable comparison linked to full run IDs. Small samples support descriptive observations, not strong statistical claims. Repeating one environment does not demonstrate generalization.

Add stronger crash recovery, schema changes, broader tests, and reproducibility machinery only where needed for this phase. If the simple task has no room for improvement, report that result and define a separate follow-up task with a meaningful decision challenge. Do not retrospectively tune the task until a favorable chart appears.

Additional environments, held-out transfer evaluation, and sponsor deployment can be considered after the local demo and evaluation design are ready.
