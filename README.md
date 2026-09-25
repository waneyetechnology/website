# Waneye Technology

**Waneye — global vision for smarter finance**

Waneye is a real-time financial news aggregation and market analysis platform. We provide real-time financial dashboard experiences, offering news, market data, and economic indicators.

## About

Visit our website at [www.waneye.com](https://www.waneye.com).

## Scheduled Docker deployments

`make deploy` mounts `../website-core`, copies it into the container, generates
the regional sites, and publishes the history and gh-pages branches. Run
`make build` after changing Docker scripts; `make deploy` uses the existing image.

All deploy targets use the container name `waneye-deploy`. Docker atomically
rejects a second run while that name exists, preventing overlapping cron jobs
and concurrent pushes. The rejected invocation exits nonzero and logs the name
conflict. `--rm` releases the name when the active container exits. Override
`CONTAINER_NAME` only for intentionally independent runs.

The image limits the whole workflow to 50 minutes. Set
`DEPLOY_TIMEOUT_SECONDS=3000` (a positive integer) in `.env.local` to adjust it.
At the deadline, the supervisor sends TERM to the workflow process group, then
KILL after 10 seconds if necessary. Timeout exits are nonzero (124, or 137 after
KILL), and `--init` forwards stop signals and reaps orphaned processes.

Rollout: review and merge the corresponding website-core browser-worker fix,
update the mounted core checkout, then rebuild this image with `make build`.
Previously started containers retain their old code and deadline behavior;
stop the confirmed stuck deployments separately. The name guard does not cover
old containers created with random names. The existing cron entry needs no change.
