# Relationship Behavior Classes

| Behavior class | Relationship types | Directed links | Semantics |
| --- | --- | ---: | --- |
| stable-structural | aggregated-by, aggregating, enabled-by, enabling | 24 | Persistent functional structure, including aggregation and enabling dependencies. |
| physical-dynamic | powered-by, powering | 12 | The active electrical source path; UC 2.14 changes grid/battery links as state changes. |
| knowledge-observability | metered-by, metering | 8 | Physical metering links whose controller visibility can be incomplete or discovered later. |

Hardware `parent` containment does not imply metering, aggregation, powering, or enabling.

## UC 2.13 Discovery

The canonical physical metering topology exists independently of controller visibility. U13-0 keeps the actual links in the topology truth set while exposing no metering links to the event observer; later discovery overlays expose the links. Accounting uses only event-visible relationships, so incomplete knowledge remains incomplete rather than fabricating a physical topology change.
