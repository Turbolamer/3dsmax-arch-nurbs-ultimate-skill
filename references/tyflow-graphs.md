# tyFlow Graphs

> **OBSOLETE.** tyFlow is **not installed** in this Max. Confirmed by direct reading of the live
> tool list, not inferred: **all 14 `3dsmax-mcp_tyflow_*` tools fail unconditionally** —
> `create_tyflow`, `create_tyflow_preset`, `add_tyflow_event`, `add_tyflow_collision`,
> `connect_tyflow_events`, `modify_tyflow_operator`, `remove_tyflow_element`, `get_tyflow_info`,
> `get_tyflow_particles`, `get_tyflow_particle_count`, `reset_tyflow_simulation`,
> `set_tyflow_physx`, `set_tyflow_shape`, `list_tyflow_operator_types`. **Kept for reference only**;
> nothing below the divider is executable.
>
> **Read this instead: [`14-chaos-scatter.md`](14-chaos-scatter.md) §4** — the absent-plugin routing
> table naming all 14 tools and the substitutions that *are* verified here — and
> [`02-mcp-live-orchestration.md`](02-mcp-live-orchestration.md) for the live tool inventory.
> **There is no tyFlow equivalent in this build.** The agentic loop below cannot be started: its
> first step is `get_tyflow_graph`, which does not exist.

## Why OBSOLETE rather than rewritten

Considered and rejected on evidence, not convenience:

1. **Every step depends on the absent plugin.** The loop is built on `get_tyflow_graph`,
   `tyflow_apply_patch`, `expected_hash` / `graph_hash`, the AppData ledger and
   `harvest_tyflow_manifest` / `list_tyflow_operators` — none of which resolve.
2. **The subject is covered, and covered better, elsewhere.** Distribution of many copies over a
   surface is **Chaos Scatter**, documented with a measured parameter map in
   [`14-chaos-scatter.md`](14-chaos-scatter.md). Motion and physics have their own verified routes.
3. **The measured physics numbers are unusable as written.** The "Physics gotchas" section is
   labelled *live-verified, tyFlow 2.05 / Max 2027* — a version pair this build does not have. They
   describe operator behaviour of an absent plugin, not a fact about this Max.

## Routing table — what replaces each tyFlow capability here

| tyFlow capability | Verified route in this build |
|---|---|
| Static distribution of instances over a surface | `ChaosScatter` via `3dsmax-mcp_execute_maxscript` — `targetNodes` / `modelNodes` / `modelFrequencies` / `seed` / `instanceCountLimit`. `ChaosScatter()` constructs; `CScatter` is **NotCreatable**. `seed` is an integer 1…31337 and is **data** |
| Density patterning (`surfaceRandomUseDensity`, `distributionDesityPattern` — the typo is in Max) | `ChaosScatter`, same call (`14-chaos-scatter.md` §2, §4) |
| Physics / collision response | **PhysX or Max particles** — not tyFlow |
| Animated motion of many elements | Keyframed MAXScript transforms plus `3dsmax-mcp_assign_controller` / `add_controller_target` / `set_controller_props` |
| Named shapes for emitters (`set_tyflow_shape`) | Native MAXScript primitives and `references/maxscript-3dsmax-objects.md` |
| Graph read-back (`get_tyflow_graph`, events/operators/wiring) | Nothing equivalent — no event-graph API is reachable from this bridge. `3dsmax-mcp_execute_maxscript` plus `capture_viewport` |
| `create_tyflow_preset` (rain, snow, fountain, burst, debris) | **Nothing equivalent.** Substitute Chaos Scatter for distribution, PhysX / Max particles for the rest |
| Operator manifest / property names | Read them from the live object — `introspection tools lie`; `execute_maxscript` and a known-bogus control in the same batch is the only trustworthy existence test |

---

*Everything below this line is the original file, retained for reference only, exactly as it was
written. **Do not execute it. Do not cite it. Do not copy from it.** Every workflow in it calls a
tool that is not in the connected bridge, against a plugin that is not installed.*

---

# tyFlow Graphs

Read this reference completely before building, inspecting, editing, or verifying tyFlow event graphs.

## Closed-graph reality

- tyFlow's event graph is private: events, operators, and wiring are invisible to `refs.dependsOn`, `refs.dependents`, sub-anim enumeration (`numsubs` is 0), `getClassInstances`, and PB2 params — at MAXScript and SDK level alike. Only dynamic name lookups (`bo[#'EventName']`) and `showProperties` parsing work.
- Wiring WRITES use the documented `op.connect eventHandle` / `op.disconnect()`; wiring READS are impossible — the MCP layer records every connect/disconnect in a JSON ledger stored as AppData on the flow node (travels with the scene file).
- Operator type identity is only the display name at creation time; renames erase it. The ledger's `operator_types` map (recorded at creation through MCP tools) is the durable type record.

## The agentic loop

