# Offline-only self-check and handoff

## Result

After the candidate and independent model edits, this command was executed:

```text
python -B Audit/phase16-p3-lease-next-2026-11-03f/test_witness_model.py -v
Ran 19 tests in 0.002s
OK
```

The independent Python model exercises a same-instance read-only sentinel,
new equal-looking lease, values and environment replacement, missing/wrong
holders/registry, wrong-but-same-length nonce and other literals, context/dirty/
units drift, historical key presence, hash refusal, modeled provisional state,
and delegate exception or post-delegate substitution. It also deliberately
demonstrates that a coherent rewrite of **both** holders and the registry can
evade the model. Separate textual checks inspect the candidate templates' stops,
guard/hash/`fileIn` order and arm-return retention. This is **not** MAXScript
execution, MAXScript syntax validation, a time bound, live continuity proof,
production runtime test, replay proof or P3.1 acceptance.

## Preserved intermediate failure

The first model execution had **17 tests / one failure** in
`test_fresh_equal_values_and_environment_arrays`: the test incorrectly demanded
that a deliberately injected array replacement had not happened. The guard had
refused correctly; the test assertion itself was inconsistent with its fault
injection. The helper was corrected to snapshot the already-injected exact
state and assert that the guard neither changed nor restored it. Later runs
grew to 19 methods and produced the result above. This failure is recorded, not
silently reclassified as an earlier pass.

## Main's next decision

Read `README.md`: the templates are intentionally disabled and invalid until
independently reviewed and adapted. The historical Main03 key remains
untouched; the last recorded live observation was absence in a later process,
not a current continuity claim. The new protocol admits **no wall replay** and
is subject to all other runtime review blockers. Only main may run live probes;
cross-call persistence, exact struct/array/string behavior and the actual guard
must be calibrated on disposable scratch fixtures first. Unknown/timeout means
INCOMPLETE, no automatic recovery. The historical Main03 arm's exception-removal
path is incompatible with this proposal's strict retain-on-ambiguity policy.

This author made no Max call, scene write, git operation, installation, or
intentional file changes outside this new directory. The underlying runtime may
be concurrently changing under other ownership; no stable-source test or hash
claim is made here.
