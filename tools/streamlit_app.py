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
                st.json(accepted)

                if isinstance(accepted, dict) and accepted.get("job_id"):
                    job_payload = poll_job(accepted["job_id"], headers, "Analise")
                    st.write("Resultado do job")
                    st.json(job_payload)

                    if job_payload.get("status") == "completed":
                        analysis_response = get_json(f"/leads/{lead_id}/analysis", headers)
                        st.write("Analise persistida")
                        st.json(response_json(analysis_response))


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
    st.json(accepted)

    if isinstance(accepted, dict) and accepted.get("job_id"):
        job_payload = poll_job(accepted["job_id"], headers, "Busca")
        st.write("Resultado do job")
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
