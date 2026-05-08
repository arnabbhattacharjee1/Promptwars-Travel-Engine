const { useState, useEffect } = React;

const App = () => {
    // Re-initialize Lucide icons after rendering
    useEffect(() => {
        if (window.lucide) {
            window.lucide.createIcons();
        }
    });

    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);

    const [formData, setFormData] = useState({
        destination: "Kyoto, Japan",
        travel_dates: "2026-10-10 to 2026-10-15",
        traveler_preferences: "Cultural, peaceful, minimal walking, loves traditional tea",
        budget: "$3000 USD",
        constraints: "Must have elevator in hotel, allergic to shellfish"
    });

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const submitPlan = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        setResult(null);

        try {
            const response = await fetch('/api/plan-travel', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            if (!response.ok) {
                throw new Error("Failed to fetch travel plan from the engine.");
            }

            const data = await response.json();
            if (data.error) {
                throw new Error(data.error);
            }
            setResult(data);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="app-container">
            <header className="header">
                <h1 className="title">Travel Planning & Experience Engine</h1>
                <p className="subtitle">Intelligent orchestration tailored to your preferences.</p>
            </header>

            <div className="glass-panel">
                <form onSubmit={submitPlan}>
                    <div className="form-grid">
                        <div className="input-group">
                            <label>Destination <i data-lucide="map-pin" style={{width:'14px'}}></i></label>
                            <input type="text" name="destination" value={formData.destination} onChange={handleInputChange} required />
                        </div>
                        <div className="input-group">
                            <label>Travel Dates <i data-lucide="calendar" style={{width:'14px'}}></i></label>
                            <input type="text" name="travel_dates" value={formData.travel_dates} onChange={handleInputChange} required />
                        </div>
                        <div className="input-group">
                            <label>Budget <i data-lucide="wallet" style={{width:'14px'}}></i></label>
                            <input type="text" name="budget" value={formData.budget} onChange={handleInputChange} required />
                        </div>
                    </div>
                    <div className="form-grid" style={{marginTop: '1.5rem'}}>
                        <div className="input-group">
                            <label>Traveler Preferences</label>
                            <textarea name="traveler_preferences" value={formData.traveler_preferences} onChange={handleInputChange} required></textarea>
                        </div>
                        <div className="input-group">
                            <label>Constraints & Special Requirements</label>
                            <textarea name="constraints" value={formData.constraints} onChange={handleInputChange} required></textarea>
                        </div>
                    </div>
                    
                    <button type="submit" className="btn-primary" disabled={loading}>
                        {loading ? <span className="loading-spinner"></span> : "Generate Orchestrated Travel Plan"}
                    </button>
                    {error && <div style={{color: 'var(--danger)', marginTop: '1rem', textAlign: 'center'}}>{error}</div>}
                </form>
            </div>

            {result && (
                <div className="results-container">
                    <div className="glass-panel">
                        <div className="result-section">
                            <h3><i data-lucide="check-circle" style={{color: 'var(--success)'}}></i> Execution Plan: {result.destination}</h3>
                            <p style={{color: 'var(--text-secondary)'}}>Status: {result.compliance_status || 'Verified'}</p>
                            {result.note && <p style={{color: 'var(--warning)', fontSize: '0.9rem', marginTop: '0.5rem'}}>{result.note}</p>}
                        </div>

                        <div className="form-grid">
                            <div className="result-section">
                                <h3><i data-lucide="home"></i> Accommodation</h3>
                                <p>{result.accommodation}</p>
                            </div>
                            <div className="result-section">
                                <h3><i data-lucide="plane"></i> Transport</h3>
                                <p>{result.transport}</p>
                            </div>
                        </div>

                        <div className="result-section">
                            <h3><i data-lucide="calendar"></i> Itinerary</h3>
                            {result.itinerary && Array.isArray(result.itinerary) ? result.itinerary.map((day, idx) => (
                                <div key={idx} className="itinerary-day">
                                    <div className="day-title">Day {day.day}</div>
                                    <ul style={{paddingLeft: '1.2rem', color: 'var(--text-secondary)'}}>
                                        {Array.isArray(day.activities) ? day.activities.map((act, i) => (
                                            <li key={i} style={{marginBottom: '0.3rem'}}>{act}</li>
                                        )) : <li>{JSON.stringify(day.activities)}</li>}
                                    </ul>
                                </div>
                            )) : <p>Itinerary generated dynamically.</p>}
                        </div>

                        <div className="form-grid">
                            <div className="result-section">
                                <h3><i data-lucide="alert-triangle"></i> Live Alerts & Advisories</h3>
                                {result.live_alerts && Array.isArray(result.live_alerts) && result.live_alerts.map((alert, idx) => (
                                    <span key={idx} className={`tag badge-${alert.severity || 'low'}`}>
                                        {alert.message || JSON.stringify(alert)}
                                    </span>
                                ))}
                                {result.traveler_advisories && Array.isArray(result.traveler_advisories) && result.traveler_advisories.map((adv, idx) => (
                                    <div key={'adv'+idx} style={{marginTop: '0.5rem', color: 'var(--text-secondary)', fontSize: '0.9rem'}}>
                                        • {typeof adv === 'string' ? adv : JSON.stringify(adv)}
                                    </div>
                                ))}
                            </div>
                            <div className="result-section">
                                <h3><i data-lucide="life-buoy"></i> Contingency Plan</h3>
                                {result.contingency_plan && Array.isArray(result.contingency_plan) && result.contingency_plan.map((cp, idx) => (
                                    <div key={idx} style={{marginBottom: '0.5rem', color: 'var(--text-secondary)', borderLeft: '2px solid var(--danger)', paddingLeft: '0.5rem'}}>
                                        {typeof cp === 'string' ? cp : JSON.stringify(cp)}
                                    </div>
                                ))}
                            </div>
                        </div>

                    </div>
                </div>
            )}
        </div>
    );
};

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
