# Deep analysis — draft-claise-green-capability-discovery-03

Date of analysis: 2026-10-31

## 1. Executive conclusion

`draft-claise-green-capability-discovery-03` adds a missing **static capability layer** to the GREEN architecture.

It does not replace `draft-ietf-green-power-and-energy-yang-04`.

The three relevant views are deliberately separate:

```text
RFC 8348 hardware inventory
        |
        | identifies the physical Component
        v
RFC 9196 system capabilities
+ draft-claise-green-capability-discovery-03
        |
        | what Power States can this Component support?
        | what nominal/max Power is associated with each state?
        | how long does entry/exit take?
        v
draft-ietf-green-power-and-energy-yang-04
        |
        | what is the Component doing now?
        | measured instantaneous Power
        | current power-state/oper
        | requested power-state/admin
        | Energy Object relationships
        v
GREEN controller / Energy Management System
```

The most useful implementation direction is therefore to build a **capability-aware external GREEN controller** that reads all three views over NETCONF and correlates them by RFC 8348 hardware Component.

The first implementation cycle should remain read-only. It should prove that a controller can discover what a Component *can* do, observe what it *is doing*, and reason about dependencies without reading simulator internals.

---

## 2. Status of the draft

Current revision studied:

- `draft-claise-green-capability-discovery-03`
- Title: **A YANG Data Model for Power State Capability Discovery**
- Published: 27 October 2026
- Authors: Benoît Claise, Nils Warnke, Reshad Rahman, Gen Chen, Gary Woodward
- Intended status: Standards Track
- Datatracker currently classifies it as an active individual Internet-Draft.

Primary source:

https://datatracker.ietf.org/doc/draft-claise-green-capability-discovery/03/

Archive:

https://www.ietf.org/archive/id/draft-claise-green-capability-discovery-03.html

The GREEN WG documents page may lag the newest revision and still show revision `-02` as a related draft. For implementation, use revision `-03`.

---

## 3. Why this draft exists

`draft-ietf-green-power-and-energy-yang-04` already reports operational Energy Object information:

- current operational Power State;
- requested administrative Power State;
- instantaneous Power;
- nameplate Power;
- Energy;
- Energy Object relationships.

However, it does not tell a controller:

- which Power States a Component supports;
- expected Power in each supported state;
- maximum sustained Power in each supported state;
- typical/max entry time;
- typical/max exit time.

Those facts are required *before* asking a Component to enter a low-power state.

This is the exact role of `draft-claise-green-capability-discovery-03`.

A useful distinction is:

```text
CAPABILITY = what the hardware is able to do
STATE      = what the hardware is doing now
POLICY     = whether the controller wants/allows it to do something
CONTROL    = the request sent to change state
```

The draft models only the first of these.

---

## 4. The YANG model

The module is:

```text
ietf-power-state-capabilities
```

Its essential tree is:

```text
module: ietf-power-state-capabilities

  augment /sysc:system-capabilities:
    +--ro power-state-capabilities
       +--ro supported-power-state* [power-state]
          +--ro power-state           identityref
          +--ro nominal-power?        uint32
          +--ro max-power?            uint32
          +--ro typical-exit-time?    transition-time-ms
          +--ro max-exit-time?        transition-time-ms
          +--ro typical-entry-time?   transition-time-ms
          +--ro max-entry-time?       transition-time-ms

  augment /sysc:system-capabilities/sysc:datastore-capabilities
            /sysc:per-node-capabilities:
    +--ro power-state-capabilities
       +--ro supported-power-state* [power-state]
          +--ro power-state           identityref
          +--ro nominal-power?        uint32
          +--ro max-power?            uint32
          +--ro typical-exit-time?    transition-time-ms
          +--ro max-exit-time?        transition-time-ms
          +--ro typical-entry-time?   transition-time-ms
          +--ro max-entry-time?       transition-time-ms
```

All data is `config false`.

There are no writable nodes, RPCs, actions, or notifications defined by this module.

---

## 5. Static capability carried in the operational datastore

A subtle but important point:

**static does not mean configuration datastore.**

The capability is essentially static, but at runtime it is represented as read-only operational data.

That is consistent with RFC 9196.

For a live NETCONF server the controller retrieves it from the operational datastore.

For pre-deployment use the same schema can be carried in an RFC 9195 YANG instance-data file.

Therefore two distribution modes exist:

