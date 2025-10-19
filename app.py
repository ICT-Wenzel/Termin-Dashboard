import streamlit as st
import requests
from datetime import datetime, timedelta
import pandas as pd
from typing import List, Dict
import json

# Page Config
st.set_page_config(
    page_title="Nachhilfe Dashboard",
    page_icon="📚",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .student-card, .teacher-card {
        background: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .event-item {
        background: white;
        padding: 15px;
        border-radius: 8px;
        margin: 8px 0;
        border-left: 4px solid #1f77b4;
    }
    .stat-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    .error-box {
        background: #ffe6e6;
        border-left: 4px solid #ff4444;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Load Secrets
try:
    API_BASE_URL = st.secrets["api"]["base_url"]
except Exception as e:
    st.error(f"""
    ### ⚠️ API URL nicht konfiguriert!
    
    Bitte erstelle eine `.streamlit/secrets.toml` Datei mit folgendem Inhalt:
    
    ```toml
    [api]
    base_url = "https://your-n8n-instance.com/webhook"
    ```
    
    Oder füge die Secrets in der Streamlit Cloud hinzu.
    """)
    st.stop()

# API Functions
def api_request(params=None):
    """Generische API-Anfrage"""
    try:
        url = API_BASE_URL
        
        # Debug-Info
        with st.sidebar:
            st.write(f"🔗 **API Call:** `{url}`")
            if params:
                st.write(f"📝 **Params:** {params}")
        
        response = requests.get(url, params=params, timeout=15)
        
        # Debug: Response Status
        with st.sidebar:
            if response.status_code == 200:
                st.success(f"✅ Status: {response.status_code}")
            else:
                st.error(f"❌ Status: {response.status_code}")
                st.error(f"Response: {response.text[:200]}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Debug: Zeige Response-Struktur
            with st.sidebar.expander("📦 API Response (Debug)"):
                st.json(data)
            
            return data
        else:
            st.error(f"API Fehler: Status {response.status_code}")
            return None
            
    except requests.exceptions.Timeout:
        st.error("⏱️ Timeout: API antwortet nicht")
        return None
    except requests.exceptions.ConnectionError:
        st.error("🔌 Verbindungsfehler: Kann API nicht erreichen")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Request-Fehler: {str(e)}")
        return None
    except json.JSONDecodeError as e:
        st.error(f"📋 JSON Parse-Fehler: {str(e)}")
        return None

@st.cache_data(ttl=300)
def fetch_calendar():
    """Holt alle Kalender-Events"""
    data = api_request(params={"type": "calendar"})
    if data:
        # Falls Response ein Objekt mit "events" oder "calendar" key ist
        if isinstance(data, dict):
            return data.get("calendar", data.get("events", []))
        # Falls Response direkt ein Array ist
        elif isinstance(data, list):
            return data
    return []

@st.cache_data(ttl=600)
def fetch_students():
    """Holt alle Schüler"""
    data = api_request(params={"type": "students"})
    if data:
        # Falls Response ein Objekt mit "students" key ist
        if isinstance(data, dict):
            return data.get("students", [])
        # Falls Response direkt ein Array ist
        elif isinstance(data, list):
            return data
    return []

@st.cache_data(ttl=600)
def fetch_teachers():
    """Holt alle Lehrer"""
    data = api_request(params={"type": "teachers"})
    if data:
        # Falls Response ein Objekt mit "teachers" key ist
        if isinstance(data, dict):
            return data.get("teachers", [])
        # Falls Response direkt ein Array ist
        elif isinstance(data, list):
            return data
    return []

@st.cache_data(ttl=300)
def fetch_student_data(student_name):
    """Holt alle Daten zu einem spezifischen Schüler"""
    data = api_request(params={"type": "student", "name": student_name})
    return data if data else {"info": {}, "events": []}

@st.cache_data(ttl=300)
def fetch_teacher_data(teacher_name):
    """Holt alle Daten zu einem spezifischen Lehrer"""
    data = api_request(params={"type": "teacher", "name": teacher_name})
    return data if data else {"info": {}, "events": []}

def format_datetime(dt_string):
    """Formatiert ISO DateTime String"""
    if not dt_string:
        return "N/A"
    try:
        dt = datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
        return dt.strftime("%d.%m.%Y %H:%M")
    except:
        return dt_string

# Sidebar Navigation
st.sidebar.title("📚 Nachhilfe Dashboard")

# Refresh Button
if st.sidebar.button("🔄 Daten aktualisieren"):
    st.cache_data.clear()
    st.rerun()

page = st.sidebar.radio(
    "Navigation",
    ["📅 Kalender", "👨‍🎓 Schüler", "👨‍🏫 Lehrer"]
)

# PAGE 1: KALENDER
if page == "📅 Kalender":
    st.title("📅 Kalender Übersicht")
    
    with st.spinner("Lade Kalenderdaten..."):
        calendar_events = fetch_calendar()
        students = fetch_students()
        teachers = fetch_teachers()
    
    if not calendar_events:
        st.warning("Keine Kalender-Events gefunden.")
    else:
        # Stats Row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="stat-box">
                <h2>{len(calendar_events)}</h2>
                <p>Termine Gesamt</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            today_events = []
            for e in calendar_events:
                try:
                    event_date = datetime.fromisoformat(e.get("start", "").replace('Z', '+00:00')).date()
                    if event_date == datetime.now().date():
                        today_events.append(e)
                except:
                    pass
            
            st.markdown(f"""
            <div class="stat-box">
                <h2>{len(today_events)}</h2>
                <p>Heute</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            week_events = []
            week_end = datetime.now() + timedelta(days=7)
            for e in calendar_events:
                try:
                    event_date = datetime.fromisoformat(e.get("start", "").replace('Z', '+00:00'))
                    if datetime.now() < event_date < week_end:
                        week_events.append(e)
                except:
                    pass
            
            st.markdown(f"""
            <div class="stat-box">
                <h2>{len(week_events)}</h2>
                <p>Diese Woche</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="stat-box">
                <h2>{len(students)}</h2>
                <p>Aktive Schüler</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Filter Options
        col1, col2 = st.columns(2)
        with col1:
            unique_subjects = list(set([e.get("subject", "Unbekannt") for e in calendar_events if e.get("subject")]))
            filter_subject = st.selectbox(
                "Fach filtern",
                ["Alle"] + sorted(unique_subjects)
            )
        with col2:
            filter_teacher = st.selectbox(
                "Lehrer filtern",
                ["Alle"] + [t.get("name", "Unbekannt") for t in teachers]
            )
        
        # Filter Events
        filtered_events = calendar_events
        if filter_subject != "Alle":
            filtered_events = [e for e in filtered_events if e.get("subject") == filter_subject]
        if filter_teacher != "Alle":
            filtered_events = [e for e in filtered_events if e.get("teacher") == filter_teacher]
        
        # Sort events by start time
        try:
            filtered_events = sorted(filtered_events, key=lambda x: x.get("start", ""))
        except:
            pass
        
        # Display Events
        st.subheader(f"Termine ({len(filtered_events)})")
        
        for event in filtered_events:
            st.markdown(f"""
            <div class="event-item">
                <h4>{event.get('summary', 'Termin')}</h4>
                <p><strong>🕐 Zeit:</strong> {format_datetime(event.get('start', ''))} - {format_datetime(event.get('end', ''))}</p>
                <p><strong>👨‍🎓 Schüler:</strong> {event.get('student', 'N/A')} | <strong>👨‍🏫 Lehrer:</strong> {event.get('teacher', 'N/A')}</p>
                <p><strong>📚 Fach:</strong> {event.get('subject', 'N/A')}</p>
                <p><strong>📝 Thema:</strong> {event.get('description', 'Keine Beschreibung')}</p>
            </div>
            """, unsafe_allow_html=True)

# PAGE 2: SCHÜLER
elif page == "👨‍🎓 Schüler":
    st.title("👨‍🎓 Schüler Übersicht")
    
    with st.spinner("Lade Schülerliste..."):
        students = fetch_students()
    
    if not students:
        st.warning("Keine Schüler gefunden.")
    else:
        # Student Selection
        selected_student = st.selectbox(
            "Schüler auswählen",
            [s.get("name", "Unbekannt") for s in students]
        )
        
        # Fetch detailed student data
        with st.spinner(f"Lade Daten von {selected_student}..."):
            student_data = fetch_student_data(selected_student)
        
        # Student Info aus der Liste
        student_info = next((s for s in students if s.get("name") == selected_student), {})
        
        # Merge mit API-Daten falls vorhanden
        if student_data and "info" in student_data:
            student_info.update(student_data["info"])
        
        # Events aus API-Daten
        student_events = student_data.get("events", []) if student_data else []
        
        if student_info:
            # Student Info Card
            col1, col2 = st.columns([1, 2])
            
            with col1:
                subjects = student_info.get('subjects', [])
                subjects_str = ', '.join(subjects) if isinstance(subjects, list) else str(subjects)
                
                st.markdown(f"""
                <div class="student-card">
                    <h2>{student_info.get('name', 'Unbekannt')}</h2>
                    <p><strong>📧 Email:</strong> {student_info.get('email', 'N/A')}</p>
                    <p><strong>📱 Telefon:</strong> {student_info.get('phone', 'N/A')}</p>
                    <p><strong>🎓 Klasse:</strong> {student_info.get('grade', 'N/A')}</p>
                    <p><strong>📚 Fächer:</strong> {subjects_str}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                # Stats for this student
                upcoming_events = []
                for e in student_events:
                    try:
                        event_date = datetime.fromisoformat(e.get("start", "").replace('Z', '+00:00'))
                        if event_date > datetime.now():
                            upcoming_events.append(e)
                    except:
                        pass
                
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("Termine Gesamt", len(student_events))
                with col_b:
                    st.metric("Kommende Termine", len(upcoming_events))
                with col_c:
                    subject_count = len(subjects) if isinstance(subjects, list) else 0
                    st.metric("Fächer", subject_count)
            
            st.markdown("---")
            
            # Calendar View for Student
            st.subheader(f"📅 Termine von {student_info.get('name', 'Unbekannt')}")
            
            if student_events:
                try:
                    sorted_events = sorted(student_events, key=lambda x: x.get("start", ""), reverse=True)[:10]
                except:
                    sorted_events = student_events[:10]
                
                for event in sorted_events:
                    st.markdown(f"""
                    <div class="event-item">
                        <h4>{event.get('summary', 'Termin')}</h4>
                        <p><strong>🕐 Zeit:</strong> {format_datetime(event.get('start', ''))}</p>
                        <p><strong>👨‍🏫 Lehrer:</strong> {event.get('teacher', 'N/A')}</p>
                        <p><strong>📚 Fach:</strong> {event.get('subject', 'N/A')}</p>
                        <p><strong>📝 Thema:</strong> {event.get('description', 'Keine Beschreibung')}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Keine Termine für diesen Schüler gefunden.")
            
            # Next Up Overview
            st.markdown("---")
            st.subheader("🔜 Nächste Termine")
            
            if upcoming_events:
                try:
                    upcoming_events = sorted(upcoming_events, key=lambda x: x.get("start", ""))[:5]
                except:
                    upcoming_events = upcoming_events[:5]
                
                df_upcoming = pd.DataFrame([
                    {
                        "Datum": format_datetime(e.get("start", "")),
                        "Lehrer": e.get("teacher", "N/A"),
                        "Fach": e.get("subject", "N/A"),
                        "Thema": e.get("description", "Keine Beschreibung")
                    }
                    for e in upcoming_events
                ])
                st.dataframe(df_upcoming, use_container_width=True)
            else:
                st.info("Keine kommenden Termine.")

# PAGE 3: LEHRER
elif page == "👨‍🏫 Lehrer":
    st.title("👨‍🏫 Lehrer Übersicht")
    
    with st.spinner("Lade Lehrerliste..."):
        teachers = fetch_teachers()
    
    if not teachers:
        st.warning("Keine Lehrer gefunden.")
    else:
        # Teacher Selection
        selected_teacher = st.selectbox(
            "Lehrer auswählen",
            [t.get("name", "Unbekannt") for t in teachers]
        )
        
        # Fetch detailed teacher data
        with st.spinner(f"Lade Daten von {selected_teacher}..."):
            teacher_data = fetch_teacher_data(selected_teacher)
        
        # Teacher Info aus der Liste
        teacher_info = next((t for t in teachers if t.get("name") == selected_teacher), {})
        
        # Merge mit API-Daten falls vorhanden
        if teacher_data and "info" in teacher_data:
            teacher_info.update(teacher_data["info"])
        
        # Events aus API-Daten
        teacher_events = teacher_data.get("events", []) if teacher_data else []
        
        if teacher_info:
            # Teacher Info Card
            col1, col2 = st.columns([1, 2])
            
            with col1:
                subjects = teacher_info.get('subjects', [])
                subjects_str = ', '.join(subjects) if isinstance(subjects, list) else str(subjects)
                
                st.markdown(f"""
                <div class="teacher-card">
                    <h2>{teacher_info.get('name', 'Unbekannt')}</h2>
                    <p><strong>📧 Email:</strong> {teacher_info.get('email', 'N/A')}</p>
                    <p><strong>📱 Telefon:</strong> {teacher_info.get('phone', 'N/A')}</p>
                    <p><strong>📚 Fächer:</strong> {subjects_str}</p>
                    <p><strong>💼 Erfahrung:</strong> {teacher_info.get('experience', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                # Stats for this teacher
                upcoming_events = []
                for e in teacher_events:
                    try:
                        event_date = datetime.fromisoformat(e.get("start", "").replace('Z', '+00:00'))
                        if event_date > datetime.now():
                            upcoming_events.append(e)
                    except:
                        pass
                
                unique_students = len(set([e.get("student", "") for e in teacher_events if e.get("student")]))
                
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("Termine Gesamt", len(teacher_events))
                with col_b:
                    st.metric("Kommende Termine", len(upcoming_events))
                with col_c:
                    st.metric("Schüler", unique_students)
            
            st.markdown("---")
            
            # Calendar View for Teacher
            st.subheader(f"📅 Termine von {teacher_info.get('name', 'Unbekannt')}")
            
            if teacher_events:
                try:
                    sorted_events = sorted(teacher_events, key=lambda x: x.get("start", ""), reverse=True)[:10]
                except:
                    sorted_events = teacher_events[:10]
                
                for event in sorted_events:
                    st.markdown(f"""
                    <div class="event-item">
                        <h4>{event.get('summary', 'Termin')}</h4>
                        <p><strong>🕐 Zeit:</strong> {format_datetime(event.get('start', ''))}</p>
                        <p><strong>👨‍🎓 Schüler:</strong> {event.get('student', 'N/A')}</p>
                        <p><strong>📚 Fach:</strong> {event.get('subject', 'N/A')}</p>
                        <p><strong>📝 Thema:</strong> {event.get('description', 'Keine Beschreibung')}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Keine Termine für diesen Lehrer gefunden.")
            
            # Next Up Overview
            st.markdown("---")
            st.subheader("🔜 Nächste Termine")
            
            if upcoming_events:
                try:
                    upcoming_events = sorted(upcoming_events, key=lambda x: x.get("start", ""))[:5]
                except:
                    upcoming_events = upcoming_events[:5]
                
                df_upcoming = pd.DataFrame([
                    {
                        "Datum": format_datetime(e.get("start", "")),
                        "Schüler": e.get("student", "N/A"),
                        "Fach": e.get("subject", "N/A"),
                        "Thema": e.get("description", "Keine Beschreibung")
                    }
                    for e in upcoming_events
                ])
                st.dataframe(df_upcoming, use_container_width=True)
            else:
                st.info("Keine kommenden Termine.")

# Footer
st.sidebar.markdown("---")
st.sidebar.info(f"""
**Nachhilfefirma Dashboard**  
Version 3.0 - API-basiert  
Letzte Aktualisierung: {datetime.now().strftime("%d.%m.%Y %H:%M")}
""")