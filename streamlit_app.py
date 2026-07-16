import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Agente Quant - WDO", layout="wide", page_icon="📊")

st.title("📊 Agente Quantitativo: Pré-Mercado Mini Dólar (WDO)")
st.caption("Protótipo de automação de dados e análise de volatilidade para o mercado futuro brasileiro")

# 1. Coleta Automática de Dados Globais via Yahoo Finance
st.sidebar.header("🌍 Mercado Global (Ao Vivo)")

tickers = {
    "Dollar Index (DXY)": "DX-Y.NYB",
    "Treasury 10 Anos (Yield)": "^TNX",
    "S&P 500 Futuro": "ES=F",
    "Nasdaq Futuro": "NQ=F",
    "Petróleo Brent": "BZ=F",
    "Ouro (XAU/USD)": "GC=F",
    "Peso Mexicano (USD/MXN)": "MXN=X"
}

for nome, ticker in tickers.items():
    try:
        dados = yf.Ticker(ticker).history(period="1d")
        if not dados.empty:
            preco = dados['Close'].iloc[-1]
            variacao = ((dados['Close'].iloc[-1] - dados['Open'].iloc[-1]) / dados['Open'].iloc[-1]) * 100
            st.sidebar.metric(label=nome, value=f"{preco:.2f}", delta=f"{variacao:.2f}%")
    except:
        st.sidebar.metric(label=nome, value="Indisponível")

# 2. Entrada de Parâmetros do Usuário para o Cálculo do WDO
st.header("🎯 Parâmetros de Volatilidade do Dia")
col_input1, col_input2, col_input3 = st.columns(3)

with col_input1:
    ajuste_anterior = st.number_input("Preço de Ajuste Anterior (WDO):", value=5100.0, step=0.5)
with col_input2:
    atr_atual = st.number_input("ATR atual (Volatilidade Média de 20 períodos):", value=48.5, step=0.5)
with col_input3:
    desvio = st.slider("Fator de Desvio Estatístico:", min_value=0.5, max_value=2.0, value=1.2, step=0.1)

# 3. Cálculos de Inteligência Quantitativa
fair_value = ajuste_anterior  # Simplificação baseada em paridade de juros/ajuste
maxima_provavel = fair_value + (atr_atual * desvio)
minima_provavel = fair_value - (atr_atual * desvio)
vah = fair_value + (atr_atual * 0.5)
val = fair_value - (atr_atual * 0.5)

st.subheader("🔮 Estimativas Projetadas para o Pregão")
c1, c2, c3 = st.columns(3)
c1.metric("📉 Mínima Provável (Suporte)", f"{minima_provavel:.1f}")
c2.metric("⚪ Fair Value (Preço Justo)", f"{fair_value:.1f}")
c3.metric("📈 Máxima Provável (Resistência)", f"{maxima_provavel:.1f}")

# 4. Zonas de Liquidez do Volume Profile Provedor
st.subheader("📍 Zonas de Liquidez e Value Area")
col_z1, col_z2 = st.columns(2)
col_z1.info(f"Value Area High (VAH): {vah:.1f} pontos")
col_z2.info(f"Value Area Low (VAL): {val:.1f} pontos")

st.markdown("---")
st.warning("⚠️ **Aviso de Risco:** Todas as estimativas exibidas nesta ferramenta são estritamente probabilísticas baseadas em desvios de volatilidade e não garantem o comportamento real do mercado.")
