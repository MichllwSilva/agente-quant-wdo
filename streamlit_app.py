import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Configurações Iniciais da Página em Modo Amplo
st.set_page_config(page_title="Panorama Quant - WDO", layout="wide", page_icon="📊")

st.markdown("""
    <style>
    div[data-testid="stMetricValue"] {
        font-size: 26px !important;
        font-weight: bold !important;
    }
    .stAlert {
        padding: 8px !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎛️ Panorama Quantitativo de Abertura — Foco Mini Dólar")
st.caption("Alinhamento estratégico baseado na Rotina de Abertura e Paridades de Volatilidade Globais")

# --- FUNÇÃO DE COLETA AUTOMÁTICA DE ATIVOS ---
@st.cache_data(ttl=60)
def puxar_metricas(ticker):
    try:
        dados = yf.Ticker(ticker).history(period="2d")
        if len(dados) >= 2:
            preco_atual = dados['Close'].iloc[-1]
            preco_anterior = dados['Close'].iloc[-2]
            variacao = ((preco_atual - preco_anterior) / preco_anterior) * 100
            return preco_atual, variacao
        elif not dados.empty:
            return dados['Close'].iloc[-1], 0.0
        return 0.0, 0.0
    except:
        return 0.0, 0.0

# --- ALGORITMO QUANTITATIVO DO MINI DÓLAR (CENTRAL) ---
try:
    historico_dolar = yf.Ticker("BRL=X").history(period="1mo")
    fechamento_raw = historico_dolar['Close'].iloc[-1]
    fair_value = float(fechamento_raw * 1000)
    
    # Cálculo estatístico do ATR (Média da volatilidade real dos últimos 20 dias)
    historico_dolar['TrueRange'] = historico_dolar['High'] - historico_dolar['Low']
    atr_atual = float(historico_dolar['TrueRange'].tail(20).mean() * 1000)
except:
    fair_value, atr_atual = 5100.0, 48.5

# Parâmetros matemáticos fixados da volatilidade
desvio_padrao = 1.1
maxima_provavel = fair_value + (atr_atual * desvio_padrao)
minima_provavel = fair_value - (atr_atual * desvio_padrao)
vah = fair_value + (atr_atual * 0.5)
val = fair_value - (atr_atual * 0.5)

# --- DIVISÃO DA TELA EM LAYOUT DE GRID (ESTILO PANORAMA) ---
col_esquerda, col_centro, col_direita = st.columns([1, 2, 1])

# --- COLUNA ESQUERDA: DIRETRIZES DA MOEDA GLOBAL & BOLSAS ---
with col_esquerda:
    st.subheader("🇺🇸 DXY & Paridades")
    p, v = puxar_metricas("DX-Y.NYB")
    st.metric("Dollar Index (DXY)", f"{p:.2f}", f"{v:.2f}%")
    p, v = puxar_metricas("EURUSD=X")
    st.metric("EUR/USD (Euro)", f"{p:.4f}", f"{v:.2f}%")
    p, v = puxar_metricas("JPY=X")
    st.metric("USD/JPY (Iene)", f"{p:.2f}", f"{v:.2f}%")
    p, v = puxar_metricas("GBPUSD=X")
    st.metric("GBP/USD (Libra)", f"{p:.4f}", f"{v:.2f}%")
    
    st.subheader("🇺🇸 Bolsas / América")
    p, v = puxar_metricas("ES=F")
    st.metric("S&P 500 Futuro", f"{p:.1f}", f"{v:.2f}%")
    p, v = puxar_metricas("NQ=F")
    st.metric("NASDAQ Futuro", f"{p:.1f}", f"{v:.2f}%")

# --- COLUNA CENTRAL: O MAIS IMPORTANTE PARA VOCÊ OPERAR O WDO ---
with col_centro:
    st.markdown("<h2 style='text-align: center; color: #FF4B4B;'>🎯 MODELO OPERACIONAL WDO</h2>", unsafe_allow_html=True)
    
    # Box com as 3 métricas principais de ancoragem
    c1, c2, c3 = st.columns(3)
    c1.metric("📉 Mínima Provável (Suporte)", f"{minima_provavel:.1f}")
    c2.metric("⚪ Fair Value (Preço Justo)", f"{fair_value:.1f}")
    c3.metric("📈 Máxima Provável (Resistência)", f"{maxima_provavel:.1f}")
    
    # Identificação rápida de Value Area (Zonas de briga)
    st.markdown("### 📍 Regiões de Liquidez (Value Area)")
    col_v1, col_v2 = st.columns(2)
    col_v1.info(f"**Value Area High (VAH):** {vah:.1f} pontos")
    col_v2.info(f"**Value Area Low (VAL):** {val:.1f} pontos")
    
    # Grade de variação percentual para colocação de ordens limite (Scalping)
    st.markdown("### 📊 Níveis Operacionais Relevantes")
    grid_dados = {
        "Nível Técnico": [
            "Resistência Crítica (+1.5%)", "Resistência 2 (+1.0%)", "Resistência 1 (+0.5%)",
            "Ponto de Equilíbrio (0.0%)",
            "Suporte 1 (-0.5%)", "Suporte 2 (-1.0%)", "Suporte Crítico (-1.5%)"
        ],
        "Preço no WDO": [
            round(fair_value * 1.015, 1), round(fair_value * 1.010, 1), round(fair_value * 1.005, 1),
            round(fair_value, 1),
            round(fair_value * 0.995, 1), round(fair_value * 0.990, 1), round(fair_value * 0.985, 1)
        ]
    }
    st.table(pd.DataFrame(grid_dados))

# --- COLUNA DIREITA: TAXAS DE JUROS, EMERGENTES & COMMODITIES ---
with col_direita:
    st.subheader("🏦 Juros / Treasuries")
    p, v = puxar_metricas("^TNX")
    st.metric("Treasury 10Y (Yield)", f"{p:.2f}%", f"{v:.2f}%", delta_color="inverse")
    p, v = puxar_metricas("^IRX")
    st.metric("Treasury 3M (Yield)", f"{p:.2f}%", f"{v:.2f}%", delta_color="inverse")
    
    st.subheader("🚩 Moedas Emergentes")
    p, v = puxar_metricas("MXN=X")
    st.metric("USD/MXN (Peso Mexicano)", f"{p:.4f}", f"{v:.2f}%")
    p, v = puxar_metricas("CNY=X")
    st.metric("USD/CNY (Yuan)", f"{p:.4f}", f"{v:.2f}%")
    
    st.subheader("🛢️ Commodities / Risco")
    p, v = puxar_metricas("BZ=F")
    st.metric("Petróleo Brent", f"US$ {p:.2f}", f"{v:.2f}%")
    p, v = puxar_metricas("GC=F")
    st.metric("Ouro Futuro", f"US$ {p:.2f}", f"{v:.2f}%")

st.markdown("---")
st.warning("⚠️ **Aviso de Risco:** Todas as estimativas exibidas nesta ferramenta são baseadas em desvios estatísticos de volatilidade e não garantem o comportamento real do mercado.")
