# Infrastructure Local Setup

## Services
- `postgres`: main local development DB (`localhost:5432`)
- `postgres_test`: disposable test DB (`localhost:5433`)

## Startup
```bash
docker compose -f infra/docker-compose.yml up -d
```

## Shutdown
```bash
docker compose -f infra/docker-compose.yml down
```

## Connection Defaults
- Username: `postgres`
- Password: `Yassine1@;`
- Main DB: `mt_facturation`
- Test DB: `mt_facturation_test`
