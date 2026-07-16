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

# 2. AUTOMATIZAÇÃO QUANTITATIVA DO CÂMBIO
@st.cache_data(ttl=3600)  # Atualiza os dados de hora em hora
def calcular_dados_cambio():
    try:
        # Puxa o último mês do dólar comercial para calcular a volatilidade real
        historico_dolar = yf.Ticker("BRL=X").history(period="1mo")
        
        # O último fechamento serve como nosso Preço Base de referência
        ajuste_auto = historico_dolar['Close'].iloc[-1]
        
        # Cálculo automático da volatilidade real (Máxima - Mínima dos últimos 20 dias)
        historico_dolar['TrueRange'] = historico_dolar['High'] - historico_dolar['Low']
        atr_auto = historico_dolar['TrueRange'].tail(20).mean()
        
        # Ajustando a escala do ATR para pontos do minidólar
        atr_pontos = atr_auto * 1000
        if atr_pontos < 10 or atr_pontos > 150:  # Trava de segurança estatística
            atr_pontos = 48.5
            
        return float(ajuste_auto * 1000), float(atr_pontos)
    except:
        return 5100.0, 48.5

# Executa o algoritmo matemático
fair_value, atr_atual = calcular_dados_cambio()
desvio_estatistico = 1.1

# 3. Painel de Parâmetros de Volatilidade do Dia (Apenas Informativos, Sem Digitação)
st.header("🎯 Parâmetros Calculados Automaticamente")
col_info1, col_info2, col_info3 = st.columns(3)

with col_info1:
    st.metric("Preço de Referência Base", f"{fair_value:.1f}")
with col_info2:
    st.metric("Volatilidade ATR Estimada", f"{atr_atual:.1f} pontos")
with col_info3:
    st.metric("Fator de Desvio Aplicado", f"{desvio_estatistico}")

# 4. Cálculos Matemáticos de Volatilidade
maxima_provavel = fair_value + (atr_atual * desvio_estatistico)
minima_provavel = fair_value - (atr_atual * desvio_estatistico)
vah = fair_value + (atr_atual * 0.5)
val = fair_value - (atr_atual * 0.5)

st.subheader("🔮 Estimativas Projetadas para o Pregão")
c1, c2, c3 = st.columns(3)
c1.metric("📉 Mínima Provável (Suporte)", f"{minima_provavel:.1f}")
c2.metric("⚪ Fair Value (Preço Justo)", f"{fair_value:.1f}")
c3.metric("📈 Máxima Provável (Resistência)", f"{maxima_provavel:.1f}")

# 5. Zonas de Liquidez do Volume Profile Provedor
st.subheader("📍 Zonas de Liquidez e Value Area")
col_z1, col_z2 = st.columns(2)
col_z1.info(f"Value Area High (VAH): {vah:.1f} pontos")
col_z2.info(f"Value Area Low (VAL): {val:.1f} pontos")

# 6. Grade de Pontos de Variação Percentual
st.subheader("📊 Níveis Operacionais Relevantes (Variação Percentual)")

grid_dados = {
    "Nível Operacional": [
        "Resistência Máxima (+1.5%)", 
        "Resistência 2 (+1.0%)", 
        "Resistência 1 (+0.5%)", 
        "Ajuste / Preço Justo (0.0%)", 
        "Suporte 1 (-0.5%)", 
        "Suporte 2 (-1.0%)", 
        "Suporte Máximo (-1.5%)"
    ],
    "Preço Calculado (WDO)": [
        round(fair_value * 1.015, 1),
        round(fair_value * 1.010, 1),
        round(fair_value * 1.005, 1),
        round(fair_value, 1),
        round(fair_value * 0.995, 1),
        round(fair_value * 0.990, 1),
        round(fair_value * 0.985, 1)
    ]
}

df_grid = pd.DataFrame(grid_dados)
st.table(df_grid)

st.markdown("---")
st.warning("⚠️ **Aviso de Risco:** Todas as estimativas exibidas nesta ferramenta são estritamente probabilísticas baseadas em desvios de volatilidade e não garantem o comportamento real do mercado.")
