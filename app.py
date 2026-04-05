import streamlit as st
import pandas as pd
import plotly.express as px
import psycopg2
from openai import OpenAI

# 🎨 Paleta CGE
VERDE = "#2EA44F"
VERDE_ESCURO = "#1B8F3A"
VERDE_CLARO = "#4FB3A5"
LARANJA = "#F25C05"
VERMELHO = "#D62828"

# 🔐 API
api_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=api_key)

# 🔐 BANCO
DB_HOST = st.secrets["DB_HOST"]
DB_NAME = st.secrets["DB_NAME"]
DB_USER = st.secrets["DB_USER"]
DB_PASSWORD = st.secrets["DB_PASSWORD"]
DB_PORT = st.secrets["DB_PORT"]

# ── CONFIG PÁGINA ─────────────────────────────────────────────
st.set_page_config(
    page_title="Painel de Anomalias - Ceará",
    page_icon="🔍",
    layout="wide"
)

# Faixa CGE
st.markdown("""
<div style="height:8px;
background: linear-gradient(90deg, #2EA44F, #4FB3A5, #F25C05);">
</div>
""", unsafe_allow_html=True)

# CSS
st.markdown("""
<style>
    .stApp { background-color: #f4f7f6; }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1B8F3A 0%, #4FB3A5 100%);
    }

    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span {
        color: white !important;
    }

    textarea {
        color: black !important;
        background-color: white !important;
    }

    .stButton > button {
        background: #2EA44F;
        color: white !important;
        border-radius: 8px;
        border: none;
    }

    .stButton > button:hover {
        background: #1B8F3A;
    }

    h1, h2, h3 { color: #1B8F3A !important; }
</style>
""", unsafe_allow_html=True)

# ── DADOS (POSTGRES) ──────────────────────────────────────────
import traceback

def carregar_dados():
    try:
        conn = psycopg2.connect(
            f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require"
        )

        st.success("✅ Conectou no banco!")

        query = "SELECT 1"
        df = pd.read_sql(query, conn)
        conn.close()

        return df

    except Exception as e:
        st.error("ERRO REAL ↓")
        st.code(traceback.format_exc())
        return pd.DataFrame()
    
    # 👇 FORA da função
df = carregar_dados()

if df is None or df.empty:
    st.warning("⚠️ Erro ao carregar dados ou banco vazio.")
    st.stop()

# ── CONTEXTO IA ───────────────────────────────────────────────
def gerar_contexto(df):
    top_fornecedores = df['fornecedor_nome'].value_counts().head(5).to_dict()

    return f"""
Você é um assistente de análise de contratos públicos.

REGRAS:
- Responda apenas com base nos dados fornecidos
- NÃO altere o dashboard
- Seja direto

Total de contratos: {len(df)}

ALTO: {len(df[df['nivel_risco']=='ALTO'])}
MÉDIO: {len(df[df['nivel_risco']=='MÉDIO'])}
BAIXO: {len(df[df['nivel_risco']=='BAIXO'])}

Top fornecedores:
{top_fornecedores}
"""

# ── SIDEBAR (CHAT) ────────────────────────────────────────────
with st.sidebar:
    st.title("🤖 Assistente IA")

    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [
            {"role": "assistant", "content": "Pergunte sobre os contratos."}
        ]

    if st.button("🗑️ Limpar conversa"):
        st.session_state.chat_messages = [
            {"role": "assistant", "content": "Conversa reiniciada."}
        ]
        st.rerun()

    for msg in st.session_state.chat_messages[-10:]:
        st.write(f"**{msg['role']}**: {msg['content']}")

    user_question = st.text_area("Pergunta")

    if st.button("📨 Enviar"):
        if not api_key:
            st.error("Chave API não encontrada")

        elif user_question.strip():

            st.session_state.chat_messages.append({
                "role": "user",
                "content": user_question
            })

            try:
                messages = [{"role": "system", "content": gerar_contexto(df)}]

                messages += [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.chat_messages
                    if m["role"] in ["user", "assistant"]
                ]

                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages
                )

                resposta = response.choices[0].message.content

                st.session_state.chat_messages.append({
                    "role": "assistant",
                    "content": resposta
                })

                st.rerun()

            except Exception as e:
                st.error(f"Erro: {e}")

