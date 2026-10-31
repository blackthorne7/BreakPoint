# BreakPoint

BreakPoint is a self-improving security benchmark for repeatable experiments in intentionally vulnerable lab environments. The agent selects from a fixed, approved toolbelt; each run records the choices, outcomes, and scoring metrics so later runs can be compared.

## Public demo

The static demo page is in `index.html` and `styles.css`. Its baseline card is explicitly marked as a fixture: it does not claim that a measured lab run has happened yet. The page is read-only and does not expose a target or launch scans.

## Local preview

Serve the page with any static web server, for example:

```sh
python3 -m http.server 8080
```

Then open `http://localhost:8080`.

## Unikraft deployment

The `Dockerfile` packages the page in NGINX, configured to listen on port 8080. Build and deploy it with the Unikraft CLI:

```sh
unikraft build ./Dockerfile --arch x86_64 --output <your-org>/breakpoint:latest
unikraft run --metro sfo --name breakpoint --domain breakpoint.sfo.unikraft.app \
  -p 443:8080/http+tls -p 80:443/http+redirect --image <your-org>/breakpoint:latest
```

Keep API tokens out of the repository. For the run comparison and agent architecture, see [PLAN.md](PLAN.md).
