# Busca Lead Backend

Backend Python independente para o motor de inteligencia comercial local do Busca Lead.

O Lovable deve permanecer responsavel por front-end, autenticacao visual e persistencia leve no Supabase. Este backend concentra busca, enriquecimento, analise, scoring, jobs e integracoes externas.

## Stack

- Python 3.12+
- FastAPI
- PostgreSQL/Supabase
- SQLAlchemy async
- Pydantic
- HTTPX
- Redis
- Celery
- Playwright
- BeautifulSoup
- PageSpeed/Lighthouse
- Docker

## Integracoes externas

| Provider | Secret | Responsabilidade no Busca Lead |
| --- | --- | --- |
| Google Places API | `GOOGLE_PLACES_API_KEY` | Busca e detalhes de estabelecimentos locais |
| Google Geocoding API | `GOOGLE_PLACES_API_KEY` | Converter cidade/endereco em latitude/longitude |
| PageSpeed/Lighthouse | `PAGESPEED_API_KEY` | Performance e sinais tecnicos do site |
| OpenAI/Gemini/Anthropic | `OPENAI_API_KEY`, `GEMINI_API_KEY`, `ANTHROPIC_API_KEY` | IA direta para diagnosticos e keywords |
| Mapbox | `MAPBOX_PUBLIC_TOKEN` | Renderizacao de mapa no Lovable/frontend |
| Redis | `REDIS_URL` | Cache e suporte a filas |

O Lovable AI Gateway nao deve ser migrado como dependencia do backend. No Python, chamadas de IA devem ir direto ao provedor escolhido, mantendo contrato estruturado em JSON.

## Fluxo principal

1. Lovable envia uma requisicao autenticada para a API Python.
2. A API resolve usuario/tenant, aplica rate limit e valida o payload.
3. Services coordenam providers externos, cache, repositories e analyzers.
4. Jobs longos rodam em Celery.
5. Resultados sao salvos no PostgreSQL/Supabase.
6. Lovable consulta e exibe os resultados.

## Execucao local

```bash
cp .env.example .env
docker compose up -d postgres redis
docker compose run --rm api alembic upgrade head
docker compose up --build api worker
```

API:

```text
http://localhost:8000/api/v1
```

Docs:

```text
http://localhost:8000/docs
```

Streamlit de teste:

```bash
docker compose up --build api streamlit
```

```text
http://localhost:8501
```

Esse painel e apenas uma ferramenta local para validar contratos da API. O produto final continua sendo exibido pelo Lovable.

Para testar sem um JWT Supabase, preencha `LEAD_INTELLIGENCE_API_KEY` no `.env` e informe o mesmo valor no campo lateral do Streamlit. Em producao, o Lovable deve usar esse header apenas em chamadas server-side/edge function, nunca exposto no navegador.

## Estrutura

```text
app/
  api/
    routes/          # Endpoints REST versionados
  auth/              # Estrategia JWT/Supabase e contexto de usuario
  cache/             # Redis e politicas de cache
  core/              # Configuracao, logging e seguranca
  db/                # Engine, sessoes e base ORM
  middleware/        # Rate limit, request id, erros
  providers/         # Google, PageSpeed, Playwright, scraping
  repositories/      # Acesso ao banco
  schemas/           # Contratos Pydantic
  services/          # Casos de uso e orquestracao
  analyzers/         # SEO, presenca digital, keywords, score
  jobs/              # Celery tasks
```

## Exemplos

Buscar leads:

```http
POST /api/v1/leads/search
Authorization: Bearer <supabase_jwt>
Content-Type: application/json

{
  "niche": "dentistas",
  "location": "Curitiba",
  "radius_meters": 8000,
  "limit": 20
}
```

Endpoints Google previstos:

- `https://maps.googleapis.com/maps/api/geocode/json`
- `https://maps.googleapis.com/maps/api/place/textsearch/json`
- `https://maps.googleapis.com/maps/api/place/details/json`

APIs obrigatorias no GCP:

- Places API
- Geocoding API

Resposta inicial:

```json
{
  "job_id": "0c7f4e34-5c83-4d75-b9c0-12c4f3d65a78",
  "status": "queued",
  "message": "Lead search queued"
}
```

Diagnostico de lead:

```http
POST /api/v1/leads/{lead_id}/analyze
Authorization: Bearer <supabase_jwt>
```

Resposta:

```json
{
  "job_id": "d3369aa7-1c91-4e57-8fcb-494b322f9f4a",
  "status": "queued",
  "message": "Lead analysis queued"
}
```

## Estrategia de autenticacao

- O front-end envia o JWT do Supabase no header `Authorization`.
- O backend valida assinatura, issuer, audience e expiracao.
- O `sub` vira `user_id`.
- Toda operacao de banco filtra por `tenant_id`/`user_id`.
- Service role do Supabase fica apenas no backend, nunca no cliente.

## Estrategia de cache

- Redis para respostas externas caras e repetitivas.
- Chaves separadas por provider, versao, nicho, localizacao e parametros.
- TTLs sugeridos:
  - Geocoding: 30 dias
  - Places search: 7 dias
  - Place details: 7 dias
  - PageSpeed/Lighthouse: 3 dias
  - SEO scrape: 3 dias
  - Keyword research: 14 dias
- Cache deve ser invalidado em refresh manual ou mudanca relevante do lead.

## Estrategia de filas

- Celery com Redis como broker/result backend inicialmente.
- Jobs idempotentes sempre que possivel.
- Tarefas longas:
  - busca Google Places paginada
  - enriquecimento Place Details
  - crawling/scraping de site
  - PageSpeed/Lighthouse
  - analise competitiva
  - diagnostico completo
- APIs retornam `job_id` e o front-end acompanha status.

## Estrategia de rate limiting

- Limite por usuario, IP e endpoint.
- Cotas separadas para:
  - busca de leads
  - analise completa
  - refresh de lead
  - endpoints leves de leitura
- Rate limit deve considerar custo do provider externo, nao apenas numero de requests.

## Roadmap tecnico

1. Fundacao: configurar app, settings, DB async, Redis, Celery, logging, request id e healthcheck.
2. Supabase Auth: validacao JWT, contexto de usuario e protecao de rotas.
3. Modelo de dados: users/tenants, leads, lead_sources, analyses, opportunities, pipeline_stages, jobs.
4. Google Providers: Geocoding, Places Search, Place Details, normalizacao e cache.
5. Lead Search: endpoint assincrono, job de busca, persistencia e deduplicacao.
6. Lead Refresh: atualizar dados do Place Details preservando historico.
7. Opportunity Engine: detectar sem site, rede social apenas, baixa avaliacao, poucas reviews e presenca fraca.
8. SEO Analyzer: scraping HTML, meta tags, headings, indexabilidade, performance e PageSpeed.
9. Keyword Research: termos locais, intencao comercial, dificuldade estimada e explicacao simples.
10. Opportunity Score: score ponderado, razoes transparentes e prioridade comercial.
11. Competitive Comparison: comparar empresas proximas do mesmo nicho/localizacao.
12. Digital Presence Diagnosis: diagnostico final com problemas, acoes recomendadas e argumento comercial.
13. Pipeline API: etapas, movimentacao, notas e proximas acoes.
14. Observabilidade: metricas, tracing, logs estruturados e dashboards.
15. Escala: workers distribuidos, politicas de retry, dead letter, backpressure e custos por usuario.
16. Meta Intelligence: preparar providers, schemas e jobs sem acoplar a implementacao inicial.