```text
implementation / procurement time
    RFC 9195 instance-data file
             |
             v
    same capability schema

runtime
    NETCONF
      |
      v
    operational datastore
      |
      v
    same capability schema
```

This is a major strength of the design: the controller does not need two semantic models.

---

## 6. RFC 9196 is the container, not the capability itself

RFC 9196 defines `ietf-system-capabilities`.

That module is a generic capability framework. It does not itself define GREEN power-state capabilities.

`draft-claise-green-capability-discovery-03` augments that framework.

RFC 9196 allows capability values at:

1. system-wide level;
2. datastore/node level through `per-node-capabilities`.

The GREEN draft uses both.

### System-wide form

```text
/system-capabilities/power-state-capabilities
```

Revision `-03` clarifies that this is a default applying to each Component that does **not** have a per-Component entry.

It is not a Device-total Power value.

### Per-Component form

The capability is attached to an RFC 8348 hardware Component using the RFC 9196 `node-selector`.

Example:

```text
/system-capabilities
  /datastore-capabilities[datastore='ietf-datastores:operational']
  /per-node-capabilities
    node-selector =
      "/ietf-hardware:hardware/component[name='linecard-3']"
```

The capability container under that entry applies to that selected hardware Component.

---

## 7. The critical correlation key

The draft intentionally introduces no new component identifier.

The correlation is:

```text
RFC 9196 node-selector
      |
      | selects
      v
/ietf-hardware:hardware/component[name='X']
      ^
      |
      | leafref
      |
ietf-power-and-energy:
  energy-object/source-component-id = X
```

So the controller can build:

```text
hardware component X
    |
    +-- inventory and hierarchy from RFC 8348
    |
    +-- supported Power States from RFC 9196
    |   + ietf-power-state-capabilities
    |
    +-- live Energy Object from ietf-power-and-energy
```

This is the core integration point for the implementation.

---

## 8. Important schema/prose inconsistency in power-and-energy-yang-04

The actual YANG tree and actual `source-component-id` definition in
`draft-ietf-green-power-and-energy-yang-04` use:

```yang
leaf source-component-id {
  type leafref {
    path "/hw:hardware/hw:component/hw:name";
  }
}
```

The draft prose later says that `source-component-id` is bound to the RFC 8348 `uuid`.

Those statements conflict.

`draft-claise-green-capability-discovery-03` correctly describes the current YANG-schema behavior: it correlates through the hardware Component `name`.

Implementation rule:

```text
ACTUAL YANG SCHEMA WINS.
```

Do not silently rewrite `source-component-id` as a UUID.

Keep these distinct:

```text
hardware component name
hardware component uuid
Energy Object id
relationship peer id
```

Record the prose/schema conflict as an implementation/WG observation.

---

## 9. NETCONF-level interaction

The capability model does **not** create a new NETCONF protocol operation.

It is ordinary YANG operational data.

A clean controller sequence is:

```text
NETCONF client
    |
    | 1. establish NETCONF session
    v
Netopeer2
    |
    | 2. discover available schemas/modules
    v
ietf-yang-library
    |
    | 3. read RFC 8348 hardware inventory
    v
ietf-hardware
    |
    | 4. read RFC 9196 system capabilities
    v
ietf-system-capabilities
  + ietf-power-state-capabilities
    |
    | 5. read GREEN operational state
    v
ietf-power-and-energy
    |
    | 6. correlate locally in controller
    v
capability-aware component view
```

### 9.1 NETCONF `<hello>` is not the GREEN capability database

Do not confuse:

```text
NETCONF protocol/server capabilities
```

with:

```text
RFC 9196 modeled system capability data
```

The client should use YANG Library to confirm that the required YANG modules are supported.

The actual Power State capability values are then read as modeled data.

### 9.2 Preferred read operation

For an NMDA server supporting RFC 8526, use `<get-data>` with the operational datastore.

Conceptually:

```xml
<get-data>
  <datastore>ietf-datastores:operational</datastore>
  ...
</get-data>
```

If `<get-data>` is not advertised, normal NETCONF `<get>` can retrieve configuration plus state data.

Do not use `<get-config>` to retrieve the capability subtree, because the capability nodes are `config false`.

### 9.3 Suggested separate reads

Read independently:

```text
/ietf-hardware:hardware

/ietf-system-capabilities:system-capabilities

/ietf-power-and-energy:energy-objects
```

Then correlate at the controller.

This keeps the three semantics visible and makes debugging much easier.

---

