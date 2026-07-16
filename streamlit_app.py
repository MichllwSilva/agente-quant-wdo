import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from datetime import datetime

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

# --- CONFIGURAÇÃO E ENVIO DO TELEGRAM ---
TELEGRAM_TOKEN = "8973889827:AAH9gd43aRXlxDj8F7P5SKDa2-9TZvK8Y5s"
TELEGRAM_CHAT_ID = "7683631230"

def enviar_relatorio_telegram():
    data_hoje = datetime.now().strftime('%d/%m/%Y')
    
    dxy_p, dxy_v = puxar_metricas("DX-Y.NYB")
    sp_p, sp_v = puxar_metricas("ES=F")
    
    mensagem = f"""
🤖 *AGENTE QUANT: BOM DIA MICHELL!* 📊
*Data de Referência:* {data_hoje}

*Contexto Rápido:*
• DXY: {dxy_p:.2f} ({dxy_v:+.2f}%)
• S&P 500 Fut: {sp_p:.1f} ({sp_v:+.2f}%)

*🎯 Projeções de Volatilidade (WDO):*
• *Máxima Provável:* {maxima_provavel:.1f}
• *Preço Justo (FV):* {fair_value:.1f}
• *Mínima Provável:* {minima_provavel:.1f}

*📍 Regiões de Liquidez (Value Area):*
• Value Area High (VAH): {vah:.1f}
• Value Area Low (VAL): {val:.1f}

*📊 Desvios de Percentuais:*
• R2 (+1.0%): {fair_value * 1.010:.1f}
• R1 (+0.5%): {fair_value * 1.005:.1f}
• S1 (-0.5%): {fair_value * 0.995:.1f}
• S2 (-1.0%): {fair_value * 0.990:.1f}

_Bons trades! Gerencie seu risco._ ⚡
"""
    # URL construída de forma direta e sem concatenação de variáveis de string
    url = "https://telegram.org"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mensagem, "parse_mode": "Markdown"}
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            st.success("✅ Relatório diário disparado com sucesso para o Telegram!")
        else:
            st.error("❌ Falha no envio. Certifique-se de que você iniciou o bot no seu aplicativo com /start.")
    except Exception as e:
        st.error(f"Erro de conexão com o Telegram: {e}")

# Botão físico no cabeçalho do site para teste ou gatilho rápido
if st.button("🚀 Disparar Relatório no meu Telegram Agora"):
    enviar_relatorio_telegram()

st.markdown("---")

# --- DIVISÃO DA TELA EM LAYOUT DE GRID ---
col_esquerda, col_centro, col_direita = st.columns(3)

# --- COLUNA ESQUERDA: DIRETRIZES DA MOEDA GLOBAL & BOLSAS ---
with col_esquerda:
    st.subheader("🇺🇸 US DXY & Paridades")
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

# --- COLUNA CENTRAL: O MAIS IMPORTANTE PARA OPERAR O WDO ---
with col_centro:
    st.markdown("<h2 style='text-align: center; color: #FF4B4B;'>🎯 MODELO OPERACIONAL WDO</h2>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    c1.metric("📉 Mínima Provável", f"{minima_provavel:.1f}")
    c2.metric("⚪ Fair Value", f"{fair_value:.1f}")
    c3.metric("📈 Máxima Provável", f"{maxima_provavel:.1f}")
    
    st.markdown("### 📍 Regiões de Liquidez (Value Area)")
    col_v1, col_v2 = st.columns(2)
    col_v1.info(f"**Value Area High (VAH):** {vah:.1f} pontos")
    col_v2.info(f"**Value Area Low (VAL):** {val:.1f} pontos")
    
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
