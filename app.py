"""Aplicação Streamlit – Gerador de Mensagens GGMAX."""
import io
import streamlit as st
from converter import carregar_formatos, renderizar_linha

st.set_page_config(page_title="Gerador de Mensagens GGMAX", layout="centered")

# ── CSS global, baseado nas VARIÁVEIS de tema do Streamlit ────────────────
st.markdown(
    """
    <style>
    /* Fundo geral do app (usa a cor do tema) */
    .stApp { background-color: var(--background-color); }

    /* Card central: usa cor secundária do tema */
    .block-container {
        max-width: 900px;
        margin: 40px auto;
        padding: 2.5rem 2rem;
        background: var(--secondary-background-color);
        border: 1px solid rgba(0,0,0,.10);            /* claro */
        border-radius: 12px;
        box-shadow: 0 8px 16px rgba(0,0,0,.08);
    }
    /* Sombra + borda ficam mais fortes no dark */
    html[data-theme='dark'] .block-container {
        border: 1px solid rgba(255,255,255,.12);
        box-shadow: 0 8px 16px rgba(0,0,0,.40);
    }

    /* Botão principal um pouco maior */
    div.stButton > button:first-child {
        font-weight: 600;
        padding: 0.6rem 1.5rem;
        border-radius: 6px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
# -------------------------------------------------------------------------

st.title("🛠️ Gerador de Mensagens GGMAX")

# Seleção de jogo
formatos = carregar_formatos()
jogo = st.selectbox("Selecione o jogo:", list(formatos.keys()))

# Upload opcional de template
tpl_upload = st.file_uploader("Template .txt personalizado (opcional)", type=["txt"])

# Dados brutos
st.markdown("### Dados brutos (uma linha por conta):")
base_text = st.text_area("Cole ou arraste as contas aqui", height=180)
base_file = st.file_uploader("…ou envie um arquivo base.txt", type=["txt"])

linhas = []
if base_file:
    linhas += base_file.getvalue().decode("utf-8").splitlines()
if base_text:
    linhas += base_text.splitlines()

# Geração
if st.button("Gerar mensagens") and linhas:
    tpl_path = None
    if tpl_upload:
        tpl_path = "_template_temp.txt"
        with open(tpl_path, "w", encoding="utf-8") as f:
            f.write(tpl_upload.getvalue().decode("utf-8"))

    msgs = [
        renderizar_linha(l, jogo=jogo, formatos=formatos, template_path=tpl_path)
        for l in linhas if l.strip()
    ]
    resultado = ";\n".join(msgs) + ";"
    st.text_area("Pré-visualização", resultado, height=250)

    buf = io.BytesIO(resultado.encode("utf-8"))
    st.download_button(
        "⬇️ Baixar mensagens",
        data=buf,
        file_name="mensagens.txt",
        mime="text/plain",
    )
