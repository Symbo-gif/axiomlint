# PyRS-0: declared review subset, not an implemented translator

Status: design draft for WP-010/WP-013. No formal claim is enabled.

First target: pure deterministic, synchronous, explicitly typed functions over
Booleans and mathematical integers, with handwritten pre/postconditions.
Python integers are unbounded subject to host resource limits; Boolean/int
subtyping must be handled explicitly rather than silently using solver coercions.
Division, modulo, negative operands and exceptions require dedicated semantics.

Reject or abstain initially: imports with effects, I/O, network, globals, mutation,
aliasing, decorators with runtime effects, reflection/eval/exec, generators,
async, concurrency, native extensions, nondeterminism, user-defined numeric
coercions, arbitrary recursion, floating-point identities, and undeclared
exceptions. Future collections/recursion/bit-vectors need separate conformance.

AST inventory merely lists top-level function locations. It does not decide
membership, purity, termination, well-typedness or correspondence.
Correspondence statuses to define in WP-005 are DIRECT, TESTED_TRANSLATION,
REVIEWED_TRANSLATION, UNSUPPORTED and ASSUMED. Only the future separately
approved correspondence pilot can enable EV-E6 for a bounded fragment.

