# 11 — Layer and Naming Standard

> **Purpose:** what each layer in the closed vocabulary is *for*, what must never go on it, how a
> massing `kind` resolves to a layer, what a node may be called in the 3ds Max scene, and what a
> delivery must satisfy. This file is consumed by `scripts/build_spec.py`, which records a layer per
> element as **data**.
>
> **CORRECTED (verified 2026-10-06):** this purpose line previously read *"…, by `assembly.json.layer_map`
> at **P6**, and by the **QA loop at P8**"* — two claims that no longer hold. **No stage applies a layer.**
> `node.layer` is read-only from MAXScript, **nine** assignment routes are ruled out, and `manage_layers`'s
> whole vocabulary is `{list, create, delete}` — so P6 carries `layer_map` as a *record of intent* that no
> builder acts on (`G-79` makes an attempt a build **FAIL**). And **P8 was cancelled by user decision on
> 2026-10-05**: there is no QA loop and no `qa.json`. **The user applies layers in the Layer dialog.**
> See `references/07-spec-grammar.md` §8.1.3 / §8.5.6 and `agents/max-assembly.md` §6.3.
>
> **Authority split.** `references/07-spec-grammar.md` **§8.1.4 owns the layer names** and §8.1.2 owns
> the `kind` → layer mapping. **This file owns their meaning, their prohibitions and the naming
> rules.** It introduces no name of its own. A new layer requires changing `07` §8.1.4 first; a change
> made only here is a defect, not an extension.
>
> **How to use it.** As a checklist. §6 is the delivery gate. Anything in this file not traceable to
> `CHECKPOINT.md` is labelled **UNVERIFIED**.

---

## 1. The vocabulary — eight names, in order

`07` §8.1.4 states the vocabulary and calls it closed. Reproduced here in its exact order and with
nothing added.

> **⚠️ Count discrepancy, unresolved and owned by `07`.** The §8.1.4 prose says *"Nine names"*; the
> table beneath it lists **eight**. The list is authoritative and it has **eight** rows. No ninth name
> has been invented here to reconcile the sentence, and none may be. Recorded as open item O-1.

| # | Layer | Kind(s) mapped to it by §8.1.2 | Massing payload at P3 |
|---|---|---|---|
| 1 | `00_SITE` | `plinth` | yes — plus `site_pad` ground pad, paving, kerb |
| 2 | `01_SLABS` | `slab` | yes |
| 3 | `02_STRUCTURE` | `column` | yes |
| 4 | `03_CORE` | `core_wall` | yes |
| 5 | `04_ROOF` | `roof_deck`, `parapet` | yes |
| 6 | `05_FACADE` | **none** — no `kind` maps here at P3 | none; P5/P6 content only |
| 7 | `90_SCENE` | **none** | none, except grouping dummies |
| 8 | `99_DEBUG` | **none** | none |

`90_SCENE` and `99_DEBUG` carry **no massing payload at P3** other than grouping dummies (`07` §8.1.4,
closing line). A column on `90_SCENE` is a defect even though the layer exists.

### 1.1 `00_SITE`

| | |
|---|---|
| **Holds** | ground pad, paving, kerb, plinth, steps, ramps |
| **Massing `kind`(s)** | `plinth`. `site_pad.ground_pad`, `site_pad.paving` and `site_pad.kerb` are each a Z-prism whose `layer` is always `00_SITE` (`07` §8.1.1) |
| **Never on it** | anything structural. A column, core wall, slab or roof element placed here is a defect, not a choice. Nothing belonging to the building envelope above the plinth |
| **Note** | `dimensions.json` has no kerb key, so `site_pad.kerb` is `null` unless a later stage supplies one. Absence is recorded as `null`, not as an empty profile |

### 1.2 `01_SLABS`

| | |
|---|---|
| **Holds** | floor slabs and ground slabs |
| **Massing `kind`(s)** | `slab` |
| **Never on it** | columns, core walls, roof decks. Each storey's `slab_ref` in `storeys[]` must resolve to a `slab` element on this layer |
| **Note** | the ground slab is a `slab`, not part of `site_pad` — the pad is ground, the slab is building |

### 1.3 `02_STRUCTURE`

