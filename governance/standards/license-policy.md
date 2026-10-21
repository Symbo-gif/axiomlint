# FOSS licensing and material-adoption policy

Status: WP-001 S1 implementation of the ratified FOSS boundary and existing
security/dependency standard; independent review is pending. This policy is
not legal advice, complete third-party license clearance or release acceptance.

## Project source and notices

The current project-authored code is offered under the existing root MIT
LICENSE. Its observed SHA-256 is
`7d3000977eec41c902e23ba0462a58c71fd7565b63f9607612f1c7baee8c797c`.
The MIT text requires retaining its copyright and permission notices in copies
or substantial portions and disclaims warranty/liability
([OSI MIT text](https://opensource.org/license/mit)).

The project license does not relicense imported source, rules, models, datasets,
quoted documents or restricted generated output. Retain applicable original
notices, provenance and redistribution conditions. A reference URL or public
repository is not a license grant.

## Material classes and required adoption record

Before a new material becomes mandatory, record:

- **Identity:** owner, purpose, source URL/origin, exact version/commit/build,
  source/binary/weights/rule/corpus digest and transitive dependencies.
- **Rights:** license identifier/text digest, notices, redistribution/modification
  conditions, use restrictions, generated-output or model/dataset conditions,
  compatibility rationale and isolation boundary.
- **Evidence:** actual files/text examined, reviewer/context, uncertainty,
  vulnerability/update considerations and decision reference.
- **Decision:** REQUIRED_ONLY_AFTER_APPROVAL, OPTIONAL_ISOLATED, QUARANTINED,
  REJECTED or NOT_ADOPTED; status must reflect reality rather than availability.

Source, binary build, enabled features, rules and transitive libraries may have
different licensing. Check them separately. Unknown, missing, mixed or
incompatible rights block mandatory adoption; do not infer permissive terms
from a neighboring repository or query library.

## Current foundation and toolchain limits

`governance/licenses/foundation-materials.json` separates project-authored
material from the installed toolchain, optional packaging and unadopted future
backends. Mandatory Python package dependencies are currently empty; that does
not make Python, Git, the OS or their bundled/native libraries unlicensed,
unpinned or audited away.

Python's official license page identifies the PSF terms and separately
incorporated-software notices, and is not an inventory of this installed binary
([Python licensing](https://docs.python.org/3/license.html)).
Record installed distribution/package notices and provenance before claiming
a complete toolchain audit. The local Git copyright file was inspected for
context; its multiple notice sections are not reduced to a blanket license
claim for every linked component.

The unpinned setuptools build requirement in pyproject is not exercised by the
stdlib-only gate. Build/install locking, SBOM, full transitive audit and supported
environment verification remain WP-004/WP-034 work. Nothing in this policy
authorizes installing, resolving or downloading tools during local tests.

## Specific exclusions and optional boundaries

No mandatory Wolfram engine/API, restricted CodeQL engine, proprietary model/API
or unreviewed ruleset enters the FOSS baseline. A permissive query/rule repository
does not clear a separately licensed engine or service.

Semgrep rules require their own verified rights; do not import a full registry
by default. Model weights, tokenizers, serving backend, prompts, corpus tasks and
oracle materials each require their own provenance/rights review. Future
Sage/Maxima or other copyleft components need an explicit compatibility and
isolation decision; process isolation alone is not asserted as legal clearance.

An external/commercial benchmark arm, if ever separately authorized, remains a
subject of comparison rather than a mandatory core dependency. No remote source
disclosure or purchase follows from this optional design boundary.

## Decisions, exceptions and retention

FOSS-only core is a governing constraint, not a waivable default in an adapter.
No agent makes an unknown/restricted material mandatory by signing its own
inventory. Use authorized role separation and independent review; material
scope/risk decisions retain AMD-002's reservations.

Quarantine disputed material and block affected claims/releases; preserve
license texts, notice digests, rejected decisions and affected artifact history.
Never remove an unfavorable license result or replace an accepted artifact
silently. Restricted source/evidence stays local with redacted shareable views.
Public release requires the separate full license audit and explicit release
authorization; current policy completion does not meet those later gates.

