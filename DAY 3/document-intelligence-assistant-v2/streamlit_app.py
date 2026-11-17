"""Streamlit UI.  Run:  streamlit run streamlit_app.py   (backend must be running)"""
import requests
import streamlit as st

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Document Intelligence Assistant", page_icon="📄")
st.title("📄 Document Intelligence Assistant")

# ---------------- Sidebar ----------------
with st.sidebar:
    st.header("Upload PDFs")
    files = st.file_uploader("Choose PDF files", type="pdf", accept_multiple_files=True)
    if st.button("Ingest", disabled=not files):
        for f in files:
            with st.spinner(f"Ingesting {f.name}..."):
                try:
                    r = requests.post(f"{API_URL}/ingest",
                                      files={"file": (f.name, f.getvalue(), "application/pdf")},
                                      timeout=600)
                    if r.ok:
                        d = r.json()
                        st.success(f"{f.name}: {d['pages']} pages, {d['chunks']} chunks")
                    else:
                        st.error(f"{f.name}: {r.json().get('detail', r.text)}")
                except requests.exceptions.ConnectionError:
                    st.error("Backend not running. Start uvicorn first.")

    st.divider()
    st.header("Status")
    try:
        h = requests.get(f"{API_URL}/health", timeout=3).json()
        st.write(f"Backend: ✅  |  Ollama: {'✅' if h['ollama'] else '❌'}")
        st.caption(f"Chunks stored: {h['chunks_stored']} · top_k={h['settings']['top_k']} · "
                   f"chunk={h['settings']['chunk_size']}")
        m = requests.get(f"{API_URL}/metrics", timeout=3).json()
        if m.get("requests"):
            st.caption(f"Requests: {m['requests']} (blocked {m['blocked_by_guard']})")
            st.caption(f"Avg latency: {m['avg_latency_s']}s · p95: {m['p95_latency_s']}s")
            st.caption(f"Tokens: {m['total_tokens']} · est. cost if hosted: ${m['est_cost_usd_if_hosted']}")
    except Exception:
        st.write("Backend: ❌ (not running)")

# ---------------- Chat ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []


def show_sources(sources):
    with st.expander(f"Sources ({len(sources)})"):
        for i, s in enumerate(sources, 1):
            st.markdown(f"**{i}. {s['file']} — page {s['page']}**")
            st.caption(s["text"])


for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        if m.get("sources"):
            show_sources(m["sources"])

if question := st.chat_input("Ask something about your documents"):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        sources = []
        with st.spinner("Thinking..."):
            try:
                r = requests.post(f"{API_URL}/ask", json={"question": question}, timeout=600)
                if r.ok:
                    data = r.json()
                    answer, sources = data["answer"], data["sources"]
                    foot = f"⏱ {data['latency_s']:.1f}s"
                else:
                    answer, foot = f"⚠️ {r.json().get('detail', r.text)}", ""
            except requests.exceptions.ConnectionError:
                answer, foot = "⚠️ Backend not running. Start uvicorn first.", ""
        st.markdown(answer)
        if sources:
            show_sources(sources)
        if foot:
            st.caption(foot)

    st.session_state.messages.append({"role": "assistant", "content": answer, "sources": sources})
