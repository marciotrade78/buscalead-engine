# Lovable Connection

Este documento descreve como o Lovable deve conversar com o backend Python.

## Variaveis no Lovable

```env
LEAD_INTELLIGENCE_URL=https://<backend-python>
LEAD_INTELLIGENCE_API_KEY=<mesmo valor configurado no backend>
CORS_ALLOWED_ORIGINS=https://<seu-app-lovable>
ALLOW_DEV_AUTH_FALLBACK=false
```

`LEAD_INTELLIGENCE_API_KEY` deve ser usado apenas em Edge Functions/server-side. Nao exponha esse segredo em componentes React.

Em producao, mantenha `ALLOW_DEV_AUTH_FALLBACK=false` para bloquear chamadas sem JWT Supabase ou sem `x-lead-intelligence-key`. Preencha `CORS_ALLOWED_ORIGINS` com o dominio do Lovable quando chamadas diretas do navegador forem necessarias; chamadas por Edge Function geralmente nao dependem de CORS.

## Busca de leads

Lovable Edge Function:

```http
POST ${LEAD_INTELLIGENCE_URL}/api/v1/leads/search
x-lead-intelligence-key: ${LEAD_INTELLIGENCE_API_KEY}
Content-Type: application/json

{
  "niche": "dentistas",
  "location": "Curitiba",
  "radius_meters": 8000,
  "limit": 20
}
```

Esse endpoint enfileira o processamento. Para testes locais com Streamlit, use `/api/v1/leads/search/preview`.

Resposta:

```json
{
  "job_id": "celery-task-id",
  "status": "queued",
  "message": "Lead search queued"
}
```

## Status do job

```http
GET ${LEAD_INTELLIGENCE_URL}/api/v1/jobs/{job_id}
x-lead-intelligence-key: ${LEAD_INTELLIGENCE_API_KEY}
```

## Listar leads salvos

```http
GET ${LEAD_INTELLIGENCE_URL}/api/v1/leads
x-lead-intelligence-key: ${LEAD_INTELLIGENCE_API_KEY}
```

## Fluxo recomendado no Lovable

1. Usuario informa nicho e localizacao no Lovable.
2. Lovable chama uma Edge Function propria.
3. A Edge Function chama o backend Python com `x-lead-intelligence-key`.
4. Backend Python busca no Google, salva no Postgres/Supabase e retorna `job_id`.
5. Lovable consulta `/api/v1/jobs/{job_id}` ate finalizar.
6. Lovable lista os leads salvos e renderiza mapa/cards/pipeline.

## Campos retornados por lead

```json
{
  "id": "uuid",
  "google_place_id": "ChIJ...",
  "name": "Clinica Exemplo",
  "address": "Rua Exemplo, 123 - Curitiba",
  "phone": "(41) 99999-9999",
  "website": "https://exemplo.com.br",
  "rating": 4.6,
  "review_count": 82,
  "category": "dentist",
  "latitude": -25.4284,
  "longitude": -49.2733
}
```

## Teste local sincronizado

Para o painel Streamlit ou depuracao local:

```http
POST ${LEAD_INTELLIGENCE_URL}/api/v1/leads/search/preview
x-lead-intelligence-key: ${LEAD_INTELLIGENCE_API_KEY}
Content-Type: application/json
```

Esse endpoint executa a busca imediatamente, salva os leads e retorna a lista. Ele e util para validar Google Places antes de depender do worker Celery.
