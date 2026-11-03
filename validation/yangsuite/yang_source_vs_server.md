# Source YANG versus server YANG

Status: comparison not performed.

No schemas or module list were retrieved from Netopeer2. Consequently there are no verified revision, import, include, or Sysrepo-installation comparisons. The source of truth for source revisions remains the repository under `allrun51/yang/`; the deployed server revisions must be obtained independently after NETCONF is available.

Do not replace source modules based on an unverified assumption. Record missing imports, unexpected modules, and revision mismatches after collecting the server list.