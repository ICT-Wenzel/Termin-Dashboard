import React, { useState, useEffect } from 'react';
import { Calendar, Users, BookOpen, Plus, RefreshCw, AlertCircle, CheckCircle } from 'lucide-react';

const NachhilfeDashboard = () => {
  const [activeTab, setActiveTab] = useState('calendar');
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [debugMode, setDebugMode] = useState(false);
  const [lastResponse, setLastResponse] = useState(null);

  // Mock API URL - ersetzen Sie dies mit Ihrer echten API
  const API_URL = 'https://your-api-endpoint.com/webhook';

  // Funktion zum Parsen der Event-Beschreibung
  const parseDescription = (description) => {
    const data = {
      lehrer: 'N/A',
      schueler: 'N/A',
      thema: 'N/A',
      kontaktSchueler: 'N/A',
      kontaktLehrer: 'N/A'
    };

    if (!description) return data;

    const lines = description.split('\n');
    lines.forEach(line => {
      if (line.includes('Lehrer:')) data.lehrer = line.split('Lehrer:')[1]?.trim() || 'N/A';
      if (line.includes('Schüler:')) data.schueler = line.split('Schüler:')[1]?.trim() || 'N/A';
      if (line.includes('Thema:')) data.thema = line.split('Thema:')[1]?.trim() || 'N/A';
      if (line.includes('Kontakt Schüler:')) data.kontaktSchueler = line.split('Kontakt Schüler:')[1]?.trim() || 'N/A';
      if (line.includes('Kontakt Lehrer:')) data.kontaktLehrer = line.split('Kontakt Lehrer:')[1]?.trim() || 'N/A';
    });

    return data;
  };

  // Mock-Daten für Entwicklung
  const getMockData = () => {
    const mockEvents = [
      {
        id: '1',
        summary: 'Mathematik Nachhilfe - Anna Schmidt',
        description: 'Lehrer: Max Müller\nSchüler: Anna Schmidt\nThema: Quadratische Gleichungen\nKontakt Schüler: anna@email.com\nKontakt Lehrer: max@email.com',
        start: new Date('2025-11-07T10:00:00').toISOString(),
        end: new Date('2025-11-07T11:00:00').toISOString(),
        htmlLink: 'https://calendar.google.com/event1'
      },
      {
        id: '2',
        summary: 'Deutsch Nachhilfe - Tom Weber',
        description: 'Lehrer: Sarah Klein\nSchüler: Tom Weber\nThema: Textanalyse\nKontakt Schüler: tom@email.com\nKontakt Lehrer: sarah@email.com',
        start: new Date('2025-11-07T14:00:00').toISOString(),
        end: new Date('2025-11-07T15:00:00').toISOString(),
        htmlLink: 'https://calendar.google.com/event2'
      },
      {
        id: '3',
        summary: 'Physik Nachhilfe - Lisa Bauer',
        description: 'Lehrer: Max Müller\nSchüler: Lisa Bauer\nThema: Mechanik\nKontakt Schüler: lisa@email.com\nKontakt Lehrer: max@email.com',
        start: new Date('2025-11-08T09:00:00').toISOString(),
        end: new Date('2025-11-08T10:00:00').toISOString(),
        htmlLink: 'https://calendar.google.com/event3'
      },
      {
        id: '4',
        summary: 'Englisch Nachhilfe - Anna Schmidt',
        description: 'Lehrer: Sarah Klein\nSchüler: Anna Schmidt\nThema: Grammar\nKontakt Schüler: anna@email.com\nKontakt Lehrer: sarah@email.com',
        start: new Date('2025-11-09T11:00:00').toISOString(),
        end: new Date('2025-11-09T12:00:00').toISOString(),
        htmlLink: 'https://calendar.google.com/event4'
      },
      {
        id: '5',
        summary: 'Chemie Nachhilfe - Tom Weber',
        description: 'Lehrer: Max Müller\nSchüler: Tom Weber\nThema: Periodensystem\nKontakt Schüler: tom@email.com\nKontakt Lehrer: max@email.com',
        start: new Date('2025-11-10T15:00:00').toISOString(),
        end: new Date('2025-11-10T16:00:00').toISOString(),
        htmlLink: 'https://calendar.google.com/event5'
      }
    ];

    return mockEvents.map(event => ({
      ...event,
      ...parseDescription(event.description)
    }));
  };

  // API-Daten laden
  const fetchEvents = async () => {
    setLoading(true);
    setError(null);

    try {
      // Für Entwicklung: Mock-Daten verwenden
      const mockData = getMockData();
      setEvents(mockData);
      setLastResponse({ type: 'mock', data: mockData });
      setLoading(false);
      return;

      // Echter API-Call (auskommentiert für Entwicklung)
      /*
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type: 'calendar' })
      });

      if (!response.ok) throw new Error('API-Fehler');

      const data = await response.json();
      setLastResponse(data);

      let rawEvents = data.events || data.items || data.data || [];
      
      const parsedEvents = rawEvents.map(event => ({
        ...event,
        ...parseDescription(event.description || event.desc || '')
      }));

      setEvents(parsedEvents);
      */
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEvents();
  }, []);

  const getStats = () => {
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const next7Days = new Date(today);
    next7Days.setDate(next7Days.getDate() + 7);

    const todayEvents = events.filter(e => {
      const eventDate = new Date(e.start);
      return eventDate >= today && eventDate < new Date(today.getTime() + 86400000);
    });

    const next7DaysEvents = events.filter(e => {
      const eventDate = new Date(e.start);
      return eventDate >= today && eventDate < next7Days;
    });

    return {
      total: events.length,
      today: todayEvents.length,
      next7Days: next7DaysEvents.length
    };
  };

  const formatDate = (isoString) => {
    const date = new Date(isoString);
    return date.toLocaleString('de-DE', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getUniqueSchueler = () => [...new Set(events.map(e => e.schueler).filter(s => s !== 'N/A'))].sort();
  const getUniqueLehrer = () => [...new Set(events.map(e => e.lehrer).filter(l => l !== 'N/A'))].sort();

  const createEvent = async (eventData) => {
    try {
      const description = `Lehrer: ${eventData.lehrer}
Schüler: ${eventData.schueler}
Thema: ${eventData.thema}
Kontakt Schüler: ${eventData.kontaktSchueler}
Kontakt Lehrer: ${eventData.kontaktLehrer}`;

      const newEvent = {
        id: Date.now().toString(),
        summary: eventData.summary,
        description: description,
        start: eventData.start,
        end: eventData.end,
        htmlLink: '#',
        ...parseDescription(description)
      };

      setEvents([...events, newEvent]);
      return { success: true };
    } catch (err) {
      return { success: false, error: err.message };
    }
  };

  const stats = getStats();

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      {/* Header */}
      <div className="bg-white shadow-lg border-b-4 border-indigo-600">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                Nachhilfe Dashboard
              </h1>
              <p className="text-gray-600 mt-1">Termine verwalten und organisieren</p>
            </div>
            <div className="flex gap-3 items-center">
              <label className="flex items-center gap-2 px-3 py-2 bg-gray-100 rounded-lg text-sm text-gray-700 hover:bg-gray-200 transition-colors cursor-pointer">
                <input
                  type="checkbox"
                  checked={debugMode}
                  onChange={(e) => setDebugMode(e.target.checked)}
                  className="rounded border-gray-300"
                />
                Debug Modus
              </label>
              <button
                onClick={fetchEvents}
                disabled={loading}
                className="flex items-center gap-2 px-5 py-2 bg-gradient-to-r from-indigo-600 to-indigo-700 text-white rounded-lg hover:from-indigo-700 hover:to-indigo-800 shadow-md hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                Aktualisieren
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Navigation */}
        <div className="bg-white rounded-xl shadow-lg mb-8 p-2 flex gap-2 border border-gray-200">
          <button
            onClick={() => setActiveTab('calendar')}
            className={`flex items-center gap-2 px-6 py-3 rounded-lg font-medium transition-all ${
              activeTab === 'calendar' 
                ? 'bg-gradient-to-r from-indigo-600 to-indigo-700 text-white shadow-md' 
                : 'text-gray-700 hover:bg-gray-100'
            }`}
          >
            <Calendar className="w-5 h-5" />
            Kalender
          </button>
          <button
            onClick={() => setActiveTab('schueler')}
            className={`flex items-center gap-2 px-6 py-3 rounded-lg font-medium transition-all ${
              activeTab === 'schueler' 
                ? 'bg-gradient-to-r from-indigo-600 to-indigo-700 text-white shadow-md' 
                : 'text-gray-700 hover:bg-gray-100'
            }`}
          >
            <Users className="w-5 h-5" />
            Schüler
          </button>
          <button
            onClick={() => setActiveTab('lehrer')}
            className={`flex items-center gap-2 px-6 py-3 rounded-lg font-medium transition-all ${
              activeTab === 'lehrer' 
                ? 'bg-gradient-to-r from-indigo-600 to-indigo-700 text-white shadow-md' 
                : 'text-gray-700 hover:bg-gray-100'
            }`}
          >
            <BookOpen className="w-5 h-5" />
            Lehrer
          </button>
          <button
            onClick={() => setActiveTab('create')}
            className={`flex items-center gap-2 px-6 py-3 rounded-lg font-medium transition-all ${
              activeTab === 'create' 
                ? 'bg-gradient-to-r from-indigo-600 to-indigo-700 text-white shadow-md' 
                : 'text-gray-700 hover:bg-gray-100'
            }`}
          >
            <Plus className="w-5 h-5" />
            Neuer Termin
          </button>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border-l-4 border-red-500 rounded-lg p-5 mb-8 flex items-start gap-3 shadow-md">
            <AlertCircle className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="font-semibold text-red-900 text-lg">Fehler aufgetreten</h3>
              <p className="text-red-700 mt-1">{error}</p>
            </div>
          </div>
        )}

        {/* Debug Panel */}
        {debugMode && lastResponse && (
          <div className="bg-gray-900 text-green-400 rounded-xl p-6 mb-8 overflow-auto max-h-96 shadow-lg font-mono">
            <div className="text-xs font-semibold text-green-300 mb-2">API Response Debug:</div>
            <pre className="text-xs">{JSON.stringify(lastResponse, null, 2)}</pre>
          </div>
        )}

        {/* Content */}
        {activeTab === 'calendar' && <CalendarView events={events} stats={stats} formatDate={formatDate} />}
        {activeTab === 'schueler' && <SchuelerView events={events} schueler={getUniqueSchueler()} formatDate={formatDate} />}
        {activeTab === 'lehrer' && <LehrerView events={events} lehrer={getUniqueLehrer()} formatDate={formatDate} />}
        {activeTab === 'create' && <CreateEventView onSubmit={createEvent} setActiveTab={setActiveTab} />}
      </div>
    </div>
  );
};

