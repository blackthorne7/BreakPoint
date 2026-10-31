# BreakPoint

BreakPoint is a self-improving security benchmark for repeatable experiments in intentionally vulnerable lab environments. The agent selects from a fixed, approved toolbelt; each run records the choices, outcomes, and scoring metrics so later runs can be compared.

## Public demo

The static demo page is in `index.html` and `styles.css`. Its linked baseline record reports a measured, fixed Nmap scanner run; it is clearly labeled as a scanner baseline rather than an autonomous-agent run. The page is read-only and does not expose a target or launch scans.

## Local preview

Serve the page with any static web server, for example:

```sh
python3 -m http.server 8080
```

Then open `http://localhost:8080`.

## First isolated lab

The first target is documented in [lab/README.md](lab/README.md). It binds only to host loopback and uses an internal-only Docker network. The target is never deployed with the public demo.

## Run records

Initialize the local append-only SQLite store with `python3 run_store.py init`. Completed run records can be appended from JSON with `python3 run_store.py record path/to/run.json`; see [docs/run-record.md](docs/run-record.md) for the record format. Local database files are ignored by Git.

## Unikraft deployment

The `Dockerfile` packages the page in NGINX, configured to listen on port 8080. Build and deploy it with the Unikraft CLI:

```sh
unikraft build . --output index.unikraft.io/<your-org>/breakpoint:latest
unikraft run --metro sfo --name breakpoint --domain breakpoint.sfo.unikraft.app \
  -m 256M -p 443:8080/http+tls -p 80:443/http+redirect \
  --image index.unikraft.io/<your-org>/breakpoint:latest
```

Keep API tokens out of the repository. For the original architecture, see [PLAN.md](PLAN.md). Current implementation status is in [PROGRESS.md](PROGRESS.md); the bounded local agent task and commands are in [docs/demo.md](docs/demo.md).