| | |
|---|---|
| **Holds** | columns, beams, bracing |
| **Massing `kind`(s)** | `column` |
| **Never on it** | slabs, core walls, roof elements. Beams and bracing are named here by `07` §8.1.4 but **no massing `kind` produces them at P3**; if a project needs them at P3 that is a schema extension to `07` §8.1.1 and §8.1.2, not an extra kind invented in `massing.json` |
| **Note** | structural sizing remains on the `09` §5 do-not-default list. A column on this layer is a proxy with a recorded `A-nnn`, not a design |

### 1.4 `03_CORE`

| | |
|---|---|
| **Holds** | core walls, core slabs, stair and lift shafts |
| **Massing `kind`(s)** | `core_wall` |
| **Never on it** | general structure. A core wall is not a column; the two are separate kinds on separate layers, and `storeys[].core_refs` resolves only to `core_wall` |
| **Note** | stair and lift shafts are named here but are **not** massing elements at P3 — they are NURBS (P4) or assembly (P6) content. A "core slab" belongs to `03_CORE` per this vocabulary, not to `01_SLABS`, and if that is ambiguous in a given project it must be settled in the spec, not by picking a layer in the scene |

### 1.5 `04_ROOF`

| | |
|---|---|
| **Holds** | roof deck, parapet, coping, upstands |
| **Massing `kind`(s)** | `roof_deck`, `parapet` |
| **Never on it** | slabs of any storey, facade elements, site works |
| **Note** | roof elements take `storey_index: null` — they belong to no storey (`07` §8.1.1) |

### 1.6 `05_FACADE`

| | |
|---|---|
| **Holds** | panels, glazing, mullions, transoms, spandrels, reveals, doors |
| **Massing `kind`(s)** | **none.** No `kind` in §8.1.2 maps to this layer, and none may be added to satisfy a builder that wants somewhere to put a panel |
| **Never on it** | massing payload at P3 — that is the whole of §8.1.4's rule. Populated from `facade_grids.json` at P5 and `assembly.json` at P6 |
| **Note** | `grouping[].kind` may take `facade`, but it is **reserved for P5/P6 and unused at P3** (`07` §8.1.1). An unused group kind does not create facade geometry |

### 1.7 `90_SCENE`

| | |
|---|---|
| **Holds** | cameras, lights, dummies, helpers |
| **Massing `kind`(s)** | **none.** It carries grouping dummies, which come from `grouping[]`, not from `elements[]` |
| **Never on it** | payload of any kind. `grouping[].layer` is `90_SCENE` — *"the dummy, never the payload"* (`07` §8.1.1). An element on `90_SCENE` is a defect |
| **Note** | see §4 for dummy rules |

### 1.8 `99_DEBUG`

| | |
|---|---|
| **Holds** | QA probes, scatter sources, reference and wireframe geometry |
| **Massing `kind`(s)** | **none** |
| **Never on it** | anything a delivery depends on. If the model is only correct with a probe in the scene, the model is wrong |
| **Delivery state** | empty, or containing only **named** QA probes. See §6 |

---

## 2. `kind` → layer, reproduced from `07` §8.1.2

**This is a table, not a preference.** A stage may not put a column on `05_FACADE`.

**Reason, in one line:** `assembly.json.layer_map` (P6, `07` §8.5) resolves against this table, so a
mapping that varied per project would make `layer_map` unverifiable.

| `kind` | layer |
|---|---|
| `plinth` | `00_SITE` |
| `slab` | `01_SLABS` |
| `column` | `02_STRUCTURE` |
| `core_wall` | `03_CORE` |
| `roof_deck` | `04_ROOF` |
| `parapet` | `04_ROOF` |

The full `kind` set at P3 is exactly these six (`07` §8.1.1). A `kind` outside this list is not a massing
element.

---

## 3. Node naming

### 3.1 The decided convention

**A massing node is named after its spec id.**

| Spec object | Id pattern | Node name in the scene |
|---|---|---|
| element | `EL-001` | `EL_001` |
| grouping | `GRP-001` | `GRP_001` |

The transformation is: take the id, replace every `-` with `_`. Nothing else changes.

**Why.** The spec id is the contract every later stage references — `storeys[].slab_ref`,
`column_refs`, `core_refs`, `grouping[].element_ids`, `assembly.json.layer_map`, and every `qa.json`
check id. A name that is derived from that id by a fixed rule can be resolved by reading the spec; a
descriptive name cannot, and forces a lookup table that is itself unversioned.

