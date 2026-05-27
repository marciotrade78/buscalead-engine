# Backend Architecture

## Responsabilidades

O backend e o motor principal do Busca Lead. Ele deve buscar empresas, enriquecer dados, analisar sinais comerciais, calcular prioridade e salvar tudo para o Lovable exibir.

O Lovable nao deve executar inteligencia de negocio pesada. Ele envia comandos, acompanha jobs e renderiza os dados persistidos.

## Camadas

- `api/routes`: contrato HTTP e validacao de entrada.
- `schemas`: modelos Pydantic de request/response.
- `services`: casos de uso, orquestracao e regras de aplicacao.
- `providers`: clientes externos, como Google Places, PageSpeed e scraping.
- `analyzers`: regras de diagnostico, SEO, keywords, score e competicao.
- `repositories`: leitura e escrita no PostgreSQL/Supabase.
- `jobs`: processamento assicrono e tarefas distribuidas.
- `cache`: Redis e politicas de TTL.
- `auth`: validacao JWT Supabase e contexto do usuario.
- `middleware`: request id, erros, rate limit e observabilidade.

## Fluxo interno de busca

1. `POST /leads/search` recebe nicho, localizacao, raio e limite.
2. Auth resolve `current_user`.
3. Rate limit valida quota por usuario.
4. Service cria job e retorna `202 Accepted`.
5. Worker executa geocoding, places search e place details.
6. Provider normaliza os dados externos.
7. Repository faz upsert e deduplicacao por `google_place_id`, telefone, site e nome/localizacao.
8. Resultado fica disponivel para o Lovable consultar.

## Fluxo interno de analise

1. `POST /leads/{lead_id}/analyze` enfileira o diagnostico.
2. Worker carrega lead e dados historicos.
3. Digital presence analyzer detecta sinais como sem site, apenas rede social e presenca fraca.
4. SEO analyzer coleta site, HTML, metadados, headings, indexabilidade e performance.
5. Keyword analyzer gera termos locais e explica a intencao em linguagem simples.
6. Competitive analyzer compara com negocios semelhantes da regiao.
7. Opportunity score consolida os sinais.
8. Repository salva diagnostico, score, problemas, acoes e argumento comercial.

## Padroes de projeto

- Rotas finas: endpoints nao devem conter regra de negocio.
- Services coordenam, mas nao conhecem detalhes de HTTP externo.
- Providers nao salvam no banco.
- Repositories nao chamam providers.
- Analyzers recebem dados normalizados e retornam resultados explicaveis.
- Jobs chamam services e devem ser idempotentes.
- Toda operacao multiusuario precisa filtrar por `user_id` ou `tenant_id`.

## Estrategia de erros

- Erros de validacao: `422`.
- Auth invalida: `401`.
- Sem permissao no recurso: `403`.
- Recurso inexistente: `404`.
- Rate limit: `429`.
- Provider externo indisponivel: retry com backoff; se falhar, job marcado como failed.

## Escalabilidade

- Cache agressivo para provider externo.
- Jobs longos fora da request HTTP.
- Workers separados por fila no futuro: `search`, `analysis`, `scraping`, `pagespeed`.
- Backpressure por usuario e por custo de provider.
- Tabelas preparadas para historico de analises e reprocessamento.

## Meta Intelligence futura

Meta Intelligence deve entrar como provider e job independentes, sem alterar o contrato principal de lead/diagnostico. O output deve virar mais um conjunto de sinais consumido pelo Opportunity Score.
