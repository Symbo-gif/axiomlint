# Environment scaffolding and deferred locks

Current runnable environment: Python >=3.12 standard library and Git on the
user's laptop. No environment is installed or changed by the scaffold.

WP-004 must add an approved, licensed, pinned tool manifest and lockfile,
`flake.nix` plus actual `flake.lock`, and a rootless OCI recipe using an image
digest, before claiming reproducible development environments. Deliberately no
fake uv.lock, empty Nix lock, unpinned latest image or untested “secure” container
is supplied. Dependency-free runtime does not mean pinned Python/OS/build tooling.

The design files under this directory are input contracts, not runnable builds.
Fresh Linux checkout, Windows support, reproducible package build/install,
coverage/lint/type tools and container enforcement are separate deferred checks.