## 10. RFC 9196 precedence rules matter

The controller must not simply concatenate system-wide and per-node capabilities.

RFC 9196 gives more-specific capability entries precedence.

For this GREEN draft, revision `-03` further clarifies the intended behavior:

```text
per-Component entry exists
    -> use it for that Component

no per-Component entry
    + system-wide entry exists
    -> system-wide capability applies to that Component

neither exists
    -> capability is unknown
```

Unknown is not zero.

A controller must distinguish:

```text
unsupported
unknown
supported without power figures
supported with power figures
```

These are semantically different.

---

## 11. Partial coverage is first-class

A Device may advertise capabilities for only some hardware Components.

The controller should compare:

```text
RFC 8348 inventory
vs.
components covered by per-node capabilities
plus
components covered by the system-wide fallback
```

Suggested statuses:

```text
COVERED_PER_COMPONENT
COVERED_BY_SYSTEM_DEFAULT
UNKNOWN_CAPABILITY
```

For subtree totals, if one or more Components are not covered, the sum of
`nominal-power` or `max-power` is not a complete total.

The draft says such a sum is a lower bound.

---

## 12. Capability values are per Component, not recursive totals

A Component's:

```text
nominal-power
max-power
```

describe that Component only.

They do not include its RFC 8348 children.

For example:

```text
chassis
  linecard
    port
    transceiver
```

the linecard capability value does not implicitly include the port or transceiver.

Any aggregate must explicitly walk the RFC 8348 hierarchy and count Components once.

This is especially important for avoiding double counting.

---

## 13. Power State identity reuse

The discovery draft reuses the `power-state` identity hierarchy from
`ietf-power-and-energy`.

Important base states include:

```text
power-state-on
power-state-off
power-state-sleep
```

Additional low-power depths may derive from `power-state-sleep`.

Therefore `sleep-capable` is a **derived fact**, not another leaf:

```text
Component is sleep-capable
    iff
it advertises a supported state derived from power-state-sleep
```

Implementation consequence:

Do not implement sleep capability as only:

```python
state == "power-state-sleep"
```

because vendor/extended identities can derive from `power-state-sleep`.

Prefer schema-aware identity ancestry.

---

## 14. Static Power Savings Potential

For a particular low-power state:

```text
static PSP =
    nominal-power(power-state-on)
  - nominal-power(low-power-state)
```

Example from the draft:

```text
ON nominal power    = 200 W
SLEEP nominal power = 15 W

static PSP = 185 W
```

Important restrictions:

- only derive it if both nominal values exist;
- do not substitute `max-power` for missing `nominal-power`;
- do not substitute measured instantaneous Power and still call the result the same static PSP;
- this is a planning baseline, not the load-dependent real-time saving.

---

## 15. Interaction with Nameplate Power

`draft-ietf-green-power-and-energy-yang-04` provides `nameplate-power`.

The discovery draft adds per-state:

```text
nominal-power
max-power
```

For `power-state-on`, when nameplate Power is available:

```text
nominal-power <= nameplate-power
max-power     <= nameplate-power
```

The values are not required to equal nameplate Power.

If ON-state capability Power is absent, nameplate Power may be a planning fallback, but it must remain labeled as a fallback and not silently become `nominal-power`.

---

## 16. Transition-time semantics

For each low-power state the draft can report:

```text
typical-entry-time
max-entry-time
typical-exit-time
max-exit-time
```

These are relative to `power-state-on`.

The model does not define a general transition matrix.

For example:

```text
ON <-> SLEEP-1
ON <-> SLEEP-2
```

can be characterized, but:

```text
SLEEP-1 -> SLEEP-2
```

is not directly characterized.

This remains an explicit open issue in revision `-03`.

---

## 17. Capability is not eligibility

This is one of the most important rules in the draft.

If a Component advertises:

```text
power-state-sleep
```

that means:

```text
the Component is capable of sleeping
```

It does not mean:

```text
the Component is currently allowed to sleep
```

Eligibility depends on runtime policy and network conditions, such as:

- resilience;
- N+1 protection;
- reserved capacity;
- traffic;
- service requirements;
- dependent Components.

Therefore a controller must keep separate fields such as:

```text
capability_status
dependency_status
policy_status
recommendation
```

Do not reduce these to one Boolean `can_sleep`.

---

## 18. Interaction with Energy Object relationships

Revision `-03` significantly strengthens integration with the GREEN Power and Energy model by explicitly pointing to:

