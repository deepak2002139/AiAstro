import React from 'react';
import './Footer.css';

function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="footer">
      <div className="footer-content">
        <div className="footer-section">
          <h3>AI Astro</h3>
          <p>Discover the cosmos within you with AI-powered astrological readings.</p>
          <div className="social-links">
            <a href="#" title="Facebook">
              <i className="fab fa-facebook-f"></i>
            </a>
            <a href="#" title="Twitter">
              <i className="fab fa-twitter"></i>
            </a>
            <a href="#" title="Instagram">
              <i className="fab fa-instagram"></i>
            </a>
            <a href="#" title="LinkedIn">
              <i className="fab fa-linkedin-in"></i>
            </a>
          </div>
        </div>

        <div className="footer-section">
          <h4>Quick Links</h4>
          <ul>
            <li><a href="/">Home</a></li>
            <li><a href="/new-reading">Get Reading</a></li>
            <li><a href="/history">My Readings</a></li>
            <li><a href="/buy-tokens">Buy Tokens</a></li>
          </ul>
        </div>

        <div className="footer-section">
          <h4>Support</h4>
          <ul>
            <li><a href="#">Contact Us</a></li>
            <li><a href="#">Help & FAQs</a></li>
            <li><a href="#">Blog</a></li>
            <li><a href="#">Feedback</a></li>
          </ul>
        </div>

        <div className="footer-section">
          <h4>Legal</h4>
          <ul>
            <li><a href="#">Privacy Policy</a></li>
            <li><a href="#">Terms of Service</a></li>
            <li><a href="#">Cookie Policy</a></li>
            <li><a href="#">Disclaimer</a></li>
          </ul>
        </div>

        <div className="footer-section">
          <h4>Newsletter</h4>
          <p>Subscribe to get cosmic updates and exclusive offers.</p>
          <div className="newsletter-form">
            <input
              type="email"
              placeholder="Enter your email"
              className="newsletter-input"
            />
            <button className="newsletter-btn">Subscribe</button>
          </div>
        </div>
      </div>

      <div className="footer-bottom">
        <div className="container">
          <div className="footer-bottom-content">
            <p>&copy; {currentYear} AI Astro. All rights reserved.</p>
            <p>Crafted with ✨ for cosmic explorers</p>
          </div>
        </div>
      </div>
    </footer>
  );
}

export default Footer;

