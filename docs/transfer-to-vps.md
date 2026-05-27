# Transfer To VPS

## Opção Recomendada: Git

Criar um repositorio Git privado e enviar o projeto sem `.env`.

```bash
git init
git add .
git commit -m "Initial Busca Lead backend"
git remote add origin <repo-privado>
git push -u origin main
```

Na VPS:

```bash
cd /opt
git clone <repo-privado> busca-lead
cd busca-lead/backend
cp .env.example .env
```

## Opção Alternativa: ZIP Sem Secrets

Antes de compactar, garantir que estes itens nao entrem:

```text
backend/.env
backend/.venv
backend/__pycache__
backend/app/**/__pycache__
```

No Windows, uma forma simples e criar um ZIP manual do projeto removendo `.env` e `.venv`.

Na VPS, descompactar em:

```text
/opt/busca-lead
```

## O Que Nao Transferir

Nao transferir para repositorio:

```text
backend/.env
backend/.venv
*.log
__pycache__/
```

## O Que Transferir

Transferir:

```text
backend/app/
backend/alembic/
backend/docs/
backend/tools/
backend/tests/
backend/pyproject.toml
backend/alembic.ini
backend/Dockerfile
backend/docker-compose.yml
backend/.env.example
backend/README.md
```
