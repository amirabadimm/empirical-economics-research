# Deployment

This directory versions the infrastructure definition used by the research server while keeping runtime secrets and state outside Git.

## What is versioned

- PostgreSQL 17 service definition;
- Python utility container definition;
- Docker network and persistent-volume names;
- required environment-variable names.

## What stays outside Git

- the real `.env` file and database password;
- PostgreSQL volume contents;
- collected raw market data and source snapshots;
- logs and runtime caches;
- machine-specific SSH configuration.

## Server use

Copy `deployment/.env.example` to a private runtime location and replace placeholder values. Do not commit the resulting file.

A deployment host can then run:

```bash
docker compose \
  --env-file /opt/investment-dashboard/.env \
  -f /opt/empirical-economics-research/deployment/docker-compose.yml \
  up -d
```

The Compose project name is fixed as `investment-dashboard`, preserving the existing container, network, and volume naming convention. `APP_DIR` defaults to `/opt/investment-dashboard/app` and can be overridden in the private environment file.

The gold research database schema and loading workflow are documented in [`../commodity/gold/db/README.md`](../commodity/gold/db/README.md). Database credentials are consumed from the environment and must never appear in commands, committed configuration, or documentation.
