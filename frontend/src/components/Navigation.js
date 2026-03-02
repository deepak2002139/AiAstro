import React from 'react';
import { Link } from 'react-router-dom';
import './Navigation.css';

function Navigation({ userTokens }) {
  return (
    <nav className="navbar">
      <div className="container nav-container">
        <Link to="/" className="nav-logo">
          ✨ AI Astrology
        </Link>
        <ul className="nav-menu">
          <li>
            <Link to="/" className="nav-link">
              Dashboard
            </Link>
          </li>
          <li>
            <Link to="/new-reading" className="nav-link">
              New Reading
            </Link>
          </li>
          <li>
            <Link to="/history" className="nav-link">
              History
            </Link>
          </li>
          <li>
            <Link to="/buy-tokens" className="nav-link btn-token">
              💰 {userTokens} Tokens
            </Link>
          </li>
        </ul>
      </div>
    </nav>
  );
}

export default Navigation;

