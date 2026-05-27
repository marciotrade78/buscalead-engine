# VPS Ubuntu Checklist

Checklist para preparar a VPS Hostinger com Ubuntu.

## Sistema

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y git curl build-essential python3.12 python3.12-venv python3-pip
```

## PostgreSQL

```bash
sudo apt install -y postgresql postgresql-contrib
sudo -u postgres psql
```

Dentro do `psql`:

```sql
CREATE DATABASE busca_lead;
CREATE USER busca_lead_user WITH PASSWORD 'trocar_senha';
GRANT ALL PRIVILEGES ON DATABASE busca_lead TO busca_lead_user;
\q
```

`DATABASE_URL`:

```env
DATABASE_URL=postgresql+asyncpg://busca_lead_user:trocar_senha@localhost:5432/busca_lead
```

## Redis

```bash
sudo apt install -y redis-server
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

Variaveis:

```env
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2
```

## Backend

```bash
sudo mkdir -p /opt/busca-lead
sudo chown -R $USER:$USER /opt/busca-lead
cd /opt/busca-lead
```

Copiar/clonar o projeto e depois:

```bash
cd backend
cp .env.example .env
python3.12 -m venv .venv
. .venv/bin/activate
pip install -e .
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Services Systemd

Criar depois:

- `busca-lead-api.service`
- `busca-lead-worker.service`

## Nginx + HTTPS

Depois que a API responder localmente:

```bash
sudo apt install -y nginx certbot python3-certbot-nginx
```

Configurar dominio, exemplo:

```text
api.seudominio.com -> IP da VPS
```

Depois:

```bash
sudo certbot --nginx -d api.seudominio.com
```

## Lovable

Secrets no Lovable:

```env
LEAD_INTELLIGENCE_URL=https://api.seudominio.com
LEAD_INTELLIGENCE_API_KEY=<mesma chave do backend>
```

O Lovable deve chamar o backend via Edge Function, nunca diretamente do React com segredo exposto.
