import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './NewReading.css';

function NewReading({ userTokens, onTokensUsed }) {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    name: '',
    birthDate: '',
    birthTime: '',
    birthPlace: '',
    zodiacSign: '',
    readingType: 'general'
  });

  const readingTypes = [
    { value: 'general', label: 'General Overview' },
    { value: 'love', label: 'Love & Relationships' },
    { value: 'career', label: 'Career & Finance' },
    { value: 'health', label: 'Health & Wellness' },
    { value: 'personality', label: 'Personality Traits' }
  ];

  const zodiacSigns = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
  ];

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (userTokens < 1) {
      setError('You need at least 1 token to generate a reading. Please purchase tokens.');
      return;
    }

    if (!formData.name || !formData.birthDate || !formData.birthTime || !formData.birthPlace || !formData.zodiacSign) {
      setError('Please fill in all fields');
      return;
    }

    setLoading(true);
    try {
      const userId = localStorage.getItem('userId');
      const response = await fetch(`${process.env.REACT_APP_API_URL}/astrology/reading`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          userId,
          ...formData
        })
      });

      if (response.ok) {
        const result = await response.json();
        onTokensUsed(1);
        navigate(`/reading/${result.id}`, { state: { reading: result } });
      } else if (response.status === 402) {
        setError('Insufficient tokens. Please purchase more.');
      } else {
        setError('Failed to generate reading. Please try again.');
      }
    } catch (err) {
      setError('Error connecting to server. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="new-reading">
      <div className="container">
        <div className="reading-header">
          <h1>Generate New Reading 🔮</h1>
          <p>Provide your birth information for a personalized astrological reading</p>
          <div className="token-info">
            <span className="token-count">💰 {userTokens} Tokens Available</span>
            <span className="token-cost">Costs: 1 Token</span>
          </div>
        </div>

        {error && <div className="alert alert-error">{error}</div>}

        <div className="card reading-form-card">
          <form onSubmit={handleSubmit}>
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="name">Full Name *</label>
                <input
                  type="text"
                  id="name"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  placeholder="Enter your full name"
                  disabled={loading}
                />
              </div>
              <div className="form-group">
                <label htmlFor="zodiacSign">Zodiac Sign *</label>
                <select
                  id="zodiacSign"
                  name="zodiacSign"
                  value={formData.zodiacSign}
                  onChange={handleChange}
                  disabled={loading}
                >
                  <option value="">Select your zodiac sign</option>
                  {zodiacSigns.map(sign => (
                    <option key={sign} value={sign}>{sign}</option>
                  ))}
                </select>
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="birthDate">Birth Date *</label>
                <input
                  type="date"
                  id="birthDate"
                  name="birthDate"
                  value={formData.birthDate}
                  onChange={handleChange}
                  disabled={loading}
                />
              </div>
              <div className="form-group">
                <label htmlFor="birthTime">Birth Time *</label>
                <input
                  type="time"
                  id="birthTime"
                  name="birthTime"
                  value={formData.birthTime}
                  onChange={handleChange}
                  disabled={loading}
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="birthPlace">Birth Place *</label>
              <input
                type="text"
                id="birthPlace"
                name="birthPlace"
                value={formData.birthPlace}
                onChange={handleChange}
                placeholder="City, Country"
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label htmlFor="readingType">Reading Type *</label>
              <select
                id="readingType"
                name="readingType"
                value={formData.readingType}
                onChange={handleChange}
                disabled={loading}
              >
                {readingTypes.map(type => (
                  <option key={type.value} value={type.value}>{type.label}</option>
                ))}
              </select>
            </div>

            <div className="form-actions">
              <button
                type="submit"
                className="btn btn-primary"
                disabled={loading || userTokens < 1}
              >
                {loading ? (
                  <>
                    <span className="loading"></span> Generating...
                  </>
                ) : (
                  'Generate Reading'
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

export default NewReading;

