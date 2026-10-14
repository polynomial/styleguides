# Diagnosing credentials without exposing them

The always-on gate is [`production-safety`](../../.agents/rules/production-safety.mdc).

## Identify and compare

- Compare by `sha256(value)[:16]` plus length plus the first ~4 characters. That proves "same" or
  "different" and identifies the type: a vendor's service-account tokens share a prefix and a
  length, and a legacy API key of the same vendor another. Publish the hash, never the value.
- **Historical ReplicaSets keep their pod template.** Hash one env var across generations to date a
  credential change exactly:
  ```bash
  kubectl -n <ns> get rs -l app=<app> \
    -o custom-columns='NAME:.metadata.name,CREATED:.metadata.creationTimestamp,REVISION:.metadata.annotations.deployment\.kubernetes\.io/revision'
  ```
- Decode only non-secret identity fields. A legacy key that decodes to `{"k","n","id"}`: print
  `n` and `id`, never `k`.
- Fetch a Deployment with plain-value secrets to a file and extract only the derived facts, rather
  than reading it into context.

## Prove function

- Replay the failing request with the deployed credential and with a known-good one, against the
  same endpoint, query and datasource. Report status codes only.
- Probe several endpoints. A 401 everywhere means the credential is invalid; a mix of 200 and 403
  means insufficient scope.

## Before changing a shared secret

List every workflow that injects it and check how each consumer actually authenticates. A pipeline
that "succeeds daily" may authenticate from a committed default instead of the secret.

## A leak found along the way

Report the file and commit, and whether the credential is still live (test read-only). Recommend
rotation, and never paste the value. Source incident: an autoscaler silently disabled for weeks by
a wrong metrics credential, found on 2026-08-08.
