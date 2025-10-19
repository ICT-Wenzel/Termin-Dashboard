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
@st.cache_data(ttl=300)
def fetch_all_data():
    """Holt alle Daten von der API (Kalender, Schüler, Lehrer)"""
    try:
        response = requests.get(f"{API_BASE_URL}/data", timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            # Erwarte folgendes Format:
            # {
            #   "calendar": [...],
            #   "students": [...],
            #   "teachers": [...]
            # }
            
            return {
                "calendar": data.get("calendar", data.get("events", [])),
                "students": data.get("students", []),
                "teachers": data.get("teachers", [])
            }
        else:
            st.error(f"API Fehler: Status {response.status_code}")
            return {"calendar": [], "students": [], "teachers": []}
            
    except requests.exceptions.RequestException as e:
        st.error(f"Verbindungsfehler zur API: {str(e)}")
        return {"calendar": [], "students": [], "teachers": []}
    except json.JSONDecodeError:
        st.error("Fehler beim Parsen der API Antwort")
        return {"calendar": [], "students": [], "teachers": []}

def filter_events_by_person(events, person_name):
    """Filtert Events nach Person (Schüler oder Lehrer)"""
    if not events or not person_name:
        return []
    return [e for e in events if person_name in e.get("student", "") or person_name in e.get("teacher", "")]

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

# Load All Data from API
with st.spinner("Lade Daten von API..."):
    all_data = fetch_all_data()
    calendar_events = all_data.get("calendar", [])
    students = all_data.get("students", [])
    teachers = all_data.get("teachers", [])

# Check if data is loaded
if not calendar_events and not students and not teachers:
    st.error("Keine Daten von der API geladen. Bitte überprüfe deine API-URL und die Verbindung.")
    st.stop()

# PAGE 1: KALENDER
if page == "📅 Kalender":
    st.title("📅 Kalender Übersicht")
    
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
                    if event_date < week_end and event_date > datetime.now():
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
    
    if not students:
        st.warning("Keine Schüler gefunden.")
    else:
        # Student Selection
        selected_student = st.selectbox(
            "Schüler auswählen",
            [s.get("name", "Unbekannt") for s in students]
        )
        
        student = next((s for s in students if s.get("name") == selected_student), None)
        
        if student:
            # Student Info Card
            col1, col2 = st.columns([1, 2])
            
            with col1:
                subjects = student.get('subjects', [])
                subjects_str = ', '.join(subjects) if isinstance(subjects, list) else str(subjects)
                
                st.markdown(f"""
                <div class="student-card">
                    <h2>{student.get('name', 'Unbekannt')}</h2>
                    <p><strong>📧 Email:</strong> {student.get('email', 'N/A')}</p>
                    <p><strong>📱 Telefon:</strong> {student.get('phone', 'N/A')}</p>
                    <p><strong>🎓 Klasse:</strong> {student.get('grade', 'N/A')}</p>
                    <p><strong>📚 Fächer:</strong> {subjects_str}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                # Stats for this student
                student_events = filter_events_by_person(calendar_events, student.get("name", ""))
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
            st.subheader(f"📅 Termine von {student.get('name', 'Unbekannt')}")
            
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
    
    if not teachers:
        st.warning("Keine Lehrer gefunden.")
    else:
        # Teacher Selection
        selected_teacher = st.selectbox(
            "Lehrer auswählen",
            [t.get("name", "Unbekannt") for t in teachers]
        )
        
        teacher = next((t for t in teachers if t.get("name") == selected_teacher), None)
        
        if teacher:
            # Teacher Info Card
            col1, col2 = st.columns([1, 2])
            
            with col1:
                subjects = teacher.get('subjects', [])
                subjects_str = ', '.join(subjects) if isinstance(subjects, list) else str(subjects)
                
                st.markdown(f"""
                <div class="teacher-card">
                    <h2>{teacher.get('name', 'Unbekannt')}</h2>
                    <p><strong>📧 Email:</strong> {teacher.get('email', 'N/A')}</p>
                    <p><strong>📱 Telefon:</strong> {teacher.get('phone', 'N/A')}</p>
                    <p><strong>📚 Fächer:</strong> {subjects_str}</p>
                    <p><strong>💼 Erfahrung:</strong> {teacher.get('experience', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                # Stats for this teacher
                teacher_events = filter_events_by_person(calendar_events, teacher.get("name", ""))
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
            st.subheader(f"📅 Termine von {teacher.get('name', 'Unbekannt')}")
            
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
Version 2.1  
Letzte Aktualisierung: {datetime.now().strftime("%d.%m.%Y %H:%M")}
""")

# API Status
with st.sidebar.expander("🔌 API Status"):
    st.write(f"📅 Kalender Events: {len(calendar_events)}")
    st.write(f"👨‍🎓 Schüler: {len(students)}")
    st.write(f"👨‍🏫 Lehrer: {len(teachers)}")
    st.write(f"🌐 API: {API_BASE_URL}")