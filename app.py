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

# ---------------------------
# API Request Funktion
# ---------------------------
def api_request(payload=None):
    """API-Request via POST – erkennt automatisch JSON"""
    if payload is None:
        payload = {}

    try:
        response = requests.post(API_BASE_URL, json=payload, timeout=15)
        if response.status_code == 200:
            try:
                data = response.json()
            except ValueError:
                data = json.loads(response.text)

            # Debug-Ausgabe
            with st.sidebar.expander("📦 API Response (Debug)"):
                st.write("Datentyp:", type(data))
                st.json(data)

            return data
        else:
            st.error(f"Fehler {response.status_code} - {response.text}")
            return []
    except Exception as e:
        st.error(f"API Fehler: {e}")
        return []

# ---------------------------
# Kalenderdaten holen
# ---------------------------
@st.cache_data(ttl=300)
def fetch_calendar():
    """Holt alle Kalender-Events via POST"""
    payload = {"type": "calendar"}  # n8n weiß, dass es Kalender-Daten senden soll
    data = api_request(payload=payload)

    if not data:
        return []

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

# ---------------------------
# Hilfsfunktionen
# ---------------------------
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

# ---------------------------
# Sidebar Navigation
# ---------------------------
st.sidebar.title("📚 Nachhilfe Dashboard")

if st.sidebar.button("🔄 Aktualisieren"):
    st.cache_data.clear()
    st.rerun()

page = st.sidebar.radio(
    "Navigation",
    ["📅 Kalender", "👨‍🎓 Schüler", "👨‍🏫 Lehrer", "➕ Neuer Termin"]
)

# ---------------------------
# Kalenderdaten laden
# ---------------------------
with st.spinner("Lade Kalenderdaten..."):
    events = fetch_calendar()

if not events:
    st.warning("Keine Kalender-Events gefunden.")
    st.stop()

for e in events:
    info = parse_description(e.get("description", ""))
    e.update(info)

# ---------------------------
# 📅 Kalender Übersicht
# ---------------------------
if page == "📅 Kalender":
    st.title("📅 Kalender Übersicht")

    col1, col2, col3 = st.columns(3)
    today = datetime.now().date()
    week_end = today + timedelta(days=7)

    today_events = [
        e for e in events
        if "start" in e and datetime.fromisoformat(e["start"]["dateTime"].replace("Z", "+00:00")).date() == today
    ]

    week_events = [
        e for e in events
        if "start" in e and today <= datetime.fromisoformat(e["start"]["dateTime"].replace("Z", "+00:00")).date() <= week_end
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

# ---------------------------
# 👨‍🎓 Schüler Übersicht
# ---------------------------
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

# ---------------------------
# 👨‍🏫 Lehrer Übersicht
# ---------------------------
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


# ---------------------------
# Neue Termin Seite
# ---------------------------
if page == "➕ Neuer Termin":
    st.title("➕ Neuen Termin erstellen")

    with st.form("create_event_form"):
        new_summary = st.text_input("Titel des Termins", "Neuer Termin")
        new_teacher = st.text_input("Lehrer", "")
        new_student = st.text_input("Schüler", "")
        new_topic = st.text_input("Thema", "")
        new_start = st.date_input("Startdatum", datetime.now().date())
        new_start_time = st.time_input("Startzeit", datetime.now().time())
        new_end = st.date_input("Enddatum", datetime.now().date())
        new_end_time = st.time_input("Endzeit", (datetime.now() + timedelta(hours=1)).time())

        submit = st.form_submit_button("Termin erstellen")

    if submit:
        if not (new_teacher and new_student and new_topic):
            st.error("Bitte Lehrer, Schüler und Thema ausfüllen!")
        else:
            start_dt = datetime.combine(new_start, new_start_time)
            end_dt = datetime.combine(new_end, new_end_time)

            description = f"Lehrer: {new_teacher}\nSchüler: {new_student}\nThema: {new_topic}"
            payload = {
                "type": "create",
                "summary": new_summary,
                "description": description,
                "start": start_dt.isoformat(),
                "end": end_dt.isoformat(),
            }

            data = api_request(payload=payload)
            if data:
                st.success("✅ Termin erfolgreich erstellt!")
                st.balloons()
                st.cache_data.clear()
            else:
                st.error("Fehler beim Erstellen des Termins.")

# ---------------------------
# Footer
# ---------------------------
st.sidebar.markdown("---")
st.sidebar.info(f"""
**Nachhilfe Dashboard**  
Version 2.2 – mit Terminerstellung  
Letzte Aktualisierung: {datetime.now().strftime("%d.%m.%Y %H:%M")}
""")