```text
enabling
enabled-by
```

for cross-Component functional dependencies.

Example:

```text
SerDes
  ENABLING -> port-A
  ENABLING -> port-B
```

The SerDes may support a sleep state according to capability discovery.

But whether it may enter that state depends on its dependents.

The capability draft intentionally does not model this dependency itself.

So the controller needs both:

```text
capability discovery
+
GREEN Energy Object relationships
```

This is a strong reason to implement the two drafts together.

---

## 19. Relationship semantics remain directional

The controller must preserve the exact GREEN identity direction:

```text
enabling
enabled-by

powering
powered-by

metering
metered-by

aggregating
aggregated-by
```

Capability discovery does not alter these relationships.

Do not manufacture inverse entries unless they are explicitly marked as a derived display.

---

## 20. Why relationships still do not prove eligibility

Even if the controller knows:

```text
serdes-0 ENABLING port-1
```

it may still not know whether `port-1` is idle.

The discovery draft's SerDes discussion explains the dependency, but the capability model does not add a traffic-idle indicator.

Therefore the safe decision logic is:

```text
supported sleep state
+ dependent relationships known
+ dependent-idle evidence known
+ policy permits
--------------------------------
candidate eligible
```

If dependent-idle evidence is not represented, the result is:

```text
dependency status = UNKNOWN
```

not `CLEAR`.

---

## 21. Interaction with `power-state/admin`

The intended control chain is:

```text
discover supported states
        |
        v
evaluate capability + dependencies + policy
        |
        v
select an allowed target state
        |
        v
write GREEN power-state/admin
        |
        v
observe power-state/oper
```

The discovery draft explicitly says a management system needs the capability before writing the GREEN `admin` leaf.

However, the chosen first implementation direction deliberately stops before this write.

That keeps the first cycle read-only and lets us validate the information model before adding control.

---

## 22. Interaction with the GREEN Controller YANG work

`draft-swepcarl-green-controller-yang-00` describes a GREEN Controller responsible for:

- collection;
- filtering;
- transformation;
- aggregation;
- delivery;
- network energy state;
- audit/provenance.

The draft is still early and contains TBD areas.

`draft-claise-green-capability-discovery-03` supplies a particularly useful controller input:

```text
what each physical Component can do
```

A controller can combine it with:

```text
current measurements
current Power State
hardware hierarchy
energy relationships
controller policy
```

to create recommendations.

The current controller draft does not eliminate the need for the device-side RFC 9196 capability model.

The two are complementary:

```text
device capability advertisement
        ->
controller collection and reasoning
```

---

## 23. Interaction with provenance work

`draft-madpr-green-provenance-00` augments the GREEN Power and Energy Energy Objects with provenance-verification results.

It does not currently provide an equivalent provenance augmentation for
`ietf-power-state-capabilities`.

The discovery draft instead relies on:

- authenticated management transport;
- NACM for read control;
- careful handling of RFC 9195 instance-data files.

For a future controller, provenance of vendor capability data is a separate question from provenance of live energy telemetry.

Do not silently treat the provenance state of an Energy Object as proving the authenticity of the corresponding capability data.

---

## 24. Interaction with YANG Push

The capability draft defines no notification.

RFC 9196 says that implementations whose capabilities can change at runtime should support on-change notifications for the `system-capabilities` container.

For the first implementation:

- use ordinary NETCONF reads;
- treat capability data as stable;
- do not require YANG Push.

A later experiment could test on-change capability refresh, but it should be a separate step.

---

## 25. Interaction with TE / IGP power work

The discovery draft references:

- `draft-many-teas-power-steering`
- `draft-many-lsr-power-group`

Those works need concepts such as:

```text
power-sleep-capable
Power Savings Potential
```

The discovery model can provide a common static source:

```text
sleep-capable
    derived from supported Power State identities

static PSP
    derived from per-state nominal Power
```

The draft does not replace the routing advertisements.

Dynamic/load-dependent quantities remain outside the capability model.

This separation is also consistent with the GREEN charter, where routing protocol algorithms are not the central GREEN deliverable.

---

## 26. Interaction with GREEN use cases

Revision `-03` explicitly identifies these use cases as depending on Power State capability discovery:

