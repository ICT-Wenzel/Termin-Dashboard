import streamlit as st
import requests
from datetime import datetime, timedelta
import re
import pandas as pd
import json

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

# API Request – alle Calls per POST
def api_request(payload=None):
    try:
        if payload is None:
            payload = {}
        response = requests.post(API_BASE_URL, json=payload, timeout=15)
        if response.status_code == 200:
            try:
                data = response.json()
            except ValueError:
                data = json.loads(response.text)
            # Debug
            with st.sidebar.expander("📦 API Response (Debug)"):
                st.write("Datentyp:", type(data))
                st.json(data)
            return data
        else:
            st.error(f"Fehler {response.status_code}: {response.text}")
            return []
    except Exception as e:
        st.error(f"API Fehler: {e}")
        return []

# Fetch Calendar Events
@st.cache_data(ttl=300)
def fetch_calendar():
    payload = {"type": "calendar"}
    data = api_request(payload)
    if not data:
        return []

    # Robust gegen einzelne Objekte oder verschachtelte Arrays
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except Exception:
            return []
    if isinstance(data, dict):
        for key in ["events", "calendar", "body", "data"]:
            if key in data and isinstance(data[key], list):
                return data[key]
        if "id" in data and "summary" in data:
            return [data]
        inner_lists = [v for v in data.values() if isinstance(v, list)]
        if inner_lists:
            return inner_lists[0]
        return []
    if isinstance(data, list):
        return data
    return []

# Format datetime
def format_datetime(dt_string):
    try:
        dt = datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
        return dt.strftime("%d.%m.%Y %H:%M")
    except:
        return dt_string

# Parse description
def parse_description(desc):
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
    ["📅 Kalender", "👨‍🎓 Schüler", "👨‍🏫 Lehrer", "➕ Neuer Termin"]
)

# Kalenderdaten holen
with st.spinner("Lade Kalenderdaten..."):
    events = fetch_calendar()

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

# ➕ Neuer Termin
elif page == "➕ Neuer Termin":
    st.title("➕ Neuen Termin erstellen")

    # Standardwerte nur einmal setzen
    now = datetime.now()
    default_start_time = datetime(now.year, now.month, now.day, 8, 0)  # z.B. 08:00 Uhr
    default_end_time = datetime(now.year, now.month, now.day, 9, 0)    # z.B. 09:00 Uhr

    with st.form("create_event"):
        title = st.text_input("Titel")
        student = st.text_input("Schüler")
        teacher = st.text_input("Lehrer")
        subject = st.text_input("Thema")
        contact = st.text_input("Kontakt")

        start_date = st.date_input("Startdatum", now.date())
        start_time = st.time_input("Startzeit", default_start_time.time())
        end_date = st.date_input("Enddatum", now.date())
        end_time = st.time_input("Endzeit", default_end_time.time())

        submit = st.form_submit_button("Termin erstellen")

        if submit:
            # Datum + Zeit kombinieren
            start_dt = datetime.combine(start_date, start_time)
            end_dt = datetime.combine(end_date, end_time)

            payload = {
                "type": "create",
                "summary": title,
                "description": f"Lehrer: {teacher}\nSchüler: {student}\nThema: {subject}\nKontakt: {contact}",
                "start": start_dt.isoformat(),
                "end": end_dt.isoformat()
            }

            response = requests.post(API_BASE_URL, json=payload)
            if response.status_code == 200:
                st.success("✅ Termin wurde erstellt!")
            else:
                st.error(f"Fehler beim Erstellen: {response.status_code} – {response.text}")
            st.write("API Response:", response.text)


# Footer
st.sidebar.markdown("---")
st.sidebar.info(f"""
**Nachhilfe Dashboard**  
Version 3.0 – mit Termin-Erstellung  
Letzte Aktualisierung: {datetime.now().strftime("%d.%m.%Y %H:%M")}
""")