# ── TÍTULO ────────────────────────────────────────────────────
st.title("🔍 Painel de Contratos Anômalos — Ceará Transparente")

# ── MÉTRICAS ──────────────────────────────────────────────────
col1, col2, col3, col4, col5 = st.columns(5)

total = len(df)
alto = len(df[df["nivel_risco"] == "ALTO"])
medio = len(df[df["nivel_risco"] == "MÉDIO"])
baixo = len(df[df["nivel_risco"] == "BAIXO"])
perc = (alto / total) * 100

col1.metric("🔴 ALTO", alto)
col2.metric("🟡 MÉDIO", medio)
col3.metric("🟢 BAIXO", baixo)
col4.metric("📋 TOTAL", total)
col5.metric("🚨 % ALTO", f"{perc:.1f}%")

st.divider()

# ── FILTRO ───────────────────────────────────────────────────
nivel = st.multiselect(
    "Filtrar risco",
    ["ALTO", "MÉDIO", "BAIXO"],
    default=["ALTO", "MÉDIO", "BAIXO"]
)

df_f = df[df["nivel_risco"].isin(nivel)]

# ── GRÁFICOS ─────────────────────────────────────────────────
st.subheader("🏢 Top Fornecedores por Valor Total")

top = (
    df_f.groupby("fornecedor_nome")["valor_global"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

fig = px.bar(
    top,
    x="valor_global",
    y="fornecedor_nome",
    orientation="h",
    color="valor_global",
    color_continuous_scale=[VERDE_CLARO, VERDE, VERDE_ESCURO],
    text="valor_global"
)

fig.update_traces(
    texttemplate="R$ %{text:,.0f}",
    textposition="outside"
)

fig.update_layout(
    xaxis_title=None,
    yaxis_title=None,
    coloraxis_showscale=False,
    margin=dict(l=20, r=20, t=20, b=20)
)

st.plotly_chart(fig, use_container_width=True)

col_a, col_b = st.columns(2)

# 📊 Anomalias
with col_a:
    st.subheader("📊 Anomalias por Fornecedor")

    fornecedor = df_f["fornecedor_nome"].value_counts().head(15).reset_index()
    fornecedor.columns = ["fornecedor_nome", "quantidade"]

    fig1 = px.bar(
        fornecedor,
        x="quantidade",
        y="fornecedor_nome",
        orientation="h",
        color="quantidade",
        color_continuous_scale=[VERDE_CLARO, VERDE, VERDE_ESCURO],
        text="quantidade"
    )

    fig1.update_traces(
        texttemplate="%{text}",
        textposition="outside"
    )

    fig1.update_layout(
        xaxis_title=None,
        yaxis_title=None,
        coloraxis_showscale=False,
        margin=dict(l=20, r=20, t=20, b=20)
    )

    st.plotly_chart(fig1, use_container_width=True)

# 🎯 PIZZA RESTAURADO
with col_b:
    st.subheader("🎯 Distribuição por Risco")

    if len(df_f) > 0:
        fig2 = px.pie(
            df_f,
            names="nivel_risco",
            color="nivel_risco",
            color_discrete_map={
                "ALTO": VERMELHO,
                "MÉDIO": LARANJA,
                "BAIXO": VERDE
            }
        )

        fig2.update_traces(textinfo="percent+label")

        fig2.update_layout(
            margin=dict(l=20, r=20, t=20, b=20)
        )

        st.plotly_chart(fig2, use_container_width=True)

    else:
        st.warning("Sem dados para exibir")

# 💰 Box
st.subheader("💰 Valor por Risco")

fig3 = px.box(
    df_f,
    x="nivel_risco",
    y="valor_global",
    color="nivel_risco",
    color_discrete_map={
        "ALTO": VERMELHO,
        "MÉDIO": LARANJA,
        "BAIXO": VERDE
    }
)

st.plotly_chart(fig3, use_container_width=True)

# ── TABELA ───────────────────────────────────────────────────
st.subheader("📋 Contratos")

df_display = df_f.copy()

df_display["valor_global"] = df_display["valor_global"].apply(
    lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
)

df_display["percentil_risco"] = df_display["percentil_risco"].apply(
    lambda x: f"{x:.2f}%".replace(".", ",")
)

st.dataframe(df_display, use_container_width=True)
