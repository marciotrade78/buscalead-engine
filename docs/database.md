# Database Setup

O backend usa PostgreSQL em todos os ambientes.

## Desenvolvimento local

Use o Postgres do Docker Compose:

```bash
cd backend
cp .env.example .env
docker compose up -d postgres redis
docker compose run --rm api alembic upgrade head
docker compose up --build api worker streamlit
```

Se preferir rodar fora do Docker depois de instalar dependencias:

```bash
.venv\Scripts\python -m alembic upgrade head
.venv\Scripts\python -m uvicorn app.main:app --reload
.venv\Scripts\streamlit run tools/streamlit_app.py
```

Dentro do Docker, use:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/busca_lead
REDIS_URL=redis://redis:6379/0
```

Rodando a API fora do Docker, use:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/busca_lead
REDIS_URL=redis://localhost:6379/0
```

## Supabase remoto

Para producao ou staging, use a connection string do Supabase:

```env
DATABASE_URL=postgresql+asyncpg://postgres:<SENHA>@db.ogjccrzbygzvxzayayzu.supabase.co:5432/postgres?ssl=require
```

Se a string recebida vier como `postgresql://...?...sslmode=require`, converta para:

```text
postgresql+asyncpg://...?...ssl=require
```

O Alembic troca internamente `+asyncpg` por `+psycopg` para rodar migrations.

## Secrets

Podem ficar no `.env` local:

```env
SUPABASE_URL=https://ogjccrzbygzvxzayayzu.supabase.co
SUPABASE_ANON_KEY=...
SUPABASE_SERVICE_ROLE_KEY=...
SUPABASE_JWT_ISSUER=https://ogjccrzbygzvxzayayzu.supabase.co/auth/v1
SUPABASE_JWT_SECRET=...
GOOGLE_PLACES_API_KEY=...
```

Nao commitar `.env`. O arquivo ja esta ignorado pelo `.gitignore`.
