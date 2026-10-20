# Draft threat model and assurance case

Status: draft input to WP-003, not independently approved.

## Assets and actors

Assets: source confidentiality; source/spec identity; evidence integrity;
valid bounded claims; host credentials; hidden benchmark labels; reproducible
environments and permanent research records. Actors: maintainer, independent
reviewer, accidental-error producer, hostile source/prompt author, compromised
dependency/tool, and same-user attacker who can rewrite local files.

## Boundaries, threats, mitigations and residuals

| ID | Threat/boundary | Foundation control | Verification / residual |
|---|---|---|---|
| T-01 | Subject executes on host | Runner always refuses; inventory never imports | Disabled-runner and nonexecution tests; hostile parse DoS remains |
| T-02 | Prompt injection grants authority | No LLM calls/promotion; charter outranks agent text | Capability tests; future adapter must isolate data/instructions |
| T-03 | Corrupt evidence accepted | Digests, exclusive creates, verification on read | Corruption/missing/symlink tests; same-user rewrite not prevented |
| T-04 | Path traversal/symlink reads host | Digest-only store names; final no-follow intake | Invalid digest, symlink, nonregular-file tests; trusted parent required |
| T-05 | Failed scan appears clean | No review verdict emitted, capabilities unavailable | CLI inventory is NOT_REVIEWED; future adapters need failed/partial tests |
| T-06 | Source-model mistranslation | No E3-E6 labels; PyRS/correspondence deferred | Status tests; formal translator not implemented |
| T-07 | Benchmark leakage / p-hacking | No benchmark execution; EXP-E0-E6 template | Protocol/holdout process draft; no effectiveness claim |
| T-08 | Credential/environment leakage | Local gate child env allowlist; no host env snapshot | Runner tests; trusted tests can still access host files |
| T-09 | False approval / cycle skipping | Pending approvals, S2 independence and closure barriers | Governance mutation tests; human review still required |
| T-10 | Dependency compromise | No runtime dependencies, no resolver in checks | Hygiene gate; Python/OS/Git remain TCB |
| T-11 | Stale gate on different source | Commit + full tree hash + post-run equality | Fingerprint tests and exact SHA logs; no authenticated attestation |
| T-12 | Host exhausts resources | Only trusted tests; no hostile fixtures executed | Timeouts for commands, bounded intake; no memory/PID isolation yet |

## Attack paths

```text
False assurance
  -> forge candidate -> no candidate acceptance implementation
  -> overwrite evidence -> hash mismatch detected unless manifest also replaced
  -> mistranslate Python -> correspondence unimplemented, E6 unavailable
  -> fake CLOSED -> structural blockers + independent human review required

Host compromise
  -> import reviewed code -> no import path exists
  -> exploit parser -> trusted small-input restriction; residual risk remains
  -> malicious test/dependency -> tests are trusted repository code; review required
```

Residual risks are not accepted by the agent. Maintainer approval and independent
threat-model review are prerequisites to closing WP-003 or enabling execution.
The foundation provides a conservative starting trust case, not high assurance.