// Kalender-Ansicht
const CalendarView = ({ events, stats, formatDate }) => {
  return (
    <div>
      {/* Statistiken */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-xl p-8 shadow-xl transform hover:scale-105 transition-transform">
          <div className="text-5xl font-bold mb-2">{stats.total}</div>
          <div className="text-blue-100 text-lg">Termine gesamt</div>
        </div>
        <div className="bg-gradient-to-br from-green-500 to-green-600 text-white rounded-xl p-8 shadow-xl transform hover:scale-105 transition-transform">
          <div className="text-5xl font-bold mb-2">{stats.today}</div>
          <div className="text-green-100 text-lg">Termine heute</div>
        </div>
        <div className="bg-gradient-to-br from-purple-500 to-purple-600 text-white rounded-xl p-8 shadow-xl transform hover:scale-105 transition-transform">
          <div className="text-5xl font-bold mb-2">{stats.next7Days}</div>
          <div className="text-purple-100 text-lg">Nächste 7 Tage</div>
        </div>
      </div>

      {/* Tabelle */}
      <div className="bg-white rounded-xl shadow-lg overflow-hidden border border-gray-200">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gradient-to-r from-indigo-600 to-indigo-700 text-white">
              <tr>
                <th className="px-6 py-4 text-left font-semibold">Datum</th>
                <th className="px-6 py-4 text-left font-semibold">Lehrer</th>
                <th className="px-6 py-4 text-left font-semibold">Schüler</th>
                <th className="px-6 py-4 text-left font-semibold">Thema</th>
                <th className="px-6 py-4 text-left font-semibold">Kontakt Schüler</th>
                <th className="px-6 py-4 text-left font-semibold">Kontakt Lehrer</th>
                <th className="px-6 py-4 text-left font-semibold">Titel</th>
                <th className="px-6 py-4 text-left font-semibold">Link</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {events.map((event, idx) => (
                <tr key={event.id || idx} className="hover:bg-indigo-50 transition-colors">
                  <td className="px-6 py-4 text-sm text-gray-900">{formatDate(event.start)}</td>
                  <td className="px-6 py-4 text-sm text-gray-900 font-medium">{event.lehrer}</td>
                  <td className="px-6 py-4 text-sm text-gray-900 font-medium">{event.schueler}</td>
                  <td className="px-6 py-4 text-sm text-gray-700">{event.thema}</td>
                  <td className="px-6 py-4 text-sm text-gray-600">{event.kontaktSchueler}</td>
                  <td className="px-6 py-4 text-sm text-gray-600">{event.kontaktLehrer}</td>
                  <td className="px-6 py-4 text-sm text-gray-700">{event.summary}</td>
                  <td className="px-6 py-4 text-sm">
                    {event.htmlLink && event.htmlLink !== '#' && (
                      <a
                        href={event.htmlLink}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center px-3 py-1 bg-indigo-100 text-indigo-700 rounded-lg hover:bg-indigo-200 transition-colors font-medium"
                      >
                        Öffnen
                      </a>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

// Schüler-Ansicht
const SchuelerView = ({ events, schueler, formatDate }) => {
  const [selectedSchueler, setSelectedSchueler] = useState('');
  const filteredEvents = selectedSchueler 
    ? events.filter(e => e.schueler === selectedSchueler)
    : [];

  return (
    <div>
      <div className="bg-white rounded-xl shadow-lg p-8 mb-8 border border-gray-200">
        <label className="block text-lg font-semibold text-gray-800 mb-3">
          Schüler auswählen
        </label>
        <select
          value={selectedSchueler}
          onChange={(e) => setSelectedSchueler(e.target.value)}
          className="w-full px-5 py-3 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-gray-900 text-lg transition-all"
        >
          <option value="">Bitte wählen...</option>
          {schueler.map(s => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
      </div>

      {selectedSchueler && (
        <div className="bg-white rounded-xl shadow-lg overflow-hidden border border-gray-200">
          <div className="bg-gradient-to-r from-indigo-600 to-indigo-700 text-white px-8 py-6">
            <h2 className="text-2xl font-bold">Termine für {selectedSchueler}</h2>
            <p className="text-indigo-100 mt-1">{filteredEvents.length} Termine gefunden</p>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b-2 border-gray-200">
                <tr>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">Datum</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">Lehrer</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">Thema</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">Titel</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">Link</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {filteredEvents.map((event, idx) => (
                  <tr key={event.id || idx} className="hover:bg-indigo-50 transition-colors">
                    <td className="px-6 py-4 text-sm text-gray-900">{formatDate(event.start)}</td>
                    <td className="px-6 py-4 text-sm text-gray-900 font-medium">{event.lehrer}</td>
                    <td className="px-6 py-4 text-sm text-gray-700">{event.thema}</td>
                    <td className="px-6 py-4 text-sm text-gray-700">{event.summary}</td>
                    <td className="px-6 py-4 text-sm">
                      {event.htmlLink && event.htmlLink !== '#' && (
                        <a
                          href={event.htmlLink}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center px-3 py-1 bg-indigo-100 text-indigo-700 rounded-lg hover:bg-indigo-200 transition-colors font-medium"
                        >
                          Öffnen
                        </a>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

// Lehrer-Ansicht
const LehrerView = ({ events, lehrer, formatDate }) => {
  const [selectedLehrer, setSelectedLehrer] = useState('');
  const filteredEvents = selectedLehrer 
    ? events.filter(e => e.lehrer === selectedLehrer)
    : [];

  return (
    <div>
      <div className="bg-white rounded-xl shadow-lg p-8 mb-8 border border-gray-200">
        <label className="block text-lg font-semibold text-gray-800 mb-3">
          Lehrer auswählen
        </label>
        <select
          value={selectedLehrer}
          onChange={(e) => setSelectedLehrer(e.target.value)}
          className="w-full px-5 py-3 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-gray-900 text-lg transition-all"
        >
          <option value="">Bitte wählen...</option>
          {lehrer.map(l => (
            <option key={l} value={l}>{l}</option>
          ))}
        </select>
      </div>

      {selectedLehrer && (
        <div className="bg-white rounded-xl shadow-lg overflow-hidden border border-gray-200">
          <div className="bg-gradient-to-r from-indigo-600 to-indigo-700 text-white px-8 py-6">
            <h2 className="text-2xl font-bold">Termine für {selectedLehrer}</h2>
            <p className="text-indigo-100 mt-1">{filteredEvents.length} Termine gefunden</p>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b-2 border-gray-200">
                <tr>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">Datum</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">Schüler</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">Thema</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">Titel</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">Link</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {filteredEvents.map((event, idx) => (
                  <tr key={event.id || idx} className="hover:bg-indigo-50 transition-colors">
                    <td className="px-6 py-4 text-sm text-gray-900">{formatDate(event.start)}</td>
                    <td className="px-6 py-4 text-sm text-gray-900 font-medium">{event.schueler}</td>
                    <td className="px-6 py-4 text-sm text-gray-700">{event.thema}</td>
                    <td className="px-6 py-4 text-sm text-gray-700">{event.summary}</td>
                    <td className="px-6 py-4 text-sm">
                      {event.htmlLink && event.htmlLink !== '#' && (
                        <a
                          href={event.htmlLink}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center px-3 py-1 bg-indigo-100 text-indigo-700 rounded-lg hover:bg-indigo-200 transition-colors font-medium"
                        >
                          Öffnen
                        </a>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

// Termin-Erstellung
const CreateEventView = ({ onSubmit, setActiveTab }) => {
  const [formData, setFormData] = useState({
    summary: '',
    schueler: '',
    lehrer: '',
    thema: '',
    kontaktSchueler: '',
    kontaktLehrer: '',
    startDate: new Date().toISOString().split('T')[0],
    startTime: '08:00',
    endDate: new Date().toISOString().split('T')[0],
    endTime: '09:00'
  });

  const [message, setMessage] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const startISO = `${formData.startDate}T${formData.startTime}:00`;
    const endISO = `${formData.endDate}T${formData.endTime}:00`;

    const result = await onSubmit({
      ...formData,
      start: startISO,
      end: endISO
    });

    if (result.success) {
      setMessage({ type: 'success', text: 'Termin erfolgreich erstellt!' });
      setTimeout(() => {
        setActiveTab('calendar');
      }, 2000);
    } else {
      setMessage({ type: 'error', text: `Fehler: ${result.error}` });
    }
  };

  return (
    <div className="max-w-3xl mx-auto">
      <div className="bg-white rounded-xl shadow-lg p-8 border border-gray-200">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Neuen Termin erstellen</h2>
        <p className="text-gray-600 mb-8">Füllen Sie alle Felder aus, um einen neuen Nachhilfe-Termin anzulegen</p>

        {message && (
          <div className={`mb-6 p-4 rounded-lg flex items-center gap-3 ${
            message.type === 'success' 
              ? 'bg-green-50 border-l-4 border-green-500' 
              : 'bg-red-50 border-l-4 border-red-500'
          }`}>
            {message.type === 'success' ? (
              <CheckCircle className="w-6 h-6 text-green-600" />
            ) : (
              <AlertCircle className="w-6 h-6 text-red-600" />
            )}
            <span className={message.type === 'success' ? 'text-green-700 font-medium' : 'text-red-700 font-medium'}>
              {message.text}
            </span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">Titel *</label>
            <input
              type="text"
              required
              value={formData.summary}
              onChange={(e) => setFormData({...formData, summary: e.target.value})}
              className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all"
              placeholder="z.B. Mathematik Nachhilfe - Max Mustermann"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Schüler *</label>
              <input
                type="text"
                required
                value={formData.schueler}
                onChange={(e) => setFormData({...formData, schueler: e.target.value})}
                className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all"
                placeholder="Name des Schülers"
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Lehrer *</label>
              <input
                type="text"
                required
                value={formData.lehrer}
                onChange={(e) => setFormData({...formData, lehrer: e.target.value})}
                className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all"
                placeholder="Name des Lehrers"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">Thema *</label>
            <input
              type="text"
              required
              value={formData.thema}
              onChange={(e) => setFormData({...formData, thema: e.target.value})}
              className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all"
              placeholder="z.B. Quadratische Gleichungen"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Kontakt Schüler</label>
              <input
                type="email"
                value={formData.kontaktSchueler}
                onChange={(e) => setFormData({...formData, kontaktSchueler: e.target.value})}
                className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all"
                placeholder="schueler@email.com"
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Kontakt Lehrer</label>
              <input
                type="email"
                value={formData.kontaktLehrer}
                onChange={(e) => setFormData({...formData, kontaktLehrer: e.target.value})}
                className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all"
                placeholder="lehrer@email.com"
              />
            </div>
          </div>

          <div className="border-t-2 border-gray-200 pt-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Zeitraum</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Startdatum *</label>
                <input
                  type="date"
                  required
                  value={formData.startDate}
                  onChange={(e) => setFormData({...formData, startDate: e.target.value})}
                  className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Startzeit *</label>
                <input
                  type="time"
                  required
                  value={formData.startTime}
                  onChange={(e) => setFormData({...formData, startTime: e.target.value})}
                  className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Enddatum *</label>
                <input
                  type="date"
                  required
                  value={formData.endDate}
                  onChange={(e) => setFormData({...formData, endDate: e.target.value})}
                  className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Endzeit *</label>
                <input
                  type="time"
                  required
                  value={formData.endTime}
                  onChange={(e) => setFormData({...formData, endTime: e.target.value})}
                  className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all"
                />
              </div>
            </div>
          </div>

          <div className="flex gap-4 pt-4">
            <button
              type="submit"
              className="flex-1 px-6 py-4 bg-gradient-to-r from-indigo-600 to-indigo-700 text-white rounded-lg font-semibold hover:from-indigo-700 hover:to-indigo-800 shadow-md hover:shadow-lg transition-all text-lg"
            >
              Termin erstellen
            </button>
            <button
              type="button"
              onClick={() => setActiveTab('calendar')}
              className="px-6 py-4 border-2 border-gray-300 text-gray-700 rounded-lg font-semibold hover:bg-gray-50 transition-all"
            >
              Abbrechen
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default NachhilfeDashboard;