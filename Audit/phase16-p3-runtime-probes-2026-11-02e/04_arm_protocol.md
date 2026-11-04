# Exact main-only arm protocol

Generate an arm file with the same validated runtime module and exact args:

```python
arm = generate_arm_script(plan, identity, namespace, expected_units,
                          nonce="MainSuppliedFreshNonce20261102e")
```

The nonce example is not a reusable lease; main supplies a genuinely fresh token.
Write only under a private new run/probe directory. Arm code itself refuses any
existing registry symbol; it never removes or replaces a prior lease. No scene
writes are performed. `fileIn armPath` **returns the exact lease array**.

Main's outer local `fileIn` harness retains that exact struct result (its detached
ten-item payload is `.values`; struct identity was operationally calibrated):

```maxscript
local witness = fileIn armPath
-- Read exact registry symbol from emitted source, do not infer ownership by name.
if (globalVars.get registryKey) != witness do throw "lost external witness"
fileIn wallPath
-- Before EACH subsequent wall fileIn, compare this same witness again.
if (globalVars.get registryKey) != witness do throw "lost external witness"
fileIn wallPath
```

No wall-script branch auto-arms an absent registry. Lease states are ARMED ->
BUILDING -> COMMITTED or POISONED. Only an explicit fresh arm authorizes first
creation; failure poisons the spent lease and future fileIn refuses. Registry
loss, different identity, bad shape/type or changed witness refuses. Main must
not carry the witness through reset/new/open/load/merge/restart, and performs
no scene operation between these sequential main-thread calls except the
explicitly scoped negative-control edit. File emission/arming does not prove
runtime baseline support or broad edit safety.
