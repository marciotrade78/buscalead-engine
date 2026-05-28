import os
import sys
import time
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import httpx  # noqa: E402
import streamlit as st  # noqa: E402

from app.core.config import settings  # noqa: E402


DEFAULT_API_URL = "http://localhost:8000/api/v1"
DEFAULT_USER_ID = "streamlit-petshop-test"


def api_url() -> str:
    return os.getenv("BACKEND_API_URL", DEFAULT_API_URL).rstrip("/")


def auth_headers(token: str, intelligence_key: str, user_id: str) -> dict[str, str]:
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    key = intelligence_key or settings.lead_intelligence_api_key
    if key:
        headers["x-lead-intelligence-key"] = key
        headers["x-lead-user-id"] = user_id
        headers["x-lead-tenant-id"] = user_id
        headers["x-lead-user-email"] = f"{user_id}@local.test"
    return headers


def post_json(path: str, payload: dict[str, Any] | None, headers: dict[str, str]) -> httpx.Response:
    with httpx.Client(timeout=60) as client:
        return client.post(f"{api_url()}{path}", json=payload, headers=headers)


def get_json(path: str, headers: dict[str, str]) -> httpx.Response:
    with httpx.Client(timeout=60) as client:
        return client.get(f"{api_url()}{path}", headers=headers)


def response_json(response: httpx.Response) -> dict[str, Any] | list[Any] | str:
    try:
        return response.json()
    except ValueError:
        return response.text


def poll_job(job_id: str, headers: dict[str, str], label: str, timeout_seconds: int = 120) -> dict[str, Any]:
    deadline = time.time() + timeout_seconds
    progress = st.progress(0, text=f"{label}: aguardando...")
    last_payload: dict[str, Any] = {}

    while time.time() < deadline:
        response = get_json(f"/jobs/{job_id}", headers)
        payload = response_json(response)
        if not isinstance(payload, dict):
            return {"status": "failed", "error": payload}

        last_payload = payload
        status = payload.get("status", "unknown")
        progress.progress(50 if status in {"queued", "started"} else 100, text=f"{label}: {status}")

        if status in {"completed", "failed"}:
            return payload
        time.sleep(2)

    return {"status": "timeout", "error": "Tempo limite ao aguardar o job", "last_payload": last_payload}


def as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if value in (None, ""):
        return []
    return [value]


def priority_from_score(score: float | int | None, priority: str | None) -> tuple[str, str]:
    if priority:
        labels = {
            "high": "Alta",
            "medium": "Media",
            "low": "Baixa",
        }
        label = labels.get(priority.lower(), priority.title())
    elif score is None:
        label = "Indefinida"
    elif score >= 70:
        label = "Alta"
    elif score >= 35:
        label = "Media"
    else:
        label = "Baixa"

    if label == "Alta":
        conclusion = "Lead com boa oportunidade comercial. Vale priorizar uma abordagem consultiva."
    elif label == "Media":
        conclusion = "Lead com sinais mistos. Vale abordar se houver capacidade de prospeccao."
    elif label == "Baixa":
        conclusion = "Lead com menor urgencia aparente. Melhor usar como teste ou abordagem leve."
    else:
        conclusion = "Ainda nao ha sinais suficientes para definir prioridade."
    return label, conclusion


def render_bullets(title: str, items: list[Any], empty_text: str) -> None:
    st.markdown(f"**{title}**")
    if not items:
        st.caption(empty_text)
        return
    for item in items[:6]:
        if isinstance(item, dict):
            label = item.get("label") or item.get("type") or "Sinal"
            insight = item.get("insight") or item.get("reason") or item
            st.write(f"- {label}: {insight}")
        else:
            st.write(f"- {item}")


def render_analysis_summary(analysis: dict[str, Any]) -> None:
    diagnosis = analysis.get("diagnosis") or {}
    lead = diagnosis.get("lead") or {}
    opportunity = diagnosis.get("opportunity") or {}
    digital = diagnosis.get("digital_presence") or {}
    seo = diagnosis.get("seo") or {}
    competitive = diagnosis.get("competitive") or {}
    meta = diagnosis.get("meta_intelligence") or {}
    ai = diagnosis.get("ai_insights") or {}

    score = analysis.get("opportunity_score") or opportunity.get("score")
    priority, conclusion = priority_from_score(score, opportunity.get("priority"))

    st.success(conclusion)

    metric_a, metric_b, metric_c, metric_d = st.columns(4)
    metric_a.metric("Prioridade", priority)
    metric_b.metric("Score", "-" if score is None else f"{score}/100")
    metric_c.metric("Presenca", digital.get("presence_level", "-"))
    metric_d.metric("IA", ai.get("provider", ai.get("status", "-")))

    st.subheader("Resumo do lead")
    lead_name = lead.get("name") or "Lead"
    lead_phone = lead.get("phone") or "telefone nao informado"
    lead_rating = lead.get("rating", "-")
    lead_reviews = lead.get("review_count", "-")
    st.write(f"**{lead_name}** | {lead_phone} | Nota {lead_rating} com {lead_reviews} avaliacoes")
    if diagnosis.get("summary"):
        st.info(diagnosis["summary"])
    if ai.get("summary"):
        st.write(ai["summary"])

    st.subheader("O que usar na abordagem")
    col_left, col_right = st.columns(2)
    with col_left:
        render_bullets("Problemas encontrados", as_list(digital.get("issues")) + as_list(seo.get("issues")), "Nenhum problema forte encontrado.")
        render_bullets("Oportunidades", as_list(seo.get("opportunities")) + as_list(competitive.get("opportunities")), "Nenhuma oportunidade clara encontrada.")
    with col_right:
        render_bullets("Pontos fortes", as_list(digital.get("strengths")) + as_list(competitive.get("advantages")), "Poucos pontos fortes detectados.")
        render_bullets("Ganchos de venda", as_list(meta.get("conversion_hooks")), "Sem gancho especifico gerado.")

    if ai.get("sales_angle") or ai.get("recommended_pitch"):
        st.subheader("Argumento comercial sugerido")
        if ai.get("sales_angle"):
            st.write(ai["sales_angle"])
        if ai.get("recommended_pitch"):
            st.info(ai["recommended_pitch"])

    if ai.get("whatsapp_message"):
        st.subheader("Mensagem pronta para WhatsApp")
        st.code(ai["whatsapp_message"], language="text")

    next_actions = as_list(ai.get("next_best_actions")) or as_list(digital.get("recommended_actions"))
    render_bullets("Proximas acoes", next_actions, "Nenhuma proxima acao gerada.")

    if ai.get("objection_handling"):
        with st.expander("Como responder objecao"):
            st.write(ai["objection_handling"])


