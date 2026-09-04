# ADR-0003: Generated bundles are committed, not gitignored

**Status:** Accepted — 2026-09-04

## Context

Standard practice is to gitignore build output. But this repository's stated
promise is "bundles ready to upload" — the audience includes data governance
people who want to drop a CSV into OpenMetadata or open a `.ttl` in Protégé, and
who have no interest in cloning a repo, installing Python and running a build.

## Decision

`build/` is committed. A CI job regenerates it on every PR and fails if the
result differs from what is checked in.

## Consequences

- Anyone can download a bundle straight from GitHub, or point Knowledge Catalog
  at a raw URL, with no toolchain.
- Diffs are noisier. Reviewers read `src/` and treat `build/` as derived.
- Generated output can drift if someone bypasses CI. The sync check is therefore
  not optional.
- A `.gitattributes` marking `build/` as `linguist-generated` keeps GitHub's
  language stats and diff view honest. *(TODO)*
