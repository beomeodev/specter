---
name: ms-ops-debugging
description: Symptom-indexed playbook for deployment/environment debugging — SSH tunnels, reverse proxies, TLS, container lifecycle, secret rotation, and real-time API integration failures that "work locally, break deployed." Every entry traces to a real diagnosed incident (probe -> resolution), stated at the failure-class level so it generalizes across projects. Use when a deploy-only symptom, a "works here but not there" report, or an environment-boundary failure needs the fastest-discriminating probe, not generic debugging methodology (that lives in /ms.fix's Hard-Bug Discipline).
---

# Ops & Deployment Debugging

## What it does

Generic debugging methodology (repro-minimise, hypothesis discipline, instrumentation) lives
in `/ms.fix`'s Hard-Bug Discipline. This skill owns a narrower, evidence-based slice: failures that only manifest
at an environment boundary — a deploy, a tunnel, a proxy, a container, a rotated secret, a
platform-native API — where the fastest path to a fix is recognizing the failure *class*, not
re-deriving it from first principles every time.

Every entry below traces to a real diagnosed incident, stated at the failure-class level with
project specifics stripped — this is not a generic textbook list. If a failure class isn't below,
fall back to `/ms.fix`'s Hard-Bug Discipline.

## When to use

- A symptom only reproduces after deploy, never locally (or vice versa).
- "It worked yesterday" / "no code changed" with a new failure.
- A network boundary is involved: SSH, tunnel, reverse proxy, TLS, DNS.
- A container won't start, is stuck `unhealthy`, or a bind-mount looks wrong.
- Auth/login breaks specifically around a secret rotation or redeploy.
- A real-time/streaming API integration (WebSocket, SSE) rejects a connection or silently stops
  producing output.

## Method (apply before reaching for a specific entry below)

- **Read the actual process-level error, not the surface signal.** An orchestrator-level warning,
  a familiar-looking symptom, or an assumption about which host a check ran on is very often
  wrong or incomplete. The literal traceback/log line from the failing process, read on the
  actual host in question, consistently cuts through it faster than reasoning from the symptom.
- **Mint a valid credential/request and hit the service directly**, bypassing the UI/browser,
  whenever a stateful auth/session bug is suspected — this bisects "backend is fine" from
  "client/transport is broken" in one step.
- **An unfiltered log tail is a required fallback** whenever a targeted grep comes up empty or
  inconsistent with the observed symptom — over-filtering can hide the one line that matters.
- **If the error changes after a fix, that's forward progress.** Multi-layered validation (proxy
  → auth → business logic → downstream API) means fixing one rejection often just exposes the
  next one — keep going rather than assuming the fix failed.

## A. Network / Tunnel Reachability

**A1. SSH tunnel routes to a stale port/host** — tunneled service unreachable or intermittently
reachable with no code change. Probe: re-derive the target from *live* state
(`docker compose ps` for the actual bound port/IP, or `hostname; hostname -I` inside the target
container) and diff against the tunnel command in use — don't trust a memorized command.
Resolution: rebuild the tunnel from live topology; if "same input, same failure" persists after a
fix, suspect a stale duplicate tunnel process (`pkill -f 'ssh -N -L'`) and restart backgrounded.
*(tunneled to a memorized port with zero references in the repo; the service had moved to `:80`.)*

**A2. Diagnostic command run on the wrong host** — a "server-side" check run on the client (or
vice versa) produces a misleading connection-refused result. Probe: state and verify which host a
check must run on *before* running it (`hostname`/`whoami` first when unsure). No code fix — a
workflow discipline.

**A3. Unnecessary SSH reach when already co-located on the same network** — defaulting to "I need
to tunnel to this" when the current shell is already on the same container network. Probe:
`docker compose ps` / `getent hosts <service-name>` from the current shell before reaching for
SSH — if the name resolves, you're already co-located and can talk to it directly.

**A4. Backgrounded process died silently between sessions** — a previously-working tunneled URL
goes dark with no new error and no completion/crash record. Probe: check liveness directly
(`curl -s -o /dev/null -w "%{http_code}" http://localhost:<port>/`) before assuming the
network/tunnel itself broke; "no completion record" is evidence the process/session was torn
down, not a regression.

