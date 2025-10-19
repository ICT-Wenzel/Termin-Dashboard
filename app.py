import streamlit as st
import requests
from datetime import datetime, timedelta
import json
import pandas as pd

# Page Config
st.set_page_config(
    page_title="📅 Nachhilfe Kalender",
    page_icon="📚",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .event-item {
        background: #2f3542;               /* dunkles Grau */
        color: #f1f2f6;                    /* helle Schrift */
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 4px solid #70a1ff;    /* hellblauer Akzent */
        box-shadow: 0 2px 6px rgba(0,0,0,0.3);
    }
    .event-item a {
        color: #70a1ff;
    }
    .event-item h4 {
        color: #dfe4ea;
        margin-bottom: 6px;
    }
    .event-item p {
        margin: 3px 0;
        font-size: 0.95rem;
    }
</style>
""", unsafe_allow_html=True)


# Load Secrets
try:
    API_BASE_URL = st.secrets["api"]["base_url"]
except Exception:
    st.error("""
    ### ⚠️ API URL nicht konfiguriert!
    Bitte füge in `.streamlit/secrets.toml` Folgendes hinzu:
    ```toml
    [api]
    base_url = "https://your-n8n-instance.com/webhook"
    ```
    """)
    st.stop()

# API Request
def api_request(params=None):
    try:
        url = API_BASE_URL
        with st.sidebar:
            st.write(f"🔗 **API Call:** `{url}`")
            if params:
                st.write(f"📝 **Params:** {params}")
        response = requests.get(url, params=params, timeout=15)

        if response.status_code == 200:
            data = response.json()
            with st.sidebar.expander("📦 API Response (Debug)"):
                st.json(data)
            return data
        else:
            st.error(f"❌ Fehler: {response.status_code}")
            st.text(response.text)
            return []
    except Exception as e:
        st.error(f"API Fehler: {e}")
        return []

@st.cache_data(ttl=300)
def fetch_calendar():
    """Holt alle Kalender-Events"""
    data = api_request(params={"type": "calendar"})
    
    # Wenn direkt eine Liste kommt
    if isinstance(data, list):
        return data

    # Wenn ein einzelnes Event (dict) kommt → in Liste verpacken
    elif isinstance(data, dict):
        # Prüfen, ob es evtl. schon ein 'events' oder 'calendar'-Key gibt
        if "events" in data:
            return data["events"]
        elif "calendar" in data:
            return data["calendar"]
        else:
            # Es ist ein einzelnes Event
            return [data]
    
    return []


def format_datetime(dt_string):
    """Formatiert ISO DateTime String"""
    try:
        dt = datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
        return dt.strftime("%d.%m.%Y %H:%M")
    except:
        return dt_string

# Sidebar
st.sidebar.title("📚 Nachhilfe Dashboard")
if st.sidebar.button("🔄 Aktualisieren"):
    st.cache_data.clear()
    st.rerun()

# Hauptinhalt
st.title("📅 Kalender Übersicht")

with st.spinner("Lade Kalenderdaten..."):
    events = fetch_calendar()

if not events:
    st.warning("Keine Kalender-Events gefunden.")
    st.stop()

# Stats
col1, col2, col3 = st.columns(3)
today = datetime.now().date()
week_end = today + timedelta(days=7)

today_events = [
    e for e in events
    if "start" in e and datetime.fromisoformat(
        e["start"]["dateTime"].replace("Z", "+00:00")
    ).date() == today
]

week_events = [
    e for e in events
    if "start" in e and today <= datetime.fromisoformat(
        e["start"]["dateTime"].replace("Z", "+00:00")
    ).date() <= week_end
]

with col1:
    st.markdown(f"""
    <div class="stat-box">
        <h2>{len(events)}</h2>
        <p>Termine Gesamt</p>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
    <div class="stat-box">
        <h2>{len(today_events)}</h2>
        <p>Heute</p>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown(f"""
    <div class="stat-box">
        <h2>{len(week_events)}</h2>
        <p>Diese Woche</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Events sortieren
try:
    events = sorted(events, key=lambda x: x["start"]["dateTime"])
except:
    pass

# Anzeigen der Events
st.subheader(f"📋 Alle Termine ({len(events)})")

for e in events:
    start = e.get("start", {}).get("dateTime")
    end = e.get("end", {}).get("dateTime")
    st.markdown(f"""
    <div class="event-item">
        <h4>{e.get('summary', 'Termin')}</h4>
        <p><strong>🕐 Zeit:</strong> {format_datetime(start)} - {format_datetime(end)}</p>
        <p><strong>📘 Beschreibung:</strong> {e.get('description', 'Keine Beschreibung')}</p>
        <p><a href="{e.get('htmlLink', '#')}" target="_blank">🌐 Im Kalender öffnen</a></p>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.sidebar.markdown("---")
st.sidebar.info(f"""
**Nachhilfe Kalender Dashboard**  
Version 1.0 - nur Kalenderansicht  
Letzte Aktualisierung: {datetime.now().strftime("%d.%m.%Y %H:%M")}
""")
