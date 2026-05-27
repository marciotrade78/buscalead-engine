# Busca Lead Backend - Handoff

Este documento serve para retomar o projeto em outra maquina, especialmente na VPS Ubuntu da Hostinger.

## Objetivo do Projeto

O Busca Lead transforma dados publicos de empresas locais em oportunidades comerciais qualificadas. O backend Python e responsavel por buscar, enriquecer, analisar, priorizar e salvar leads. O Lovable permanece como front-end, autenticacao visual e exibicao.

Fluxo principal:

1. Usuario informa nicho e localizacao.
2. API Python busca empresas reais no Google Places.
3. API enriquece dados com Place Details.
4. Sistema identifica oportunidades comerciais.
5. Sistema gera score, diagnostico e recomendacoes.
6. Leads sao salvos no banco.
7. Lovable exibe leads, mapa, diagnostico e pipeline.

## Estado Atual

Ja existe:

- Estrutura FastAPI modular em `app/`.
- Providers Google Geocoding e Google Places funcionando.
- Endpoint de preview com busca real:
  - `POST /api/v1/leads/search/preview`
- Streamlit local de teste:
  - `tools/streamlit_app.py`
- Alembic configurado.
- Migration inicial para:
  - `leads`
  - `lead_analyses`
  - `pipeline_items`
- Autenticacao por:
  - JWT Supabase, ou
  - `x-lead-intelligence-key` para chamada server-side.
- Documentos:
  - `docs/architecture.md`
  - `docs/database.md`
  - `docs/integrations.md`
  - `docs/lovable-connection.md`

Validado nesta maquina:

- API sobe localmente.
- Healthcheck responde `200`.
- Google Geocoding funciona.
- Google Places Text Search funciona.
- Place Details funciona.
- Streamlit mostra resultados reais de busca.

## Importante Sobre Secrets

O arquivo `.env` local nao deve ser commitado nem copiado para repositorio publico.

Secrets usados:

```env
GOOGLE_PLACES_API_KEY=
LEAD_INTELLIGENCE_API_KEY=
DATABASE_URL=
REDIS_URL=
CELERY_BROKER_URL=
CELERY_RESULT_BACKEND=
SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=
SUPABASE_JWT_SECRET=
SUPABASE_JWT_ISSUER=
```

As chaves Google foram testadas localmente, mas como foram coladas em conversa, o ideal e rotacionar ou restringir no Google Cloud antes de producao.

## Como Retomar Na VPS Ubuntu

1. Conectar via SSH usando VS Code Remote SSH.
2. Copiar ou clonar o projeto para:

```text
/opt/busca-lead
```

3. Entrar no backend:

```bash
cd /opt/busca-lead/backend
```

4. Criar `.env` a partir do exemplo:

```bash
cp .env.example .env
```

5. Preencher secrets reais no `.env`.

6. Instalar dependencias:

```bash
python3.12 -m venv .venv
. .venv/bin/activate
pip install -e .
```

7. Rodar migrations:

```bash
alembic upgrade head
```

8. Subir API:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

9. Testar:

```bash
curl http://127.0.0.1:8000/api/v1/health
```

## Proximo Trabalho Tecnico

Prioridade recomendada:

1. Instalar PostgreSQL e Redis na VPS.
2. Configurar `DATABASE_URL` e aplicar Alembic.
3. Ativar persistencia real no endpoint definitivo.
4. Validar `POST /api/v1/leads/search`.
5. Validar Celery worker com Redis.
6. Implementar diagnostico inicial de lead.
7. Implementar Opportunity Score.
8. Publicar API com Nginx + HTTPS.
9. Conectar Lovable via Edge Function.

## Endpoints Atuais

```http
GET /api/v1
GET /api/v1/health
POST /api/v1/leads/search/preview
POST /api/v1/leads/search
GET /api/v1/leads
POST /api/v1/leads/{lead_id}/analyze
GET /api/v1/jobs/{job_id}
POST /api/v1/pipeline/move
```

## Teste De Busca

```bash
curl -X POST http://127.0.0.1:8000/api/v1/leads/search/preview \
  -H "Content-Type: application/json" \
  -H "x-lead-intelligence-key: $LEAD_INTELLIGENCE_API_KEY" \
  -d '{
    "niche": "dentistas",
    "location": "Curitiba",
    "radius_meters": 8000,
    "limit": 3
  }'
```

Resultado esperado:

```json
{
  "query": "dentistas em Curitiba",
  "location": "Curitiba",
  "total": 3,
  "leads": []
}
```

`leads` deve vir preenchido com empresas reais quando a chave Google estiver correta.

## Como Explicar Ao Codex Na VPS

Ao abrir o projeto na VPS, diga:

```text
Leia backend/docs/project-handoff.md, backend/docs/architecture.md,
backend/docs/database.md e backend/docs/lovable-connection.md.
Continue a partir do estado atual do Busca Lead Backend.
Prioridade: configurar PostgreSQL/Redis na VPS, aplicar migrations,
validar persistencia real e preparar a API para o Lovable.
```

## Regra De Arquitetura

Nao transformar o backend em apenas uma listagem de empresas. Toda funcionalidade deve ajudar o usuario a encontrar, entender, priorizar e converter leads comerciais.