def render_lead_card(lead: dict[str, Any], headers: dict[str, str]) -> None:
    title = lead.get("name") or "Lead sem nome"
    with st.container(border=True):
        col_info, col_action = st.columns([3, 1])
        with col_info:
            st.subheader(title)
            st.write(lead.get("address") or "Endereco nao informado")
            st.caption(
                f"Nota: {lead.get('rating', '-')} | Avaliacoes: {lead.get('review_count', '-')} | "
                f"Telefone: {lead.get('phone') or '-'}"
            )
            if lead.get("website"):
                st.link_button("Abrir site", lead["website"])
        with col_action:
            lead_id = lead.get("id")
            if st.button("Analisar", key=f"analyze-{lead_id}", type="primary", use_container_width=True):
                analyze_response = post_json(f"/leads/{lead_id}/analyze", None, headers)
                accepted = response_json(analyze_response)
                st.write("Status da solicitacao:", analyze_response.status_code)
                with st.expander("Resposta da solicitacao"):
                    st.json(accepted)

                if isinstance(accepted, dict) and accepted.get("job_id"):
                    job_payload = poll_job(accepted["job_id"], headers, "Analise")

                    if job_payload.get("status") == "completed":
                        analysis_response = get_json(f"/leads/{lead_id}/analysis", headers)
                        analysis_payload = response_json(analysis_response)
                        if isinstance(analysis_payload, dict):
                            render_analysis_summary(analysis_payload)
                        with st.expander("JSON completo da analise"):
                            st.json(analysis_payload)
                    else:
                        st.error("A analise nao terminou com sucesso.")
                        st.json(job_payload)


st.set_page_config(page_title="Teste Petshop Curitiba", layout="wide")

st.title("Teste de busca e analise: petshops em Curitiba")
st.caption("Valida o backend direto pelo Streamlit, sem passar pelo Lovable.")

with st.sidebar:
    st.header("Conexao")
    st.text_input("Backend API URL", value=api_url(), disabled=True)
    user_id = st.text_input("Usuario de teste", value=DEFAULT_USER_ID)
    supabase_token = st.text_input("Supabase JWT", type="password")
    intelligence_key = st.text_input(
        "Lead Intelligence API Key",
        type="password",
        help="Se deixar vazio, usa o valor do .env da VPS.",
    )

headers = auth_headers(supabase_token.strip(), intelligence_key.strip(), user_id.strip() or DEFAULT_USER_ID)

with st.expander("Headers usados no teste", expanded=False):
    safe_headers = {key: ("***" if "key" in key.lower() or key.lower() == "authorization" else value) for key, value in headers.items()}
    st.json(safe_headers)

col_a, col_b, col_c, col_d = st.columns(4)
with col_a:
    niche = st.text_input("Nicho", value="petshop")
with col_b:
    location = st.text_input("Cidade", value="Curitiba")
with col_c:
    radius_meters = st.number_input("Raio em metros", min_value=100, max_value=50000, value=8000)
with col_d:
    limit = st.number_input("Limite", min_value=1, max_value=20, value=5)

payload = {
    "niche": niche,
    "location": location,
    "radius_meters": int(radius_meters),
    "limit": int(limit),
}

st.code(payload, language="json")

search_col, list_col = st.columns(2)
with search_col:
    run_search = st.button("Buscar petshops em Curitiba", type="primary", use_container_width=True)
with list_col:
    load_saved = st.button("Carregar leads salvos", use_container_width=True)

if run_search:
    response = post_json("/leads/search", payload, headers)
    accepted = response_json(response)
    st.write("Status da busca:", response.status_code)
    with st.expander("Resposta da solicitacao de busca"):
        st.json(accepted)

    if isinstance(accepted, dict) and accepted.get("job_id"):
        job_payload = poll_job(accepted["job_id"], headers, "Busca")
        with st.expander("JSON do job de busca"):
            st.json(job_payload)

        leads = []
        if job_payload.get("status") == "completed":
            result = job_payload.get("result") or {}
            leads = result.get("leads") or []
            st.session_state["latest_petshop_leads"] = leads
            st.success(f"Busca concluida: {len(leads)} leads encontrados.")
            if leads:
                st.dataframe(leads, use_container_width=True)

if load_saved:
    response = get_json("/leads", headers)
    data = response_json(response)
    st.write("Status da listagem:", response.status_code)
    st.json(data)
    if isinstance(data, list):
        st.session_state["latest_petshop_leads"] = data

leads = st.session_state.get("latest_petshop_leads", [])
if leads:
    st.divider()
    st.header("Leads encontrados")
    for lead in leads:
        render_lead_card(lead, headers)
else:
    st.info("Clique em buscar para encontrar petshops em Curitiba. Depois use o botao Analisar em um lead.")