## B. Reverse Proxy / TLS

**B1. Proxy route-matcher drift** — frontend calls return 200 but are actually the SPA's HTML
shell, not JSON (auth/dashboard state never updates). Probe: `curl -i <route>` on the *exact*
application route (not `/health`) — an HTML `<!doctype html>` body instead of JSON is the tell
that the proxy doesn't cover this path prefix. Resolution: fix the route matcher to cover the
paths the frontend actually calls.

**B2. Reverse proxy doesn't hot-reload a mounted config** — a routing fix is committed and pulled
onto the server but the bug persists. Probe: cross-check container start time vs. fix commit time,
and confirm via an app-side "did the request even arrive" signal (empty access log = proxy never
forwarded it). Resolution: most proxies (Caddy, nginx) read config once at start — recreate the
container (`--force-recreate`), don't just edit the mounted file.

**B3. TLS handshake failure from a hostname-less/SNI-less site block** — browser shows a TLS
error on `:443`; plaintext `:80` works and redirects cleanly. Probe: `curl -k https://<host>`
directly on the server alongside `curl -sI http://<host>` — clean `:80` + TLS alert on `:443`
means proxy TLS config, not network/tunnel. *(Caution: enabling on-demand cert issuance for
whatever SNI connects is only safe on a non-publicly-exposed listener — otherwise it's a DoS
vector and needs an explicit allowlist.)*

**B4. Browser HSTS cache masks a working plain-HTTP local service** — `curl http://localhost/...`
succeeds but the browser shows connection-refused/redirect on the identical URL. Probe: compare
curl (bypasses browser policy) vs. browser on the same URL — divergence on a plain-HTTP endpoint
means browser-side HSTS/HTTPS-first enforcement, not the server. Resolution: use `http://127.0.0.1/`
explicitly or clear the domain's HSTS cache.

**B5. Static/SPA fallback route masquerades as a backend health check** — `GET /health` (or any
path) returns 200 even with no backend listening at all. Probe: don't trust a bare 200 from a
frontend-only static server; POST to a real API route or check for a bound backend process
(`docker ps`, `ss -ltn`) — a 404 on a real route with 200 on `/health` proves the "backend" is the
SPA's catch-all.

## C. Secrets & Rotation

**C1. Fail-closed boot guard blocks startup on a secret not threaded into the container** — stuck
restart loop; an unrelated orchestrator-level warning is a red herring. Probe: read the
container's own stderr (`docker compose logs <service>`), not orchestrator warnings — the real
blocking variable is named explicitly in the app's own startup-validation exception. Resolution:
compose only passes through vars explicitly listed under `environment:` — add the missing one(s).

**C2. Post-rotation decryption failure surfaces as 500, not 401, at login** — login fails with a
server error even with correct credentials. Probe: read server logs right after the failed
attempt for a crypto-library exception (decryption/verification failure), not an auth-logic one.
Resolution: a stored secret was encrypted under a key-encryption-key that no longer matches the
currently-mounted one (rotation, env switch, stale row) — decryption is cryptographically
unrecoverable; identify and purge affected rows, re-provision fresh secrets under the current key.

**C3. Stale client-side signed cookie/token survives a secret rotation** — login appears to
succeed, then immediately bounces back to the login screen (next request 401s). Probe (highly
reusable): mint a *fresh* valid credential server-side using the current secret and hit the API
directly (curl/httpx), bypassing the browser — if that succeeds, the fault is specifically what
the browser is sending. Resolution: clear the cookie / hard reload / re-login; any secret rotation
on redeploy invalidates previously-issued signed tokens.

**C4. "Idempotent" bootstrap/seed script isn't idempotent in the values that matter** — a
demo/bootstrap script reports success but login still fails with old credentials (silently skipped
re-creating an existing row), or a registered OTP secret never matches because the script minted a
brand-new random seed every run. Probe: check container/volume age against when bootstrap last ran
— a reused volume carries forward stale state a "successful" run never touched. Resolution: make
bootstrap idempotent on the *secret material itself* (reuse if still valid under the current key;
regenerate only for genuinely new entities or explicit rotation), not idempotent on "row exists."

