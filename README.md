# Egregore

An agent you can copy onto a machine.

One file — an Actually Portable Executable built with cosmocc — carrying the harness, its
configuration and its tools. Drop it on a box with a goal and it works toward that goal
unattended. It assumes no runtime, no package manager, no root and no shell; it can copy itself
onward, and the copies coordinate through a hub.

What that adds up to is a population: many agents, on many machines, all working toward one
main goal. The goal decomposes into subgoals, each copy is issued one, and the hub keeps the
account — which subgoal is claimed by whom, what came back, and what is still open. A copy that
finds the work larger than itself issues the subgoals it cannot reach and places another copy.

## Design

- **One file.** cosmocc, so the same binary runs on amd64 and aarch64 across Linux, macOS, the
  BSDs and Windows. Config and tools live inside it as a zip payload; nothing is installed and
  nothing is left behind.
- **TLS is the only network dependency.** An embedded mbedTLS client, a CA bundle in the payload,
  and an egress ladder that probes for a route before the first request — DNS or a pinned address,
  a direct route or a proxy, and a diagnosis written down when none of them work.
- **Hub and spoke, not a peer mesh.** Copies can each reach the hub and usually cannot reach each
  other, so coordination goes through one endpoint: subgoals claimed, results posted, work deduped.
  The population is only ever as coordinated as that account is.
- **Budgets are code, not prompt.** Token, cost and wall-clock caps enforced in the loop, with a
  distinct `budget_exhausted` outcome — an unattended copy stops on purpose and says why.
- **Every run carries a task id**, so a result is attributable to the task that was issued, without
  anything having to parse a prompt.
- **Tools are built into the binary**, not shipped beside it: no shell-quoting surface, no
  subprocess per capability, and nothing to extract.

## Status

Design, plus the pieces landing upstream in [hax](https://github.com/jmars/hax): the `--json`
record stream, per-run task id, and enforced budgets.
