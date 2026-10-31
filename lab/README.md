# Local Struts 2 S2-045 lab

This lab uses Vulhub's published Struts 2.3.30 environment for CVE-2017-5638, pinned to image digest `sha256:b992e080d8e5ad332bf526ae26124d28f56ca4fc9e0eaa91510dbee9870eb2c8`. It is for local, controlled testing only. The target is reachable from the host at `http://127.0.0.1:18080`; the Compose network is internal, so the target has no outbound route. The public BreakPoint demo does not connect to this lab.

Vulhub's environment and version reference: [struts2/s2-045](https://github.com/vulhub/vulhub/tree/master/struts2/s2-045).

## Start

From the repository root:

```sh
docker compose -f lab/compose.yaml up -d
```

Check the target locally:

```sh
curl --fail --silent --show-error http://127.0.0.1:18080/
```

Record the pulled image digest for the run environment metadata:

```sh
docker image inspect vulhub/struts2:2.3.30 --format '{{index .RepoDigests 0}}'
```

## Stop and remove

```sh
docker compose -f lab/compose.yaml down
```

The lab intentionally publishes no host port except loopback and uses an internal-only Docker network. Do not add a public listener or connect this target to the Unikraft demo service.