- UC 2.1 — Incremental Application of the GREEN Framework
- UC 2.2 — Selective reduction of energy consumption in network parts proportional to traffic levels
- UC 2.7 — Dynamic adjustment of network element throughput according to traffic levels in wireless transport networks
- UC 2.9 — WLAN Network Energy Saving
- UC 2.10 — Fixed Network Energy Saving
- UC 2.11 — Energy Efficiency Network Management
- UC 2.14 — Energy Efficiency Under Power Shortage
- UC 2.16 — Network-level Cross Layer Energy Saving
- UC 2.17 — AI Agents for Energy Efficiency Management

For the existing simulator, the cleanest initial demonstrations are:

```text
UC 2.1
UC 2.9
UC 2.10
UC 2.14
UC 2.16
```

because they naturally expose differences between capability, operational state, dependencies and policy.

---

## 27. Fit with the GREEN WG charter

The current GREEN charter explicitly includes:

- energy efficiency capability discovery;
- YANG models for monitoring and management;
- incremental deployment;
- configurable energy efficiency capabilities;
- implementation/adoption experience.

The capability draft therefore fills a charter-level requirement rather than being an isolated extension.

It is particularly relevant to the WG's stated preference for simple foundational building blocks.

---

## 28. Major design strengths

### 28.1 Separation of concerns

Capability is not mixed into live telemetry.

### 28.2 Reuse of existing identifiers

The model reuses RFC 8348 Component identity instead of defining another object identifier.

### 28.3 Reuse of Power State identities

No parallel GREEN capability-state vocabulary is introduced.

### 28.4 Implementation-time and runtime equivalence

RFC 9195 and NETCONF use the same schema.

### 28.5 Incremental deployment

Partial capability coverage is explicitly allowed.

### 28.6 Controller-friendly derivation

`sleep-capable` and static PSP can be derived rather than separately configured.

---

## 29. Main implementation traps

1. Confusing operational datastore with dynamic telemetry.
2. Reading capability data with `<get-config>`.
3. Treating RFC 9196 capability data as NETCONF `<hello>` capabilities.
4. Correlating by Energy Object ID instead of RFC 8348 Component.
5. Following the erroneous UUID prose instead of the actual `source-component-id` leafref.
6. Treating unknown capability as zero.
7. Treating unsupported and unknown as equivalent.
8. Merging system-wide and per-Component capability incorrectly.
9. Ignoring RFC 9196 precedence.
10. Assuming a parent capability applies to children.
11. Counting parent and child Power recursively without coverage logic.
12. Treating `nominal-power` as a measurement.
13. Treating `max-power` as `nominal-power`.
14. Treating capability as runtime eligibility.
15. Ignoring `enabling/enabled-by` dependencies.
16. Assuming a dependency is idle merely because a relationship exists.
17. Recognizing only the literal `power-state-sleep` identity and missing derived low-power identities.
18. Treating transition times as a general state-to-state matrix.
19. Assuming capabilities from an RFC 9195 file apply to another platform/software release.
20. Modifying upstream YANG to simplify the implementation.

---

## 30. Short list of possible implementation directions

### Direction A — Device capability advertisement only

Implement `ietf-power-state-capabilities` in Sysrepo/Netopeer2 and prove it can be read through NETCONF.

Value: validates the draft and NETCONF encoding.

Limitation: does not show what a controller does with the capability.

### Direction B — Capability-aware GREEN controller over NETCONF

Combine:

```text
RFC 8348 inventory
+ RFC 9196 capability discovery
+ GREEN live power state
+ GREEN relationships
```

and derive capability coverage, sleep capability, static PSP and safe decision support.

Value: highest relevance to the existing `allrun5 -> controller` implementation.

### Direction C — RFC 9195 pre-deployment catalogue

Build vendor/platform instance-data files and compare capabilities before deployment.

Value: very relevant to procurement/planning and the draft design.

Limitation: less direct interaction with the current live NETCONF simulator.

### Direction D — Capability-gated NETCONF control

Use discovered capabilities to validate a target Power State, then write `power-state/admin` and observe `power-state/oper`.

Value: complete closed loop.

Limitation: adds control policy and safety before the read-only model has been fully validated.

---

## 31. Chosen direction

Choose:

# Direction B — Capability-aware GREEN controller over NETCONF

Why:

1. It directly extends the current `allrun5` / controller architecture.
2. It tests the most important semantic claim of the discovery draft: one physical Component joins capability and live state.
3. It exposes actual interoperability issues in the current drafts.
4. It remains safe and read-only.
5. It prepares a later control experiment without prematurely mixing capability and policy.
6. It produces useful feedback for the GREEN WG.

