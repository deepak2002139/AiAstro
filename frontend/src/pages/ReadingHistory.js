import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import './ReadingHistory.css';

function ReadingHistory() {
  const [readings, setReadings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchReadingHistory();
  }, []);

  const fetchReadingHistory = async () => {
    try {
      const userId = localStorage.getItem('userId');
      const response = await fetch(
        `${process.env.REACT_APP_API_URL}/astrology/readings?userId=${userId}`
      );

      if (response.ok) {
        const data = await response.json();
        setReadings(Array.isArray(data) ? data : data.content || []);
      } else if (response.status !== 404) {
        setError('Failed to load reading history');
      }
    } catch (err) {
      console.error('Error fetching readings:', err);
      // Fallback to empty array instead of showing error
      setReadings([]);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="reading-history">
        <div className="container">
          <div className="spinner"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="reading-history">
      <div className="container">
        <div className="history-header">
          <h1>Your Reading History 📚</h1>
          <p>View all your previous astrological readings</p>
        </div>

        {error && <div className="alert alert-error">{error}</div>}

        {readings.length === 0 ? (
          <div className="card empty-state">
            <div className="empty-icon">📖</div>
            <h3>No readings yet</h3>
            <p>Start by generating your first astrological reading</p>
            <Link to="/new-reading" className="btn btn-primary">
              Generate Reading
            </Link>
          </div>
        ) : (
          <div className="readings-list">
            {readings.map((reading) => (
              <div key={reading.id} className="card reading-card">
                <div className="reading-card-header">
                  <h3>{reading.name}</h3>
                  <span className="reading-badge">{reading.readingType}</span>
                </div>
                <div className="reading-card-info">
                  <span className="info-item">
                    ♈ {reading.zodiacSign}
                  </span>
                  <span className="info-item">
                    📅 {new Date(reading.birthDate).toLocaleDateString()}
                  </span>
                  <span className="info-item">
                    🕐 {new Date(reading.createdAt || reading.timestamp).toLocaleDateString()}
                  </span>
                </div>
                <div className="reading-card-preview">
                  {(reading.content || reading.reading || 'No content').substring(0, 150)}...
                </div>
                <Link
                  to={`/reading/${reading.id}`}
                  state={{ reading }}
                  className="btn btn-primary"
                >
                  View Full Reading
                </Link>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default ReadingHistory;