**Where descriptive names begin.** `SLAB_L00`, `MULLION_E_03` and similar architectural names are a
**P6 assembly** concern, when `components_registry.json` and `placements[]` exist and a component
needs a readable label in the UI. They are **not** a massing-stage concern. At P3 the only
descriptive field is `grouping[].name`, and it must also resolve to the group id.

### 3.2 What a name must satisfy

| # | Rule | Why |
|---|---|---|
| N1 | **MAXScript-identifier-safe.** Letters, digits and `_` only. No spaces, no `-`, no `.`, no brackets | A name is pasted into emitted MAXScript and referenced in a typed-tool argument. `-` is also a subtraction operator, so `EL-001` in an expression reads as `EL - 001` |
| N2 | **Unique in the scene**, across all objects, not only within a layer | Names are how a later probe, a selection set or a `layer_map` entry identifies a node |
| N3 | **Stable across rebuilds.** The same locked spec produces the same names on every run | A QA diff between two builds is meaningless if names churn |
| N4 | **Derived deterministically from the spec** — id, with `-` → `_`. Never from an interactive create, a Max auto-name (`Box01`, `Dummy001`) or an index that depends on creation order | An auto-name records the order the builder happened to run in, not the design |
| N5 | **Never inferred.** If a name is needed for something with no spec id, that object has no spec entry, and a spec entry is what must be added | Same discipline as `08` §4 and the `09` §5 do-not-default list |

**N4 is the rule that prevents the most common failure.** A node created interactively, or by a probe,
acquires an auto-name. Such a node is not in the spec, is on layer `0` or `99_DEBUG`, and must be
deleted — see §6.

---

## 4. Grouping dummies

`grouping[]` in `massing.json` describes assemblies that span storeys. Each is realised in the scene
as a `Dummy` that parents its elements.

| # | Rule | Status |
|---|---|---|
| D1 | Dummies live on `90_SCENE` and on no other layer. `grouping[].layer` is `90_SCENE` | design decision, `07` §8.1.1 |
| D2 | A dummy is **never payload**. Its elements keep their own layers from §2 | design decision, `07` §8.1.1 |
| D3 | `parent_pivot_cm` is the dummy's pivot: the group's bbox centre in XY and its **minimum** Z, tol 0.5 | design decision, `07` §8.1.1 |
| D4 | A dummy must not carry geometry. A dummy with a visible mesh is not a grouping dummy; it is an unrecorded element | hygiene rule, §6 |
| D5 | Every element appears in **exactly one** group | design decision, `07` §8.1.1 |
| D6 | The dummy's node name follows §3.1 — `GRP_001`, matching `grouping[].name` | design decision, this file |

### 4.1 Verified 3ds Max behaviour that constrains dummy handling

| Fact | Evidence |
|---|---|
| `node.parent = dummy` works | `CHECKPOINT.md` §"Scene units and placement semantics" — verified 2026-10-04 |
| `getChildren` **does not exist** → use the `dummy.children` **property** | `d.children` → `#children($P3_CHILD) count=1` |
| `Dummy boxSize:` needs a **`point3`**. A float throws *"Unable to convert: 100.0 to type: Point3"* | verified 2026-10-04 |
| **`delete <dummy>` does not delete its children.** The child survives and must be deleted explicitly | `objects.count` fell by exactly 1 after deleting a dummy with one child |
| **Deleting a group must therefore delete its payload first**, or the payload becomes orphan geometry on the correct layer and passes §6 by accident | consequence of the row above |

---

## 5. The layer-assignment constraint

### 5.1 Verified finding

**An object's layer cannot be assigned from MAXScript in Max 2026.3.2. Nine routes were executed; all
failed.**

> **CORRECTED (verified 2026-10-06):** this sentence previously read *"Six routes were executed; all threw `ERR`"*.
> The six MAXScript routes below are exactly as measured, but **nine** routes are ruled out in total: P6
> executed three further ones (`3dsmax-mcp_manage_layers` assignment actions, `3dsmax-mcp_set_object_property`
> with `property=layer`, and the `manage_layers` vocabulary sweep of 40+ candidate action names, all of which
> returned a uniform `Unknown layer action`). `manage_layers`' entire vocabulary is `{list, create, delete}` —
> the action name is **not unknown, it does not exist**. See `agents/max-assembly.md` §6.3, which is the
> transcript of record for the full nine.

