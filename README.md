# GREEN Energy Management

A reference implementation project for exploring IETF GREEN energy-efficiency modeling and management of network devices and their components.

## Project Status

This repository is at the scaffold stage. The current implementation brief is [`prompt_basic.md`](prompt_basic.md), which describes the proposed controller and managed-device simulator, standards alignment, safety requirements, and validation goals.

## Intended Scope

- A managed-device simulator exposing power and energy telemetry and controllable power states.
- A controller for device discovery, telemetry collection, inventory correlation, energy-topology aggregation, and guarded state changes.
- YANG model and instance-data validation, automated tests, and a reproducible demo.

## Design References

- [Power and Energy YANG Module, draft-ietf-green-power-and-energy-yang-04](https://datatracker.ietf.org/doc/html/draft-ietf-green-power-and-energy-yang-04)
- [GREEN Framework, draft-ietf-green-framework-02](https://datatracker.ietf.org/doc/html/draft-ietf-green-framework-02)
- [GREEN Use Cases, draft-ietf-green-use-cases-02](https://datatracker.ietf.org/doc/html/draft-ietf-green-use-cases-02)
- [GREEN Controller YANG, draft-swepcarl-green-controller-yang-00](https://datatracker.ietf.org/doc/html/draft-swepcarl-green-controller-yang-00)
- [Power State Capability Discovery, draft-claise-green-capability-discovery-02](https://datatracker.ietf.org/doc/html/draft-claise-green-capability-discovery-02)
- [RFC 8348: A YANG Data Model for Hardware Management](https://www.rfc-editor.org/rfc/rfc8348)
- [RFC 8641: Subscription to YANG Notifications for Datastore Updates](https://www.rfc-editor.org/rfc/rfc8641)

The Internet-Drafts above are work in progress and may change. In particular, the controller and capability-discovery models are drafts; implementations should document the exact versions and any draft-specific interpretations they use.
