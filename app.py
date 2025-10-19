import streamlit as st
import requests
from datetime import datetime, timedelta
import re
import pandas as pd

# -------------------------------------------------
# 🧭 Grundkonfiguration
# -------------------------------------------------
st.set_page_config(
    page_title="Nachhilfe Dashboard",
    page_icon="📚",
    layout="wide"
)

# -------------------------------------------------
# 🎨 Styling
# -------------------------------------------------
st.markdown("""
<style>
    .event-item {
        background: #f7f8fc;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 4px solid #4a6cf7;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        color: #222;
    }
    .event-item h4 {
        color: #1f2937;
        margin-bottom: 6px;
    }
    .event-item p {
        margin: 2px 0;
        font-size: 0.95rem;
    }
    .stat-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# 🔐 API laden
# -------------------------------------------------
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

# -------------------------------------------------
# 🌐 API Anfrage
# -------------------------------------------------
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

# -------------------------------------------------
# 📅 Kalenderdaten holen & cachen
# -------------------------------------------------
@st.cache_data(ttl=300)
def fetch_calendar():
    """Holt alle Kalender-Events"""
    data = api_request(params={"type": "calendar"})
    if isinstance(data, list):
        return data
    elif isinstance(data, dict):
        if "events" in data:
            return data["events"]
        elif "calendar" in data:
            return data["calendar"]
        else:
            return [data]
    return []

# -------------------------------------------------
# 🕓 Hilfsfunktionen
# -------------------------------------------------
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

# -------------------------------------------------
# 🧭 Sidebar Navigation
# -------------------------------------------------
st.sidebar.title("📚 Nachhilfe Dashboard")

if st.sidebar.button("🔄 Aktualisieren"):
    st.cache_data.clear()
    st.rerun()

page = st.sidebar.radio(
    "Navigation",
    ["📅 Kalender", "👨‍🎓 Schüler", "👨‍🏫 Lehrer"]
)

# -------------------------------------------------
# 🔄 Daten laden
# -------------------------------------------------
with st.spinner("Lade Kalenderdaten..."):
    events = fetch_calendar()

if not events:
    st.warning("Keine Kalender-Events gefunden.")
    st.stop()

# Beschreibung auslesen
for e in events:
    info = parse_description(e.get("description", ""))
    e.update(info)

# -------------------------------------------------
# 📅 Kalenderübersicht
# -------------------------------------------------
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

    # 🔹 DataFrame-Ansicht für große Datenmengen
    calendar_df = pd.DataFrame([
        {
            "Datum Start": format_datetime(e["start"]["dateTime"]),
            "Datum Ende": format_datetime(e["end"]["dateTime"]),
            "Titel": e.get("summary", ""),
            "Lehrer": e.get("Lehrer", "N/A"),
            "Schüler": e.get("Schüler", "N/A"),
            "Thema": e.get("Thema", "N/A"),
            "Link": e.get("htmlLink", "")
        }
        for e in sorted(events, key=lambda x: x["start"]["dateTime"])
    ])

    st.dataframe(calendar_df, use_container_width=True, hide_index=True)

# -------------------------------------------------
# 👨‍🎓 Schülerübersicht
# -------------------------------------------------
elif page == "👨‍🎓 Schüler":
    st.title("👨‍🎓 Schüler Übersicht")

    schueler = sorted(set([e.get("Schüler") for e in events if e.get("Schüler")]))

    if not schueler:
        st.info("Keine Schüler in den Beschreibungen gefunden.")
        st.stop()

    selected_student = st.selectbox("Schüler auswählen", schueler)
    student_events = [e for e in events if e.get("Schüler") == selected_student]

    st.subheader(f"📅 Termine von {selected_student}")

    student_df = pd.DataFrame([
        {
            "Datum": format_datetime(e["start"]["dateTime"]),
            "Lehrer": e.get("Lehrer", "N/A"),
            "Thema": e.get("Thema", "N/A"),
            "Titel": e.get("summary", ""),
            "Link": e.get("htmlLink", "")
        }
        for e in sorted(student_events, key=lambda x: x["start"]["dateTime"])
    ])

    if student_df.empty:
        st.info("Keine Termine gefunden.")
    else:
        st.dataframe(student_df, use_container_width=True, hide_index=True)

# -------------------------------------------------
# 👨‍🏫 Lehrerübersicht
# -------------------------------------------------
elif page == "👨‍🏫 Lehrer":
    st.title("👨‍🏫 Lehrer Übersicht")

    lehrer = sorted(set([e.get("Lehrer") for e in events if e.get("Lehrer")]))

    if not lehrer:
        st.info("Keine Lehrer in den Beschreibungen gefunden.")
        st.stop()

    selected_teacher = st.selectbox("Lehrer auswählen", lehrer)
    teacher_events = [e for e in events if e.get("Lehrer") == selected_teacher]

    st.subheader(f"📅 Termine von {selected_teacher}")

    teacher_df = pd.DataFrame([
        {
            "Datum": format_datetime(e["start"]["dateTime"]),
            "Schüler": e.get("Schüler", "N/A"),
            "Thema": e.get("Thema", "N/A"),
            "Titel": e.get("summary", ""),
            "Link": e.get("htmlLink", "")
        }
        for e in sorted(teacher_events, key=lambda x: x["start"]["dateTime"])
    ])

    if teacher_df.empty:
        st.info("Keine Termine gefunden.")
    else:
        st.dataframe(teacher_df, use_container_width=True, hide_index=True)

# -------------------------------------------------
# 📘 Footer
# -------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.info(f"""
**Nachhilfe Dashboard**  
Version 3.0 – optimiert für 1000+ Termine  
Letzte Aktualisierung: {datetime.now().strftime("%d.%m.%Y %H:%M")}
""")