| # | Route rejected | Result |
|---|---|---|
| L1 | `node.layer = "0"` | `ERR` — read-only |
| L2 | `node.layer = "P3_X"` | `ERR` — read-only |
| L3 | `node.layer = LayerManager.getLayerFromName "P3_X"` | `ERR` — read-only |
| L4 | `node.setLayer "P3_X"` | `ERR` |
| L5 | `node.setProperty #layer` | `ERR` |
| L6 | `LayerManager.setLayerNode` | `ERR` |

> `07` §8.1.3 lists the same six MAXScript routes with `LayerManager.setLayer` as its sixth in place of L2/L3's
> two string forms. Both statements agree that those six were executed and all failed. `CHECKPOINT.md`
> is the transcript of record; do not re-attempt any of these — or of the three P6 routes added above.

**Do not re-attempt MAXScript layer assignment.** The finding is closed with transcripts.

### 5.2 What does work

| Operation | Route | Status |
|---|---|---|
| Create a layer | `LayerManager.newLayerFromName "NAME"` | ✅ verified 2026-10-04 |
| Read a layer | `LayerManager.getLayerFromName`, `LayerManager.getLayer 0` → `LayerProperties` | ✅ verified 2026-10-04 |
| Read an object's layer | `node.layer.name` | ✅ verified 2026-10-04 |
| Enumerate layers | `3dsmax-mcp_manage_layers` `list` only. From MAXScript: `layers`, `layers[1]`, `layers.count`, `LayerManager.layers`, `LayerManager.numLayers`, `LayerManager.getCount()` — **all fail** | ✅ verified — enumeration is not available from script |

### 5.3 `3dsmax-mcp_manage_layers` status

| Action | Status |
|---|---|
| `list` | ✅ verified 2026-10-04 |
| `create` | ✅ verified 2026-10-04 |
| `delete` | ✅ verified 2026-10-04 |
| **object assignment** | 🔴 **IMPOSSIBLE — the action name does not exist, and never will.** Six names rejected, each returning *"Unknown layer action: X"*: `move`, `assign`, `add`, `addobjects`, `moveobjects`, `setlayer`; 40+ candidates rejected in total across P3 and P6. `manage_layers`' whole vocabulary is `{list, create, delete}`. |

### 5.4 The standing rule

1. **Layer is data at P3.** `massing.json` records the target layer per element and per group.
2. **`scripts/build_spec.py` emits geometry only.** It must contain no layer code. Adding layer code to
   a MAXScript builder is a defect, not an improvement — the code cannot work (L1–L6).
3. **Application is the user's action, in the Layer dialog.** No stage applies a layer.
   > **CORRECTED (verified 2026-10-06):** this item previously read *"Application is a **P6 item**, via
   > `assembly.json.layer_map`, and only after the correct `manage_layers` action name is found. That find
   > is open item O-2."* **P6 closed it as permanently impossible** — nine routes ruled out, the vocabulary
   > is exactly `{list, create, delete}`, and the action name is not unknown, it does not exist. `layer_map`
   > is a **record of intent** only, and a builder that tries to apply it is a build **FAIL** (`G-79`).
   > **The user applies layers in the Layer dialog, permanently.**
4. **No layer name may be created ad hoc in a builder.** Layers come from §1; creation goes through
   `LayerManager.newLayerFromName` or `manage_layers create`, so the same eight names exist everywhere.

---

## 6. Delivery checklist

Run before declaring any stage done. Each row is checkable, and "looks right" is not a pass.

