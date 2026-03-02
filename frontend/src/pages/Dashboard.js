import React from 'react';
import { Link } from 'react-router-dom';
import './Dashboard.css';

function Dashboard({ userTokens }) {
  return (
    <div className="dashboard">
      <div className="container">
        <div className="welcome-section">
          <h1>Welcome to AI Astrology ✨</h1>
          <p>Discover cosmic insights powered by artificial intelligence</p>
        </div>

        <div className="dashboard-grid">
          <div className="card dashboard-card">
            <div className="card-icon">🔮</div>
            <h3>Your Balance</h3>
            <div className="balance-amount">{userTokens}</div>
            <p className="balance-label">Tokens Available</p>
            {userTokens === 0 && (
              <Link to="/buy-tokens" className="btn btn-primary">
                Get Tokens
              </Link>
            )}
          </div>

          <div className="card dashboard-card">
            <div className="card-icon">📖</div>
            <h3>New Reading</h3>
            <p>Generate a personalized astrological reading</p>
            <Link to="/new-reading" className="btn btn-primary">
              Start Reading
            </Link>
          </div>

          <div className="card dashboard-card">
            <div className="card-icon">📚</div>
            <h3>Your History</h3>
            <p>View all your previous readings</p>
            <Link to="/history" className="btn btn-primary">
              View History
            </Link>
          </div>

          <div className="card dashboard-card">
            <div className="card-icon">💰</div>
            <h3>Buy More Tokens</h3>
            <p>Need more tokens for readings?</p>
            <Link to="/buy-tokens" className="btn btn-primary">
              Purchase Now
            </Link>
          </div>
        </div>

        <div className="info-section card">
          <h2>How It Works</h2>
          <div className="steps">
            <div className="step">
              <div className="step-number">1</div>
              <h4>Provide Birth Info</h4>
              <p>Enter your birth date, time, and location</p>
            </div>
            <div className="step">
              <div className="step-number">2</div>
              <h4>Choose Reading Type</h4>
              <p>Select from various astrological readings</p>
            </div>
            <div className="step">
              <div className="step-number">3</div>
              <h4>Get Insights</h4>
              <p>Receive AI-powered cosmic insights</p>
            </div>
            <div className="step">
              <div className="step-number">4</div>
              <h4>Save for Later</h4>
              <p>Access your readings anytime in history</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;

