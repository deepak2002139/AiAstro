import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import './ReadingResult.css';

function ReadingResult({ onTokensUsed }) {
  const { readingId } = useParams();
  const [reading, setReading] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchReading = async () => {
      try {
        const userId = localStorage.getItem('userId');
        const response = await fetch(
          `${process.env.REACT_APP_API_URL}/astrology/reading/${readingId}?userId=${userId}`
        );

        if (response.ok) {
          const data = await response.json();
          setReading(data);
        } else {
          setError('Failed to load reading');
        }
      } catch (err) {
        setError('Error connecting to server');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchReading();
  }, [readingId]);

  if (loading) {
    return (
      <div className="reading-result">
        <div className="container">
          <div className="loading-spinner">
            <div className="spinner"></div>
            <p>Loading your cosmic reading...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="reading-result">
        <div className="container">
          <div className="alert alert-error">{error}</div>
          <Link to="/" className="btn btn-primary">Return Home</Link>
        </div>
      </div>
    );
  }

  return (
    <div className="reading-result">
      <div className="container">
        <div className="result-header">
          <h1>Your Astrological Reading ✨</h1>
        </div>

        {reading && (
          <div className="card result-card">
            <div className="result-info">
              <h2>{reading.name}'s {reading.readingType} Reading</h2>
              <p className="result-meta">
                Zodiac Sign: <strong>{reading.zodiacSign}</strong> |
                Date: <strong>{new Date(reading.birthDate).toLocaleDateString()}</strong>
              </p>
            </div>

            <div className="result-content">
              <div className="reading-text">
                {reading.content || reading.reading || 'Your cosmic insights are being prepared...'}
              </div>
            </div>

            <div className="result-footer">
              <p className="result-date">
                Generated: {new Date(reading.createdAt || reading.timestamp).toLocaleString()}
              </p>
            </div>
          </div>
        )}

        <div className="action-buttons">
          <Link to="/new-reading" className="btn btn-primary">
            Get Another Reading
          </Link>
          <Link to="/history" className="btn btn-secondary">
            View All Readings
          </Link>
        </div>
      </div>
    </div>
  );
}

export default ReadingResult;

