# Interactive Fixtures — the shared contract

**Doors, breachable walls, and anything whose state all players must agree on.**

This file is the contract between three layers of the pipeline. Copy it into
both `zoo` and `deli-counter` so they stay in sync; the game
(`DELCO_DANGEROUS`) reads it too.

---

## The one principle

**The contract describes STATE, never SYNCHRONIZATION.**

It says *what* is interactive, *what discrete states* it can be in, and *what
named transitions* move between them. It says **nothing** about who is
authoritative, how state replicates, tick rate, interpolation, or ownership.
All of that is the game's networking layer, chosen later.

That is the whole reason this stays network-solution-agnostic. Do not add a
field that tells the netcode *how* to replicate. If you ever want to, it goes in
the game, not here.

---

## The model: a replicable state machine

Every interactive fixture is:

```
(stable_id, states[], default, transitions[])
```

That tuple is the **entire networked surface**. It maps onto any solution:

| Networking solution        | What it replicates                                   |
|----------------------------|------------------------------------------------------|
| Server-authoritative snapshot | the current-state enum per `id`                   |
| Event / RPC                | the named transition per `id`                        |
| Deterministic lockstep     | the input; every client runs the same transition     |
| Rollback                   | the state enum is in the snapshot; transitions are deterministic |

Because the contract carries **both** the state set **and** the named
transitions, the game replicates whichever fits — and nothing here had to
commit to one.

---

## The two files

The seam splits along the existing **art vs gameplay** line.

### 1. `<building>.slots.json` — art swap contract (Zoo / the resolver read this)

The `interactive` block only declares the **state set** and (optionally) which
module geometry backs each state. The resolver derives per-state art from the
naming law's `_<state>` suffix, so it stays theme/style-agnostic.

```json
{
  "role": "doorway",
  "slot_id": "gs_auto_shop.slot.0007",
  "transform": { "translation": [12.0, 0.0, 3.5], "rot_y": 90, "scale": [1,1,1] },
  "fit": { "dims": [1.1, 0.3, 2.2], "pivot": "center", "collision": true },
  "current_ref": "doorway_delco_01_w110",
  "interactive": {
    "id": "gs_auto_shop:if:07",
    "kind": "door",
    "states": ["closed", "open"],
    "default": "closed",
    "state_geometry": { "closed": "doorway", "open": "doorway" },
    "collision_per_state": { "closed": true, "open": false }
  }
}
```

### 2. `<building>.gameplay.json` — netcode-owned (the game reads this)

Self-sufficient, so the replication layer never parses art. Deli Counter emits
one entry per interactive slot.

```json
"interactives": [
  {
    "id": "gs_auto_shop:if:07",
    "kind": "door",
    "slot_ref": "gs_auto_shop.slot.0007",
    "transform": { "translation": [12.0, 0.0, 3.5], "rot_y": 90 },
    "states": ["closed", "open"],
    "default": "closed",
    "transitions": [
      { "event": "toggle", "from": "closed", "to": "open" },
      { "event": "toggle", "from": "open",   "to": "closed" }
    ]
  },
  {
    "id": "gs_auto_shop:if:12",
    "kind": "breach_wall",
    "slot_ref": "gs_auto_shop.slot.0031",
    "transform": { "translation": [20.0, 0.0, 0.0], "rot_y": 0 },
    "states": ["intact", "breached"],
    "default": "intact",
    "transitions": [
      { "event": "breach", "from": "intact", "to": "breached" }
    ],
    "reversible": false
  }
]
```

---

## Field reference

### `interactive` block (slots.json)

| Field                 | Required | Meaning                                                      |
|-----------------------|----------|--------------------------------------------------------------|
| `id`                  | yes      | Stable network handle (see **Stable ids** below).            |
| `kind`                | yes      | Fixture kind (`door`, `breach_wall`, `window`, …). Advisory. |
| `states`              | yes      | The discrete states, in a stable order.                      |
| `default`             | rec.     | Starting state. If omitted, `states[0]`.                     |
| `state_geometry`      | no       | `{state: module_species}` — which geometry backs each state. Unmapped states use the slot's own type. |
| `collision_per_state` | no       | `{state: bool}` hint for the game; art also carries collision. |

### `interactives` entry (gameplay.json)

