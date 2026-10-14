# Production changes: infrastructure-as-code, destructive tests, config fixes

The always-on gate is [`production-safety`](../../.agents/rules/production-safety.mdc). This page
holds the procedure behind it.

## Infrastructure-as-code on a shared production state

Run this for any `terraform apply` against a state with several owners, and especially in repos
with no CI apply path.

```bash
# 1. SEE the drift. If it shows change/destroy you did not author, STOP.
terraform plan -input=false [-var feature=true]            # N add, M change, K destroy

# 2. Scoped plan: only your resources. It must be additive-only.
terraform plan -input=false [-var feature=true] \
  -target=module.my_feature -target=aws_x.my_feature \
  -out=feature.tfplan                                      # N add, 0 change, 0 destroy

# 3. Apply exactly the reviewed plan, output streamed in full.
terraform apply -input=false feature.tfplan

# 4. Remove the secret-bearing plan file.
rm -f feature.tfplan
```

- If a scoped plan still shows a change, a shared dependency is dragging it in. Give your component
  a dedicated copy (subnet group, parameter group, security group) and follow the nearest
  per-component precedent. One database change needed its own subnet group for this reason.
- Scoped teardown uses the same `-target` set. A plain apply with the feature disabled sweeps the
  drift back in.
- **Secrets:** source them into `TF_VAR_<name>` by command substitution and check only the length
  (`echo "len=${#TF_VAR_password}"`). Use an obvious placeholder for read-only plans. Never commit
  a `*.tfplan`, because plan files store variable values in the clear.
- **Repos with no CI apply path** may apply manually from a branch only when the additive-only
  gate passes, the user gives an explicit go, and the saved plan is recorded in an investigation
  doc. Where a CI apply path exists, dispatch it instead.

## Destructive tests

1. Replace the component while its data survives.
2. Confirm it serves: reach the port and run the health command. `running` is not proof.
3. Only then discard data, with the recovery command already tested.

List what survives before you say "nuke it":
- A separately managed volume re-attaches to a replacement instance.
- Cursors held in a database outlive a broker wipe.
- In-flight records and consumer-group offsets held only in the broker do not.

For machine images selected by `most_recent = true`, "it booted last month" is no evidence. One
2026-07-27 broker rebuild failed exactly this way.

## Verifying a config fix

A queue or backlog between the setting and the harm means a correct fix can leave the incident at
full severity for hours.

1. Read the setting back from the authoritative API.
2. Count the harmful work per short interval, and look for a tail-off.
3. With no tail-off, measure consumer lag in event time, `now() - max(written_timestamp)`. State the
   recovery gate as "when the watermark passes <fix time>".
4. Report the setting and each harm separately, with the clock each one recovers on.
