# Registry config

This folder builds registry configs and a docker-compose file from a combined config.

## Requirements

- Python 3
- `pip install -r requirements.txt`

## Build

- Build all (configs + registry dirs): `make`
- Build one config: `make config/ghcr.yml`
- Build registry dirs only: `make registries`
- Render compose: `make compose`

Sources:

- Combined config: `config.yml`
- Compose template: `docker-compose.yml.j2`

Generated outputs are `config/*.yml` files and `docker-compose.yml`.
Registry directories are created under `web-public/registries/<name>` based on the last N parts of each `remoteurl` host (default N=2). Override with `DOMAIN_PARTS=3`.
