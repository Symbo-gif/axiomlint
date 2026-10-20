# Local generated artifacts

Local check runs go under `gates/<run-id>/`. Raw logs are preserved with SHA-256
digests and a run manifest. They are ignored by Git and must be deliberately
reviewed and exported before long-term acceptance; ignored storage alone is not
permanent retention. Accepted evidence is copied to governance/evidence or a
maintainer-approved append-only archive, never silently rewritten.