---

## 32. Incremental implementation plan

### green10 — device capability exposure

Create a device-side capability provider using the exact revision `-03` model and expose it through the same Sysrepo/Netopeer2 NETCONF environment as the GREEN device data.

Output:

```text
caprun10/
```

Main proof:

```text
NETCONF -> operational datastore -> RFC9196 capability subtree
```

### green11 — external controller correlation

Build an external NETCONF client that joins:

```text
ietf-hardware
ietf-system-capabilities + ietf-power-state-capabilities
ietf-power-and-energy
```

Output:

```text
caprun11/
```

Main proof:

```text
one Component -> inventory + capability + live state
```

### green12 — capability-aware decision support

Add:

- coverage analysis;
- sleep-capable derivation;
- static PSP;
- nameplate consistency checks;
- transition-time checks;
- `enabling/enabled-by` dependency reasoning;
- deterministic recommendations;
- explicit UNKNOWN handling.

Output:

```text
caprun12/
```

No `<edit-config>` yet.

---

## 33. Target architecture after green12

```text
                    +--------------------------+
                    | RFC 8348 hardware        |
                    +------------+-------------+
                                 |
                                 | component name
                                 |
+-----------------------+        v        +-------------------------+
| RFC 9196              |   +---------+   | GREEN power/energy      |
| system capabilities   +-->| JOINER  |<--+ live operational state  |
| + power-state caps    |   +----+----+   | + relationships         |
+-----------------------+        |        +-------------------------+
                                 |
                                 v
                     +------------------------+
                     | capability-aware       |
                     | controller view        |
                     +-----------+------------+
                                 |
                 +---------------+----------------+
                 |               |                |
                 v               v                v
             coverage        static PSP      dependency /
                                             transition checks
                                 |
                                 v
                         recommendation only
                         NO device control
```

---

## 34. IETF feedback likely to be valuable

An implementation of this direction can provide concrete WG feedback on:

1. Whether RFC 9196 `node-selector` is practical for large hardware inventories.
2. Whether system-wide fallback semantics are sufficiently clear.
3. Whether repeated capabilities for identical components cause material data expansion.
4. Whether schema-aware identity derivation is easy enough for controllers.
5. Whether component name is sufficient as the local join key.
6. The prose/YANG conflict around `source-component-id` and UUID in `draft-ietf-green-power-and-energy-yang-04`.
7. Whether transition times relative only to ON are sufficient.
8. Whether dependency information from `enabling/enabled-by` is enough for useful control preparation.
9. Which required eligibility inputs are still outside the current models.
10. How capability coverage should be surfaced in controller/network-wide views.

---

## 35. Sources

- draft-claise-green-capability-discovery-03  
  https://datatracker.ietf.org/doc/draft-claise-green-capability-discovery/03/

- draft-ietf-green-power-and-energy-yang-04  
  https://datatracker.ietf.org/doc/draft-ietf-green-power-and-energy-yang/04/

- draft-ietf-green-framework-02  
  https://datatracker.ietf.org/doc/draft-ietf-green-framework/

- draft-ietf-green-use-cases-02  
  https://datatracker.ietf.org/doc/draft-ietf-green-use-cases/02/

- draft-swepcarl-green-controller-yang-00  
  https://datatracker.ietf.org/doc/draft-swepcarl-green-controller-yang/

- draft-madpr-green-provenance-00  
  https://datatracker.ietf.org/doc/draft-madpr-green-provenance/

- RFC 9196 — YANG Modules Describing Capabilities for Systems and Datastore Update Notifications  
  https://datatracker.ietf.org/doc/rfc9196/

- RFC 9195 — A File Format for YANG Instance Data  
  https://datatracker.ietf.org/doc/rfc9195/

- RFC 8348 — A YANG Data Model for Hardware Management  
  https://datatracker.ietf.org/doc/rfc8348/

- RFC 8342 — Network Management Datastore Architecture  
  https://datatracker.ietf.org/doc/rfc8342/

- RFC 8525 — YANG Library  
  https://datatracker.ietf.org/doc/rfc8525/

- RFC 8526 — NETCONF Extensions to Support NMDA  
  https://datatracker.ietf.org/doc/rfc8526/

- RFC 6241 — NETCONF  
  https://datatracker.ietf.org/doc/rfc6241/

- GREEN WG charter  
  https://datatracker.ietf.org/wg/green/about/
