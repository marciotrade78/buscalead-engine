import os
from typing import Any

import httpx
import streamlit as st

from app.core.config import settings


DEFAULT_API_URL = "http://localhost:8000/api/v1"


def api_url() -> str:
    return os.getenv("BACKEND_API_URL", DEFAULT_API_URL).rstrip("/")


def auth_headers(token: str, intelligence_key: str) -> dict[str, str]:
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    key = intelligence_key or settings.lead_intelligence_api_key
    if key:
        headers["x-lead-intelligence-key"] = key
    return headers


def post_json(path: str, payload: dict[str, Any] | None, headers: dict[str, str]) -> httpx.Response:
    with httpx.Client(timeout=30) as client:
        return client.post(f"{api_url()}{path}", json=payload, headers=headers)


def get_json(path: str, headers: dict[str, str]) -> httpx.Response:
    with httpx.Client(timeout=30) as client:
        return client.get(f"{api_url()}{path}", headers=headers)


st.set_page_config(page_title="Busca Lead API Tester", layout="wide")

st.title("Busca Lead API Tester")
st.caption("Ferramenta local para validar o backend Python. Nao substitui o Lovable.")

with st.sidebar:
    st.header("Conexao")
    st.text_input("Backend API URL", value=api_url(), disabled=True)
    supabase_token = st.text_input("Supabase JWT", type="password")
    intelligence_key = st.text_input(
        "Lead Intelligence API Key",
        type="password",
        help="Opcional em ambiente local: se vazio, usa o valor do .env.",
    )

headers = auth_headers(supabase_token.strip(), intelligence_key.strip())

tab_search, tab_saved, tab_analyze, tab_jobs = st.tabs(
    ["Buscar leads", "Leads salvos", "Analisar lead", "Jobs"]
)

with tab_search:
    st.subheader("Busca por nicho e localizacao")

    col_a, col_b = st.columns(2)
    with col_a:
        niche = st.text_input("Nicho", value="dentistas")
        radius_meters = st.number_input("Raio em metros", min_value=100, max_value=50000, value=8000)
    with col_b:
        location = st.text_input("Localizacao", value="Curitiba")
        limit = st.number_input("Limite", min_value=1, max_value=60, value=20)

    payload = {
        "niche": niche,
        "location": location,
        "radius_meters": int(radius_meters),
        "limit": int(limit),
    }

    st.code(payload, language="json")

    col_send, col_queue = st.columns(2)

    with col_send:
        run_preview = st.button("Buscar agora", type="primary")
    with col_queue:
        run_queue = st.button("Enfileirar busca")

    if run_preview:
        response = post_json("/leads/search/preview", payload, headers)
        st.write("Status:", response.status_code)
        try:
            data = response.json()
            st.json(data)
            leads = data.get("leads", [])
            if leads:
                st.dataframe(leads, use_container_width=True)
        except ValueError:
            st.text(response.text)

    if run_queue:
        response = post_json("/leads/search", payload, headers)
        st.write("Status:", response.status_code)
        try:
            st.json(response.json())
        except ValueError:
            st.text(response.text)

with tab_saved:
    st.subheader("Leads persistidos")

    if st.button("Carregar leads salvos"):
        response = get_json("/leads", headers)
        st.write("Status:", response.status_code)
        try:
            data = response.json()
            st.json(data)
            if data:
                st.dataframe(data, use_container_width=True)
        except ValueError:
            st.text(response.text)

with tab_analyze:
    st.subheader("Enfileirar diagnostico de lead")
    lead_id = st.text_input("Lead ID")

    if st.button("Analisar lead"):
        response = post_json(f"/leads/{lead_id}/analyze", None, headers)
        st.write("Status:", response.status_code)
        try:
            st.json(response.json())
        except ValueError:
            st.text(response.text)

with tab_jobs:
    st.subheader("Consultar status de job")
    job_id = st.text_input("Job ID")

    if st.button("Consultar job"):
        response = get_json(f"/jobs/{job_id}", headers)
        st.write("Status:", response.status_code)
        try:
            st.json(response.json())
        except ValueError:
            st.text(response.text)
