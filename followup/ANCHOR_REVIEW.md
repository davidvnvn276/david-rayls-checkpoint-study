# Starting-Anchor Review

The initial committee has not been independently authenticated by this review.

The original seven public keys and epoch-0 record hash are preserved inside the unchanged original publication archive. Every later verification retains that observed anchor.

The follow-up inspected the public Axyl tree at commit `6909618ba3d178884e613b329a99816ba546f62e`, including:

- `etc/observer/README.md`: lists network genesis, committee and parameter files as inputs supplied by the network operator.
- `etc/validator/README.md`: likewise requires operator-provided network bootstrap files.
- `etc/manage/src/client-node/genesis.sh`: constructs bootstrap files from supplied validator node information; it is a generation procedure, not an authenticated mainnet committee publication.
- The genesis/chainspec source and genesis-deployment utilities: do not establish the provenance of the seven observed initial mainnet keys in this study.

No operator-authenticated mainnet bootstrap artifact was obtained and validated against the observed keys. This is a statement about the review's inspected sources and obtained inputs, not a claim that no such artifact exists anywhere.

The new 175-header retrieval used the same official RPC. The complete py_ecc check uses the same captured certificate inputs. Neither operation is an independent source of starting-key authority.

The synthetic alternative chain intentionally passes under its own supplied anchor. Its positive outcome illustrates why a mathematically consistent chain cannot authenticate the provenance of its own initial keys.

To close this limit, a reader needs an authenticated genesis committee or checkpoint from a source they explicitly trust, must verify its exact key/hash identity, and must then run the same continuity and signature checks from that anchor. Repeating a query to the same endpoint is not that step.

Primary bootstrap reference: https://github.com/raylsnetwork/axyl/blob/6909618ba3d178884e613b329a99816ba546f62e/etc/observer/README.md