**C5. An env-context fail-safe silently overrides an unrelated dev-only flag** — an explicitly
enabled dev/debug bypass has no effect. Probe: grep the deploy config for the env-context marker
itself — if absent, the flag-gating logic may be structurally double-gated so an unmarked
environment always fails toward "production," making the flag irrelevant regardless of its value.

## D. Container / Orchestration Lifecycle

**D1. A Docker bind-mount source that doesn't exist yet becomes a silently-created directory** —
a service that validates an expected file (permissions, exact size) fails that validation
specifically. Probe: `ls -la <mounted-path>` — a directory where a file was expected means the
bind-mount source never existed at first `up`. Resolution: remove the wrongly-created directory,
create the real file with correct permissions. *(Caution: if the missing file was a rotated
key/secret, check whether existing data was encrypted under the old value before regenerating —
may be irreversible.)*

**D2. Healthcheck false-negative after an entrypoint refactor** — a container is permanently
`(unhealthy)` even though its actual job completes successfully. Probe: compare the entrypoint
actually executing against where the heartbeat/liveness-signal code lives — a refactor commonly
leaves the old signal-writing code in a dead path while the healthcheck definition is untouched.

**D3. Full-stack local repro needs the container runtime, which the current shell lacks** — a
one-command demo/deploy script can't run because Docker isn't available in the current
environment. Probe: `command -v docker` before attempting anything compose-based. Resolution:
locate where Docker actually runs (usually a separate host) and run/tunnel there — don't try to
fake container orchestration in a sandbox that lacks it.

## E. Auth/Session Behavior and Self-Inflicted State

**E1. A generic error code collapses multiple distinct causes into one message** — wrong
password vs. wrong OTP vs. rate-limited vs. backend-unreachable all show the same UI error. Probe:
bypass the UI, call the endpoint directly with a controlled payload, and read the raw HTTP status
code (not app-level error text) — this can reveal the failure isn't even auth-related (a 404
proves routing is broken, not credentials). Note: collapsing password/OTP into one code can be
correct-by-design (anti-enumeration) — only add discrimination for buckets that are safe to
distinguish (rate-limited vs. transport failure vs. bad credentials).

**E2. Repeated diagnostic attempts trip the app's own lockout/rate-limit** — after several failed
troubleshooting attempts, further attempts with objectively correct input keep failing identically,
masquerading as a persistent original bug. Probe: query the app's own defensive-state store
directly (lockout table, rate-limit counter) to distinguish "genuinely still locked" from "still
actually wrong." Firefighting itself can add a self-inflicted failure layer on top of the original
bug.

## F. Upstream Dependencies & Third-Party Tooling