- Read with `get_tyflow_graph` — events (name/position/width/enabled), operators, optional properties, ledger `edges`, `operator_types`, `graph_hash`, and `ledger_status`.
- `ledger_status`: `fresh` (live structure matches the last MCP mutation), `stale` (flow edited outside MCP — edges may be outdated), `absent` (no MCP ledger yet).
- Edit transactionally with `tyflow_apply_patch`, passing `expected_hash` from the last `get_tyflow_graph`; a hash conflict means the user edited the flow — re-read before retrying.
- Patch ops: `add_event`, `remove_event`, `add_operator`, `remove_operator`, `set_properties`, `connect`, `disconnect`, `rename_event`, `rename_operator`, `set_event_position`, `set_enabled`. Always pass explicit operator `name`s in `add_operator` — ledger keys are `"Event/OpName"`.
- Verify empirically: `verify_frames` + `min_particles`/`max_particles` resets the sim and asserts counts; there is no compile step, so structural success does not imply behavioral success.
- On failure, additive-only patches (add_event/add_operator/connect/set_event_position) roll back via synthesized inverse operations (`rollback_mode: inverse`) — no node clone involved. Patches containing other ops use a checkpoint clone (`rollback_mode: checkpoint`); that node swap breaks references other scene objects hold to the flow (e.g. tyMesher) — use `checkpoint=false` when such references exist.
- Prefer additive patches plus a follow-up destructive patch over mixed batches: additive batches avoid clone churn entirely, which matters for tyFlow stability.
- Single edges outside a patch: `connect_tyflow_events` (Send Out convenience) or `connect_tyflow_operator` / `disconnect_tyflow_operator` (any test operator). Re-connecting re-targets: the ledger edge for that (event, operator) is replaced.

## Operator manifest

- `harvest_tyflow_manifest` probes every known operator type in a scratch flow and caches per tyFlow version; run once per installation (or `refresh=true` after a tyFlow update). `list_tyflow_operators` queries the cache with no Max traffic.
- Use manifest property names verbatim — tyFlow PB2 names are non-obvious (`shape_type_tab`, `type_3d_ID_tab`, `frequency_tab`). Never guess.
- `Script` and `MAXScript` operators are executable code: `tyflow_apply_patch` fails closed unless MCP safe mode is disabled AND `allow_executable=true`. Creating them empty via harvest probing is inert and allowed.

## Per-event census

- No API reports which event a particle is in. `tyflow_event_census` instruments each event with a temporary `Mapping` operator (ordinal stamped into UVW channel 99 by default), resets, evaluates probe frames, buckets per-particle reads, then removes the instrumentation. It mutates the flow during the call — opt-in diagnostic, not a free read.
- `method="groups"` (export-group bits) is limited to 16 events and misreports particles that accumulated bits across multiple events; prefer the default mapping method.
- The response's `instrumentation` block names the properties actually resolved on the Mapping operator — check it before trusting zeros.

## Foreign flows (not built through MCP)

- Structure (events/operators/properties) reads fine; edges are unknown (`ledger_status: absent`).
- `capture_tyflow_editor` (requires `enabled=true`) opens the tyFlow editor, captures the screen, and returns per-event rectangles (`position`/`width`) — read the wires visually from the image, then record them with `set_tyflow_wiring_ledger` (mode `replace` or `merge`; unknown event names are warned, edges keyed by from-event + from-operator).
- After reconciliation the ledger is fresh by definition; subsequent MCP edits keep it current.

## Physics gotchas (live-verified, tyFlow 2.05 / Max 2027)

- Speed `directionMode` 0/1 ("Along Icon Arrow" / "Icon Center Out") produce a ZERO vector on a default flow icon — the operator silently contributes nothing (and divergence spreads nothing). Use mode 8 ("Custom vector direction", defaults up) for directional jets; the operator default is 3 ("Random 3D").
- Force `gravityStrength` is signed with POSITIVE pushing +Z (up). Downward gravity needs a negative value. Working fountain reference: Speed magnitude 25 (±6) with gravityStrength -2.6 gives ~1m arcs and ~18-frame flight.
- Birth emits at the flow icon's world position; moving the flow NODE did not relocate births in testing. Never place a collider surface at the birth plane — particles born touching a collider are captured instantly (jet velocity killed the same frame), which mimics "operators have no effect".
- Diagnose sims with data, not guesses: `getParticlePosition`/`getParticleVelocity` on the newest particle (index = numParticles) exposes launch state; identical census counts across setting changes means the settings are not reaching the behavior you think they are.
- `flow.baseobject.cacheEnable = false` plus `reset_simulation()` is a safe diagnostic step to rule out stale caching during iteration.

## Runtime rules

- tyFlow's dispatch exposes spaced names underscored: an operator displayed "Send Out" reads back as `Send_Out`, and graph reads / ledger keys use that underscore form canonically. Tools accept either form in lookups; expect underscores in responses.
- Event/operator lookups are name-based: duplicate operator names within an event make ledger keys and patch targets ambiguous — keep names unique.
- Probe gently: never loop create→simulate→delete of tyFlow objects inside a single MAXScript program — tyFlow's Qt cleanup can deadlock Max (live-confirmed). Reuse one scratch flow, mutate in place, pump messages (`windows.processPostedMessages()`) between sim iterations, delete once at the end.
- `add_operator` position is 0-based; `-1` appends.
- Census and patch verification call `reset_simulation` — cached sim state is discarded. Never fire renders from these tools.
- Probe/scratch objects are named `zzz_mcp_*` and are cleaned up by the tools; if a crash leaves one behind, delete it manually.
- The ledger lives in AppData channel 1415075927 on the flow node; `manage_scene(hold)` before risky sessions still protects everything, and clones of the flow carry the ledger with them.
