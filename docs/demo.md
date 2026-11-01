# Local agent demo task

This is a bounded illustration of the tool-selection and memory mechanism. It is not a reliable-improvement evaluation. Keep the existing deterministic Nmap scanner baseline separate from agent-run results.

## Task and success rule

Given the fixed local endpoint `http://127.0.0.1:18080/`, determine whether the Struts 2 S2-045 lab is confirmed vulnerable to CVE-2017-5638. The agent may report **confirmed vulnerable** only when the fixed Nmap check returns a positive finding and the final response cites that invocation. If there is no positive result, report **unconfirmed**; absence of a finding is not evidence that the service is safe. Trusted code validates the cited invocation and its recorded positive result.

The scanner result is the task's evidence source, not independent ground truth. This task does not require command execution, file retrieval, a shell, or exploit execution.

## Fixed tools

The intended toolbelt is deliberately small:

- `http_metadata`: fetch a small amount of HTTP response metadata from the configured loopback endpoint. It cannot follow redirects.
- `struts_s2045_check`: run the installed Nmap `http-vuln-cve2017-5638` script against the fixed loopback port. It takes no model-supplied target or shell arguments.

The model chooses a tool ID and empty argument object. Trusted code rejects unknown tools and arguments. Tool output is treated as untrusted data, not instructions. The model receives no Docker access or credentials.

## Prompt and response protocol

The system instruction tells the model to answer the task using only the supplied evidence, select only an available tool when more evidence is needed, and stop when it can give a supported conclusion. Each response must be one JSON object:

```json
{"type":"tool","tool_id":"nmap/http-vuln-cve2017-5638","arguments":{}}
```

or:

```json
{"type":"final","verdict":"confirmed_vulnerable","answer":"Confirmed vulnerable: ...","evidence_invocation_id":"..."}
```

The trusted evaluator accepts `confirmed_vulnerable` only when the model's structured verdict is `confirmed_vulnerable`, the cited invocation exists, and its result marks the target vulnerable. Otherwise the outcome is `unconfirmed` (represented as `fail` in the current SQLite schema, with the exact verdict in run metadata/result text). Preserve the raw visible answer and the evaluator verdict. Do not include hidden chain-of-thought in run transcripts.

## Initial budgets

These are ceilings; stop as soon as evidence supports a final answer:

- 3 tool invocations and 5 model requests per attempt, including invalid responses and retries.
- 120 seconds overall; each provider or tool timeout must be no longer than the remaining budget.
- 4 KiB maximum per tool observation, 512 output tokens per model response, and 1 KiB maximum strategy notes.
- One configured, inexpensive model/provider for agent decisions and note extraction. Record the actual model identifier and limits used.

The metadata tool is optional if it does not help the agent make a decision; do not force a pointless call merely to exercise a second tool.

## Memory demonstration

Use the same task, model/settings, toolbelt, and budgets for both attempts:

1. Run once without memory.
2. Extract a short structured note from that attempt's visible observations, recording the source run and invocation IDs and limitations. Do not give the extractor hidden evaluator results.
3. Run a second time with the exact note supplied. Memory cannot alter permissions, target, or budgets.

Show outcome, tool calls, elapsed time, available token usage/cost, and whether memory was used. Label the result “illustrative demo; two attempts; not evidence of reliable improvement.” If the first attempt already uses the best tool, state that the mechanism was exercised without claiming the second run improved. Preserve failed attempts and provider errors.

## Provider configuration

The current configuration uses the TrueFoundry AI Gateway. Its OpenAI-compatible client uses the gateway base URL and a namespaced model ID; the runner posts to the corresponding `/chat/completions` route. It reads only `TRUEFOUNDRY_GPT_LUNA_TOKEN` from `.env` (without executing the file or printing the value), or uses `BREAKPOINT_MODEL_API_KEY` if explicitly set. Do not print credentials.

```sh
export BREAKPOINT_MODEL_BASE_URL='https://gateway.truefoundry.ai'
export BREAKPOINT_MODEL='tfy-managed/gpt-6-luna'
python3 agent_demo.py run
python3 agent_demo.py extract-notes RUN_ID --output data/notes/RUN_ID.json
python3 agent_demo.py run --memory data/notes/RUN_ID.json
python3 run_store.py list
python3 compare_runs.py RUN_1_ID RUN_2_ID --notes data/notes/RUN_1_ID.json
```

The endpoint and model shown match the current local configuration; environment variables can override them. `BREAKPOINT_MODEL_ENDPOINT` can override the full chat-completions URL. The runner does not execute or generally load `.env`; it reads only the named token. Do not put credentials into prompts or event logs. If the token or model access is unavailable, report that no live agent runs were made. Do not fabricate provider results.

### Offline fake-model checks

The runner has deterministic local scenarios that make no provider requests. The budget case requires no lab; the fixed-tool case runs the Nmap check and therefore requires the manually started local lab:

```sh
python3 agent_demo.py run --fake-model --fake-scenario budget_exhaustion
python3 agent_demo.py run --fake-model --fake-scenario unknown_tool
python3 agent_demo.py run --fake-model --fake-scenario unexpected_arguments
python3 agent_demo.py run --fake-model
```

Fake-model records are implementation checks only. They must not be presented as model-agent runs or evidence of improvement.
