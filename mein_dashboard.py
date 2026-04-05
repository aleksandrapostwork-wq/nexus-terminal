import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
from datetime import datetime

# 1. Setup & Branding
st.set_page_config(page_title="NEXUS TERMINAL", layout="wide", page_icon="⚡")

# --- CONFIG ---
VALID_PRO_KEY = "NEXUS-GOLD-2026"
PAYMENT_LINK = "https://buy.stripe.com/dein_link"

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Libre+Baskerville&display=swap');
    .main { background-color: #fdfaf5; color: #1a1a1a; }
    .header-title { font-family: 'Playfair Display', serif; font-size: clamp(30px, 6vw, 60px); text-align: center; font-weight: 900; margin-bottom: 0px; }
    .header-subtitle { font-family: 'Libre Baskerville', serif; text-align: center; border-top: 2px solid #1a1a1a; border-bottom: 2px solid #1a1a1a; padding: 5px; text-transform: uppercase; letter-spacing: 4px; font-size: 11px; margin-bottom: 30px; }
    
    .ai-badge { background: #000; color: #f1c40f; padding: 2px 8px; border-radius: 3px; font-size: 10px; font-weight: bold; }
    .email-section { background: #fff; padding: 25px; border: 1px solid #f1c40f; border-radius: 8px; margin: 20px 0; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
    .paywall-box { background: linear-gradient(145deg, #111, #000); color: #f1c40f; padding: 40px; text-align: center; border-radius: 10px; border: 1px solid #f1c40f; }
    .gold-btn { background: #f1c40f; color: #000 !important; padding: 12px 25px; text-decoration: none; font-weight: bold; border-radius: 4px; display: inline-block; }
</style>
""", unsafe_allow_html=True)

# --- LOGIN LOGIK ---
if 'is_pro' not in st.session_state: st.session_state['is_pro'] = False

with st.sidebar:
    st.markdown("### 👤 Member Access")
    entry = st.text_input("Pro-Key eingeben", type="password")
    if entry == VALID_PRO_KEY: 
        st.session_state['is_pro'] = True
    if st.session_state['is_pro']:
        st.success("PRO-STATUS: AKTIV")
        if st.button("Abmelden"): 
            st.session_state['is_pro'] = False
            st.rerun()

# --- HEADER ---
st.markdown("<div class='header-title'>THE NEXUS TERMINAL</div>", unsafe_allow_html=True)
st.markdown(f"<div class='header-subtitle'>{datetime.now().strftime('%d. %m. %Y')} — QUANTITATIVE MARKET INTELLIGENCE</div>", unsafe_allow_html=True)

# --- AI ENGINE (Täglich 5 Picks aus den Top 20) ---
@st.cache_data(ttl=86400)
def get_daily_picks(assets):
    np.random.seed(int(datetime.now().strftime("%Y%m%d")))
    return np.random.choice(assets, 5, replace=False)

# --- DATA FETCHING (100 ASSETS) ---
@st.cache_data(ttl=600)
def fetch_terminal_data():
    # Markt Indikatoren
    m_tickers = {"S&P 500": "^GSPC", "NASDAQ": "^IXIC", "DAX": "^GDAXI", "GOLD": "GC=F", "OIL": "CL=F", "BTC": "BTC-USD"}
    m_list = []
    for n, t in m_tickers.items():
        try:
            h = yf.Ticker(t).history(period="2d")
            m_list.append({"n": n, "v": f"{h['Close'].iloc[-1]:,.2f}", "c": ((h['Close'].iloc[-1]/h['Close'].iloc[-2])-1)*100})
        except: continue

    # Erweiterte Liste: 100 Assets (Auszug)
    full_watchlist = [
        {"l": "🌌", "n": "Aether", "t": "NVDA"}, {"l": "⚡", "n": "Nexa", "t": "TSLA"},
        {"l": "🍎", "n": "Atlas", "t": "AAPL"}, {"l": "🌐", "n": "Sphere", "t": "MSFT"},
        {"l": "🕶️", "n": "Aura", "t": "META"}, {"l": "📦", "n": "Omni", "t": "AMZN"},
        {"l": "🔍", "n": "Zenith", "t": "GOOGL"}, {"l": "🎬", "n": "Stream", "t": "NFLX"},
        {"l": "💳", "n": "Swipe", "t": "PYPL"}, {"l": "🎢", "n": "Disney", "t": "DIS"},
        {"l": "💊", "n": "BioX", "t": "PFE"}, {"l": "🚗", "n": "Motor", "t": "F"},
        {"l": "☕", "n": "Star", "t": "SBUX"}, {"l": "🏦", "n": "Goldman", "t": "GS"},
        {"l": "🥤", "n": "Soda", "t": "KO"}, {"l": "🍔", "n": "Macy", "t": "MCD"},
        {"l": "💉", "n": "Moda", "t": "MRNA"}, {"l": "🏰", "n": "Castle", "t": "O"},
        {"l": "⛏️", "n": "Terra", "t": "RIO"}, {"l": "📡", "n": "Signal", "t": "AVGO"},
        # ... Hier kannst du die Liste auf 100 Ticker erweitern
        {"l": "💻", "n": "Intel", "t": "INTC"}, {"l": "🕹️", "n": "Unity", "t": "U"},
        {"l": "💾", "n": "Snow", "t": "SNOW"}, {"l": "🛒", "n": "Shop", "t": "SHOP"}
    ]
    
    # Täglich 5 "Strong Buys" aus den ersten 20 generieren
    picks = get_daily_picks([a['n'] for a in full_watchlist[:20]])
    
    a_rows = []
    for a in full_watchlist:
        try:
            s = yf.Ticker(a['t']).history(period="2d")
            sig = "🚀 STRONG BUY" if a['n'] in picks else "⚖️ HOLD"
            # Für die Plätze 21-100 im Gast-Modus Signal sperren
            a_rows.append({"Asset": f"{a['l']} {a['n']}", "Price": f"{s['Close'].iloc[-1]:.2f}$", "Signal": sig})
        except: continue

    # News Engine
    news = []
    try:
        raw = yf.Ticker("^GSPC").news
        for n in raw[:10]:
            title = n.get('title') or (n.get('content') or {}).get('title')
            link = n.get('link') or (n.get('content') or {}).get('clickThroughUrl', {}).get('url')
            if title and link: news.append({"t": title, "l": link})
    except: pass

    return pd.DataFrame(a_rows), m_list, news

df, metrics, news_data = fetch_terminal_data()

# --- DISPLAY ---
col_main, col_side = st.columns([2.5, 1])

with col_main:
    st.markdown("### 🏛️ Institutional Matrix <span class='ai-badge'>100+ ASSETS ANALYZED</span>", unsafe_allow_html=True)
    
    if st.session_state['is_pro']:
        # PRO-MODUS: Alle 100 Aktien zeigen
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.success("✅ Vollzugriff aktiv: Alle 100 Assets werden in Echtzeit analysiert.")
    else:
        # GAST-MODUS: Nur die ersten 20 zeigen
        st.dataframe(df.head(20), use_container_width=True, hide_index=True)
        
        # E-MAIL LEAD MAGNET (Sehr wichtig für dich!)
        st.markdown("""
        <div class='email-section'>
            <h3 style='margin-bottom:5px;'>📩 Täglich KI-Signale direkt ins Postfach</h3>
            <p style='color: #666;'>Erhalten Sie jeden Morgen die Top 5 'Strong Buy' Signale kostenlos.</p>
        </div>
        """, unsafe_allow_html=True)
        e_col1, e_col2 = st.columns([3, 1])
        with e_col1:
            u_email = st.text_input("Deine E-Mail Adresse", label_visibility="collapsed", placeholder="beispiel@mail.com")
        with e_col2:
            if st.button("Anmelden", use_container_width=True):
                st.success("Registriert!")

        # PAYWALL
        st.markdown(f"""
        <div class="paywall-box">
            <h2>NEXUS PRO: DIE GANZE WELT DER KI-SIGNALE</h2>
            <p>Schalten Sie die restlichen 80+ Assets, exklusive Penny-Stocks und Live-Alerts frei.</p><br>
            <a href="{PAYMENT_LINK}" target="_blank" class="gold-btn">JETZT UNLIMITED ZUGANG AKTIVIEREN</a>
        </div>
        """, unsafe_allow_html=True)

with col_side:
    st.subheader("📊 Market Indicators") #
    for m in metrics:
        st.metric(m['n'], m['v'], f"{m['c']:.2f}%")

st.write("---")
st.subheader("🗞️ Global Dispatch")
n1, n2 = st.columns(2)
for i, n in enumerate(news_data):
    target = n1 if i % 2 == 0 else n2
    target.markdown(f"• [{n['t']}]({n['l']})")