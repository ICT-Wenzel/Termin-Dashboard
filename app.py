import streamlit as st
import requests
from datetime import datetime, timedelta
import re
import pandas as pd

# Page Config
st.set_page_config(
    page_title="Nachhilfe Dashboard",
    page_icon="📚",
    layout="wide"
)

# CSS Styles
st.markdown("""
<style>
    .stat-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Load Secrets
try:
    API_BASE_URL = st.secrets["api"]["base_url"]
except Exception:
    st.error("""
    ⚠️ API URL nicht konfiguriert!
    Füge bitte in `.streamlit/secrets.toml` folgendes hinzu:
    ```toml
    [api]
    base_url = "https://your-n8n-instance.com/webhook"
    ```
    """)
    st.stop()

# API Request
def api_request(params=None):
    try:
        response = requests.get(API_BASE_URL, params=params, timeout=15)
        if response.status_code == 200:
            data = response.json()
            with st.sidebar.expander("📦 API Response (Debug)"):
                st.json(data)
            return data
        else:
            st.error(f"Fehler {response.status_code}")
            return []
    except Exception as e:
        st.error(f"API Fehler: {e}")
        return []

@st.cache_data(ttl=300)
def fetch_calendar():
    """Holt alle Kalender-Events (automatisch robust gegen API-Formate)"""
    data = api_request(params={"type": "calendar"})
    
    if not data:
        return []
    
    # n8n gibt evtl. direkt eine Liste oder ein Objekt zurück
    if isinstance(data, list):
        return data
    elif isinstance(data, dict):
        # Falls es verschachtelt ist (body, data, events etc.)
        for key in ["events", "calendar", "body", "data"]:
            if key in data and isinstance(data[key], list):
                return data[key]
        # Falls einzelnes Event:
        if "id" in data and "summary" in data:
            return [data]
    return []

def format_datetime(dt_string):
    try:
        dt = datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
        return dt.strftime("%d.%m.%Y %H:%M")
    except:
        return dt_string

def parse_description(desc):
    """Extrahiert Lehrer, Schüler, Thema aus der Beschreibung"""
    if not desc:
        return {"Lehrer": None, "Schüler": None, "Thema": None}
    info = {}
    for key in ["Lehrer", "Schüler", "Thema"]:
        match = re.search(rf"{key}:\s*([^\n\r]+)", desc)
        if match:
            info[key] = match.group(1).strip()
    return info

# Sidebar Navigation
st.sidebar.title("📚 Nachhilfe Dashboard")

if st.sidebar.button("🔄 Aktualisieren"):
    st.cache_data.clear()
    st.rerun()

page = st.sidebar.radio(
    "Navigation",
    ["📅 Kalender", "👨‍🎓 Schüler", "👨‍🏫 Lehrer"]
)

# Kalenderdaten holen
with st.spinner("Lade Kalenderdaten..."):
    events = fetch_calendar()

# Falls keine Daten
if not events:
    st.warning("Keine Kalender-Events gefunden.")
    st.stop()

# Alle Events erweitern mit Info aus Beschreibung
for e in events:
    info = parse_description(e.get("description", ""))
    e.update(info)

# 📅 Kalender Übersicht
if page == "📅 Kalender":
    st.title("📅 Kalender Übersicht")

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
        st.markdown(f"<div class='stat-box'><h2>{len(events)}</h2><p>Termine Gesamt</p></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='stat-box'><h2>{len(today_events)}</h2><p>Heute</p></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='stat-box'><h2>{len(week_events)}</h2><p>Diese Woche</p></div>", unsafe_allow_html=True)

    st.markdown("---")

    df = pd.DataFrame([
        {
            "Datum": format_datetime(e["start"]["dateTime"]),
            "Lehrer": e.get("Lehrer", "N/A"),
            "Schüler": e.get("Schüler", "N/A"),
            "Thema": e.get("Thema", "N/A"),
            "Titel": e.get("summary", ""),
            "Link": e.get("htmlLink", "")
        }
        for e in events
    ])
    st.dataframe(df, use_container_width=True, hide_index=True)

# 👨‍🎓 Schüler Übersicht
elif page == "👨‍🎓 Schüler":
    st.title("👨‍🎓 Schüler Übersicht")
    schueler = sorted(set([e.get("Schüler") for e in events if e.get("Schüler")]))
    if not schueler:
        st.info("Keine Schüler in den Beschreibungen gefunden.")
        st.stop()

    selected_student = st.selectbox("Schüler auswählen", schueler)
    student_events = [e for e in events if e.get("Schüler") == selected_student]

    df = pd.DataFrame([
        {
            "Datum": format_datetime(e["start"]["dateTime"]),
            "Lehrer": e.get("Lehrer", "N/A"),
            "Thema": e.get("Thema", "N/A"),
            "Titel": e.get("summary", ""),
            "Link": e.get("htmlLink", "")
        }
        for e in student_events
    ])
    st.dataframe(df, use_container_width=True, hide_index=True)

# 👨‍🏫 Lehrer Übersicht
elif page == "👨‍🏫 Lehrer":
    st.title("👨‍🏫 Lehrer Übersicht")
    lehrer = sorted(set([e.get("Lehrer") for e in events if e.get("Lehrer")]))
    if not lehrer:
        st.info("Keine Lehrer in den Beschreibungen gefunden.")
        st.stop()

    selected_teacher = st.selectbox("Lehrer auswählen", lehrer)
    teacher_events = [e for e in events if e.get("Lehrer") == selected_teacher]

    df = pd.DataFrame([
        {
            "Datum": format_datetime(e["start"]["dateTime"]),
            "Schüler": e.get("Schüler", "N/A"),
            "Thema": e.get("Thema", "N/A"),
            "Titel": e.get("summary", ""),
            "Link": e.get("htmlLink", "")
        }
        for e in teacher_events
    ])
    st.dataframe(df, use_container_width=True, hide_index=True)

# Footer
st.sidebar.markdown("---")
st.sidebar.info(f"""
**Nachhilfe Dashboard**  
Version 2.1 – robust & performant  
Letzte Aktualisierung: {datetime.now().strftime("%d.%m.%Y %H:%M")}
""")
