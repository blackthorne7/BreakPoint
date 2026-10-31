# Local Struts 2 S2-045 lab

This lab uses Vulhub's published Struts 2.3.30 environment for CVE-2017-5638, pinned to image digest `sha256:b992e080d8e5ad332bf526ae26124d28f56ca4fc9e0eaa91510dbee9870eb2c8`. It is for local, controlled testing only. The target is reachable from the host at `http://127.0.0.1:18080` through a small Nginx proxy. The vulnerable target stays on an internal-only Compose network and has no outbound route; only the proxy is connected to the host-facing bridge. The public BreakPoint demo does not connect to this lab.

Vulhub's environment and version reference: [struts2/s2-045](https://github.com/vulhub/vulhub/tree/master/struts2/s2-045).

## Start

From the repository root:

```sh
systemctl --user enable --now docker.socket
export DOCKER_HOST="unix://${XDG_RUNTIME_DIR}/docker.sock"
docker compose -f lab/compose.yaml up -d
```

Check the target locally:

```sh
curl --fail --silent --show-error http://127.0.0.1:18080/
```

The proxy publishes only on host loopback. Keeping it on the host-facing bridge avoids a Docker Engine 29 port-publishing issue with containers attached only to internal networks, while leaving the vulnerable target isolated.

## Fixed baseline check

The baseline uses the installed Nmap `http-vuln-cve2017-5638` NSE script, which checks for the vulnerability by asking Struts to add a response header. It does not run a command or read a file. The runner fixes the target to `127.0.0.1:18080`, records the installed Nmap version and script hash, and appends the output to the local SQLite run store:

```sh
python3 lab/run_baseline.py
python3 run_store.py list
```

This is a deterministic scanner baseline, not an LLM-agent run. Token counts are recorded as unavailable.

Record the pulled image digest for the run environment metadata:

```sh
docker image inspect vulhub/struts2:2.3.30 --format '{{index .RepoDigests 0}}'
```

## Stop and remove

```sh
docker compose -f lab/compose.yaml down
```

The lab intentionally publishes no host port except loopback. Do not add a public listener or connect the target to the Unikraft demo service.
