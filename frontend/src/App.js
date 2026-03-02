import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';
import Navigation from './components/Navigation';
import Dashboard from './pages/Dashboard';
import NewReading from './pages/NewReading';
import ReadingHistory from './pages/ReadingHistory';
import BuyTokens from './pages/BuyTokens';
import ReadingResult from './pages/ReadingResult';

function App() {
  const [userTokens, setUserTokens] = useState(0);
  const [userId, setUserId] = useState(null);

  useEffect(() => {
    // Initialize user session
    const storedUserId = localStorage.getItem('userId');
    if (!storedUserId) {
      const newUserId = `user_${Date.now()}`;
      localStorage.setItem('userId', newUserId);
      setUserId(newUserId);
    } else {
      setUserId(storedUserId);
    }

    // Fetch user credits/tokens
    fetchUserTokens();
  }, []);

  const fetchUserTokens = async () => {
    try {
      const storedUserId = localStorage.getItem('userId');
      const response = await fetch(
        `${process.env.REACT_APP_API_URL}/credits/balance?userId=${storedUserId}`
      );
      if (response.ok) {
        const data = await response.json();
        setUserTokens(data.credits || 0);
      }
    } catch (error) {
      console.error('Failed to fetch tokens:', error);
      setUserTokens(0);
    }
  };

  const handleTokensPurchased = (tokens) => {
    setUserTokens(prevTokens => prevTokens + tokens);
    fetchUserTokens(); // Refresh from backend
  };

  const handleTokensUsed = (tokensSpent) => {
    setUserTokens(prevTokens => Math.max(0, prevTokens - tokensSpent));
  };

  return (
    <Router>
      <div className="App">
        <Navigation userTokens={userTokens} />
        <Routes>
          <Route path="/" element={<Dashboard userTokens={userTokens} />} />
          <Route
            path="/new-reading"
            element={
              <NewReading
                userTokens={userTokens}
                onTokensUsed={handleTokensUsed}
              />
            }
          />
          <Route
            path="/reading/:readingId"
            element={<ReadingResult onTokensUsed={handleTokensUsed} />}
          />
          <Route
            path="/history"
            element={<ReadingHistory />}
          />
          <Route
            path="/buy-tokens"
            element={
              <BuyTokens
                onTokensPurchased={handleTokensPurchased}
              />
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;