**F1. HTTP client's default no-follow-redirect silently breaks ingestion when a vendor endpoint
moves** — a scheduled job reports a non-200 status with no code change, falling back to stale data
rather than crashing loudly. Probe: read the *unfiltered* tail of the job's logs — an
overly-narrow keyword filter can hide the exact failing request line (a `301 Moved Permanently`).
Resolution: check whether the HTTP client follows redirects by default (many don't) and enable it
explicitly; update the configured base URL.

**F2. Case-sensitive text-scraping of a third-party CLI's output breaks when casing/wording
differs from assumed** — an isolated automation step fails with a parsing/iterator exception.
Probe: read the actual raw output of the external tool — case or wording often silently differs
from what the parser assumes. Resolution: never string-match free-text CLI output; parse from a
stable machine-readable source (dedicated output file, `--json` flag, exit code) or match
case-insensitively.

## G. Real-Time / Streaming API Integration (WebSocket, SSE)

**G1. A parameter accepted through two different channels validates against different schemas
depending on which is active** — WebSocket connects then immediately closes with an "invalid
config value" error, in a retry loop; simply changing the value doesn't help. Probe: print what
the app's config loader actually resolves the value to, independent of the transport — this
discriminates "config didn't take effect" from "config took effect but is wrong," which produce an
identical error. Resolution: identify which single channel the active mode actually reads (a URL
query param vs. a session-setup message are common examples) and remove the value from the other
channel entirely, rather than just correcting it.

**G2. A stale protocol/feature-flag header survives a vendor API-version sunset** — a WebSocket
connection is immediately rejected at handshake with a 400-class error. Probe: a minimal,
standalone connect-only reproduction script decoupled from all application code (no config layer,
no reconnect wrapper) — isolates "transport/protocol itself is broken" from "something in
session/business logic is broken." Resolution: remove the stale header entirely rather than
updating its value; treat any hardcoded protocol-version header to a hosted API as a latent
breakage point independent of your own code changes.

**G3. A cross-thread shared-state race specific to free-threaded (no-GIL) runtimes** — no crash,
no test failure; only caught by an adversarial review asking "which thread mutates this, and is it
locked?" Probe: for any client running its event loop/reconnect logic on a background thread while
the main thread also touches the same state, explicitly enumerate every shared mutable field and
which thread(s) touch it under what lock — a structural question a runtime test won't surface
without real contention. Resolution: add explicit locks, invoking any callback/sink *outside* the
lock to avoid cross-lock deadlock. Code that "worked" under the classic GIL via implicit
read-modify-write atomicity can become order-dependent the moment it runs free-threaded.

**G4. Silent (no error, no output) failure in a multi-stage real-time pipeline** — several
independent stages (hardware/OS capture → transport → processing → display) could each be at
fault, and the symptom is identical regardless of which one failed. Probe (bisection by
substituting a synthetic input at a pipeline boundary): feed a static, known-good input file
through the same downstream pipeline, bypassing only the live/hardware capture stage. If expected
output now appears, the fault is upstream (capture); if not, downstream. A finer second probe:
grep the latest structured per-stage log for boundary counters — near-zero "sent" count means
capture is silently producing nothing; a large count with still no output means the
transport/processing stage never returned. This only works if the pipeline accepts a canned/offline
input mode and emits structured per-stage counters — worth building into any real-time pipeline
specifically to make this bisection possible later.

## H. Remote-Device Debugging Loop (the runtime is on a machine you can't touch)

When the product runs on the user's own device (Windows/macOS desktop, a phone, a
server you have no shell on) and evidence arrives only as pasted terminal output,
**round-trips are the only cost that matters** — each one costs minutes of the
user's attention, not yours. Discipline:

**H1. One evidence-maximizing script per round trip, never iterative one-liners.**
Each round, hand over a single copy-paste block that captures everything a whole
hypothesis set needs: environment (`OS/runtime versions`), config actually resolved,
the failing operation itself, and the full unfiltered traceback/log tail — dumped to
one file or one paste. Budget: if you're about to ask for a second command before
seeing the first's output, merge them.

**H2. Platform-native diagnostic templates.** Write PowerShell for Windows
(`$PSVersionTable; Get-Process ...; <failing command> *>&1 | Tee-Object diag.txt`)
and zsh/bash for macOS — don't hand a Linux one-liner to a PowerShell prompt and
burn a round trip on syntax errors.

**H3. Design probes to discriminate, not confirm.** Before sending, list the live
hypotheses (aim for 2–3) and make sure the script's output will *separate* them —
a probe that only confirms the favorite hypothesis wastes the trip when it's wrong.

**H4. Instructions the user can run blind.** Numbered steps, exact commands, no
"adjust the path as needed". Expect the raw output pasted back; you parse everything
— never ask the user to interpret or summarize what they see.

## Source-version note

Some source transcripts predate current SPECTER command/workflow versions. That's irrelevant here
— only the product/environment debugging content (symptom → probe → resolution) was mined, never
workflow mechanics, which may be stale and is out of this skill's scope regardless.

## Works well with

- `/ms.fix`: ops incidents (deploy/environment issues, no new requirement) usually arrive as
  fixes; its Hard-Bug Discipline covers the generic methodology this skill doesn't duplicate.
- For environment/deployment-class errors, use this skill's symptom index instead of generic
  code-error categories.