| # | Check | How it is judged |
|---|---|---|
| H1 | **Every node in the scene sits on a layer from §1.** No exceptions | `manage_layers list`, then `node.layer.name` per object |
| H2 | **Every layer name is exactly one of the eight**, character for character, including the two-digit prefix and the `_` | string equality against §1 |
| H3 | **No node on layer `0`** once the vocabulary is in use | `node.layer.name == "0"` returns nothing |
| H4 | **No node on a layer outside the vocabulary.** A typo'd layer is invisible until a later stage cannot find it | `manage_layers list` |
| H5 | **`99_DEBUG` is empty at delivery**, or holds only **named** QA probes — a QA probe with no name is a defect | `manage_layers list`, then inspect each object on it |
| H6 | **No orphan test geometry.** No auto-named node (`Box01`, `Dummy001`, `Teapot…`) anywhere | every node name matches N1–N4 |
| H7 | **No dummy carrying geometry** (D4) | each dummy's children are spec elements, and the dummy has no mesh of its own |
| H8 | **Every group deleted also had its payload deleted** — or the payload was re-parented | no element on `90_SCENE`; no unparented element left after a group teardown |
| H9 | **Every element appears in exactly one group** (D5) | from `massing.json`, not from the scene |
| H10 | **Deterministic rebuild produces identical names.** Build twice from the same locked spec and compare the node-name set | name-set equality, second run vs first |
| H11 | **Every `layer` value in `massing.json` matches §2 for its `kind`** | table lookup, not a preference |
| H12 | **No probe left the scene dirty.** A failed probe leaves its objects behind — sweep in the same call, not later | `objects.count` compared before and after |

> **H12 exists because of a measured failure.** Eight orphans accumulated across aborted probes during
> P3 and had to be swept (`CHECKPOINT.md`). Orphan geometry on a *correct* layer passes H1–H3 and still
> ships a wrong model, which is why H6 and H8 are separate rows.

---

## 7. Open items

| # | Item | Owner | Blocking |
|---|---|---|---|
| O-1 | `07` §8.1.4 prose says *"Nine names"*; the table has **eight** rows. Correct the prose in `07`, or add a ninth row there deliberately with a `kind` mapping. **Not settled here** — this file adds nothing | P3 / `07` owner | nothing at P3; blocks any claim that the vocabulary has nine entries |
| O-2 | ~~The `3dsmax-mcp_manage_layers` action name that assigns objects to a layer.~~ **CLOSED as impossible (2026-10-06).** **CORRECTED (verified 2026-10-06):** this row previously read *"Six names rejected (§5.3). Find it before P6 writes `layer_map`"* with owner P6 — i.e. an open task. It is not a task and never was: **nine routes were executed and all failed**, `manage_layers`' entire vocabulary is `{list, create, delete}`, and `node.layer` is read-only from MAXScript. **There is no action name to find.** Layer stays data; the user applies it in the Layer dialog | **closed** — the user | nothing blocks; `layer_map` is a record of intent and `G-79` fails any builder that acts on it |
| O-3 | Whether `04_ROOF` keeps a core slab's slab-like geometry, or whether that resolves to `03_CORE`. `07` §8.1.4 names "core slabs" under `03_CORE` while §8.1.2 maps only `core_wall` there. Settle in the spec, not in the scene | P3 → P4 | low; needs a decision before a core slab exists |
| O-4 | Beams and bracing are in the `02_STRUCTURE` vocabulary but no `kind` produces them at P3. Either they arrive at P4/P6 or the vocabulary text narrows | P3 / `07` owner | low |
| O-5 | Whether `05_FACADE` ever takes a massing `kind`. Currently none does, and §1.6 forbids adding one to suit a builder | P5 | low; nothing depends on it yet |
| O-6 | `parent_pivot_cm` tolerance 0.5 cm is inherited from the general linear tolerance (`07` §3.3). Confirm it is the right tolerance for a pivot rather than a dimension | P3 | low |
| O-7 | Per-layer colour and render flags. **UNVERIFIED, no live probe.** Neither this file nor `07` §8.1.4 declares them; `manage_layers` accepts `color`, `hidden`, `frozen`, `renderable` but no call has been made | P6 | nothing; not part of the standard today |

---

## 8. What this standard deliberately does not say

- It does **not** declare a `kind` list — `07` §8.1.1 owns it.
- It does **not** declare tolerances, units or defaults — `07` §3.3 and `09-defaults.md` own them.
- It does **not** declare dimensions — `08`/`09` own those.
- It does **not** claim that any 3ds Max tool other than `3dsmax-mcp_manage_layers`, `LayerManager.newLayerFromName`, `node.layer.name` and the parenting calls in §4.1 exists. Every other API named in this file is marked with its status and probe date, and an unprobed one is labelled UNVERIFIED rather than described.
- It does **not** resolve conflicts between sources — `10-conflict-resolution.md` §6 owns that. A layer
  disagreement between two sources is a `conflicts_resolved.json` entry with a ladder rule, never a
  layer chosen in the scene.