| Field         | Required | Meaning                                                          |
|---------------|----------|------------------------------------------------------------------|
| `id`          | yes      | Same handle as the slot's `interactive.id`.                      |
| `kind`        | yes      | Fixture kind.                                                    |
| `slot_ref`    | yes      | The `slot_id` this drives (art lives there).                     |
| `transform`   | yes      | World placement (netcode may spawn a node here).                |
| `states`      | yes      | Discrete states.                                                 |
| `default`     | yes      | Starting state.                                                  |
| `transitions` | yes      | `{event, from, to}` edges — the named moves between states.     |
| `reversible`  | no       | **Advisory.** Whether the machine can go backward.              |
| `authority_hint` | no    | **Advisory.** `server` / `host` / `shared`. Netcode may ignore. |
| `persist`     | no       | **Advisory.** Whether state should survive across a session.    |

---

## Stable ids — the one thing to get right

`id` is the handle every client, snapshot, and saved game references. It **must
be deterministic AND stable across a re-greybox**.

- **Do NOT derive it from array index.** Adding one slot upstream renumbers
  everything and silently breaks every networked reference and any saved state.
- **Do** derive it from something positional and stable: a hash of
  `(building_id, role, rounded_translation)`, or a designer-assigned slot GUID
  that Deli Counter persists in the source.

This is the single place a bug is genuinely nasty, so it's worth nailing.

---

## Advisory hints stay advisory

`reversible`, `authority_hint`, `persist`, `collision_per_state` are
**descriptions the netcode MAY honor or ignore** — never instructions. The
moment the contract says "replicate this way," it stops being agnostic.

---

## Mid-states and continuous motion

Handle these with the **state set**, not by adding networking concepts.

- A door that can be ajar → `["closed", "ajar", "open"]`.
- A wall that cracks before it blows → `["intact", "damaged", "breached"]`.

The *visual* swing of the door between states is **presentation the game
interpolates locally**; the networked truth stays the discrete checkpoint. You
never sync a float angle — so the contract stays agnostic to whether the game
interpolates, animates, or hard-swaps meshes.

---

## Ownership — who owns what

| Layer            | Owns                                                                 |
|------------------|----------------------------------------------------------------------|
| **Zoo**          | The per-state **art variants** (via the `_<state>` naming law). Netcode-free. |
| **Deli Counter** | The **seam**: flags a slot interactive, assigns the stable `id`, emits both blocks. |
| **The game**     | The **netcode**: one replicated node per `id`, drives which variant renders. |

None of the networking lives in Zoo or Deli Counter. They stay offline and
deterministic — they only expose the seams so replication has a clean hook.

---

## The naming law + progressive art pass

Art variants follow Zoo's module naming law:

```
<type>_<theme>_<style:02d>[_w<cm>][_<state>].glb
```

- The **default** state = the base stem (no `_<state>`), which `current_ref`
  points at.
- A **non-default** state = base stem + `_<state>`, e.g.
  `doorway_delco_01_w110_open`, `wall_delco_01_w200_breached`.

The resolver **falls back to the base module when a `_<state>` variant is
missing** — so the art pass is progressive. Zoo only builds a variant when its
geometry actually differs from the default (see below); until the art pass
gives, say, an open door its own leaf, the `open` state renders the base and
nobody has to author a duplicate.

### `state_geometry`: which module a state is built from

`state_geometry` maps `state -> module species`. A non-default state whose
species **differs** from the default's is built as a distinct variant; one that
**matches** is deferred (identical art today → resolver fallback).

This is what makes **a breachable wall the `breached` STATE of a wall slot**,
not a standalone module:

```json
"state_geometry": { "intact": "wall", "breached": "breach" }
```

→ Zoo builds `wall_delco_01_w200` (wall geometry) **and**
`wall_delco_01_w200_breached` (breach geometry, at the wall's exact dims). The
standalone `breach` species is still for walls authored *pre-blown*; a
*breachable* wall is one slot with two states.

---

## What Zoo does today (v0.16.0)

`core.kit.plan_kit` reads each slot's `interactive` block and expands it:

- default state → base module
- each non-default state with **differing** geometry → a `_<state>` variant,
  built with its `state_geometry` species at the slot's exact dims
- same-geometry states → reported under `deferred_variants` (not built)

`build.build_kit` builds all variants into `art/zoo/` and records
`state`/`species` per module plus the deferred list in
`<building>_kit.built.json`.

```bash
# dry plan (pure, no Blender) — shows variants + deferrals
python tools/zoo_cli.py --kit <building>.slots.json --theme delco

# build (needs Blender)
blender --background --python tools/zoo_cli.py -- \
  --build-kit <building>.slots.json --theme delco --out art_zoo
```

Zoo does **not** invent ids or transitions — those live in `gameplay.json`,
emitted by Deli Counter. Zoo builds the art the states point at; the state
machine and its replication are the game's.
