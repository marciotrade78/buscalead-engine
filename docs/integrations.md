# External Integrations

## Google Maps Platform

Secret:

```text
GOOGLE_PLACES_API_KEY
```

APIs obrigatorias no Google Cloud:

- Places API
- Geocoding API

Endpoints:

| Endpoint | Funcao | Uso |
| --- | --- | --- |
| `https://maps.googleapis.com/maps/api/place/textsearch/json` | Busca empresas por nicho, cidade e raio | `search-places` |
| `https://maps.googleapis.com/maps/api/place/details/json` | Detalhes do Place ID | `search-places`, `refresh-place` |
| `https://maps.googleapis.com/maps/api/geocode/json` | Converte cidade/endereco em lat/lng | `search-places` |

O backend deve cachear agressivamente geocoding, text search e details para controlar custo.

## Mapbox

Secret:

```text
MAPBOX_PUBLIC_TOKEN
```

Uso principal:

- Renderizacao do mapa no Lovable/frontend via `mapbox-gl`.

Nao ha necessidade de chamada server-side para a primeira versao. O token e publico e pode continuar sendo entregue ao front-end pela edge function atual ou por configuracao do Lovable.

## IA

O Lovable AI Gateway atual nao deve ser tratado como provider principal do backend Python.

No backend, usar chamada direta ao provedor escolhido:

- OpenAI: `OPENAI_API_KEY`
- Google Gemini: `GEMINI_API_KEY`
- Anthropic: `ANTHROPIC_API_KEY`

O contrato interno deve ser JSON estruturado, compativel com diagnostico, keyword research e argumentos comerciais.

## Google Suggest

Endpoint publico atual:

```text
https://suggestqueries.google.com/complete/search?client=firefox&q=...&hl=pt-BR
```

Uso:

- Sugestoes de palavras-chave e intencao inicial.

Risco:

- Endpoint nao oficial e sem SLA.

Alternativas recomendadas:

- Google Ads API / Keyword Planner
- SEMrush API
- DataForSEO
- Serper.dev

## Lead Intelligence Engine

Secrets previstos para o Lovable chamar este backend:

```text
LEAD_INTELLIGENCE_URL
LEAD_INTELLIGENCE_API_KEY
```

Contrato esperado:

- Lovable envia requisicoes autenticadas para a API Python.
- Python processa, salva no Supabase/PostgreSQL e retorna `job_id` ou resultado.
- Lovable exibe dados persistidos.

Headers aceitos pelo backend:

```http
Authorization: Bearer <supabase_jwt>
```

ou, para chamadas server-side entre Lovable Edge Function e Python:

```http
x-lead-intelligence-key: <LEAD_INTELLIGENCE_API_KEY>
```

O `LEAD_INTELLIGENCE_API_KEY` nao deve ser usado diretamente em componentes React/browser.
