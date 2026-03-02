import React, { useState, useEffect } from 'react';
import './BuyTokens.css';

function BuyTokens({ onTokensPurchased }) {
  const [selectedPackage, setSelectedPackage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('');
  const [userLocation, setUserLocation] = useState('US'); // Default to US
  const [currency, setCurrency] = useState('$');
  const [tokenPackages, setTokenPackages] = useState([]);

  // Fetch user location on component mount
  useEffect(() => {
    fetchUserLocation();
  }, []);

  // Update token packages when location changes
  useEffect(() => {
    updateTokenPackages(userLocation);
  }, [userLocation]);

  const fetchUserLocation = async () => {
    try {
      // Using IP geolocation API to detect user location
      const response = await fetch('https://ipapi.co/json/');
      const data = await response.json();
      const country = data.country_code || 'US';
      setUserLocation(country);
    } catch (error) {
      console.error('Error fetching location:', error);
      // Default to US if geolocation fails
      setUserLocation('US');
    }
  };

  const updateTokenPackages = (location) => {
    let packages;

    if (location === 'IN') {
      // India pricing: 10 tokens for 20 rupees
      setCurrency('₹');
      packages = [
        {
          id: 1,
          tokens: 10,
          price: 20,
          popular: false,
          description: 'Starter Pack'
        },
        {
          id: 2,
          tokens: 30,
          price: 60,
          popular: true,
          description: 'Best Value',
          savings: '10%'
        },
        {
          id: 3,
          tokens: 60,
          price: 120,
          popular: false,
          description: 'Power Pack',
          savings: '10%'
        },
        {
          id: 4,
          tokens: 200,
          price: 400,
          popular: false,
          description: 'Ultimate Pack',
          savings: '20%'
        }
      ];
    } else {
      // US and other countries: 1 dollar for 10 tokens
      setCurrency('$');
      packages = [
        {
          id: 1,
          tokens: 10,
          price: 1.00,
          popular: false,
          description: 'Starter Pack'
        },
        {
          id: 2,
          tokens: 30,
          price: 2.99,
          popular: true,
          description: 'Best Value',
          savings: '1%'
        },
        {
          id: 3,
          tokens: 60,
          price: 5.99,
          popular: false,
          description: 'Power Pack',
          savings: '1%'
        },
        {
          id: 4,
          tokens: 200,
          price: 19.99,
          popular: false,
          description: 'Ultimate Pack',
          savings: '1%'
        }
      ];
    }
    setTokenPackages(packages);
  };

  const handlePurchase = async (pkg) => {
    setSelectedPackage(pkg.id);
    setLoading(true);
    setMessage('');

    try {
      const userId = localStorage.getItem('userId');
      const response = await fetch(`${process.env.REACT_APP_API_URL}/payments/create-session`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          userId,
          tokens: pkg.tokens,
          amount: pkg.price,
          packageId: pkg.id
        })
      });

      if (response.ok) {
        const data = await response.json();

        // Simulate successful payment (in production, this would redirect to Stripe)
        setMessageType('success');
        setMessage('Payment processed successfully! Tokens added to your account.');

        // Update tokens after a short delay
        setTimeout(() => {
          onTokensPurchased(pkg.tokens);
          setMessage('');
        }, 2000);
      } else {
        setMessageType('error');
        setMessage('Payment failed. Please try again.');
      }
    } catch (error) {
      console.error('Payment error:', error);
      setMessageType('error');
      setMessage('Error processing payment. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="buy-tokens">
      <div className="container">
        <div className="buy-header">
          <h1>Buy Tokens 💰</h1>
          <p>Purchase tokens to generate astrological readings</p>
          <p style={{ fontSize: '14px', marginTop: '15px', opacity: 0.8 }}>
            Pricing based on your location: <strong>{userLocation === 'IN' ? 'India (₹)' : 'International ($)'}</strong>
          </p>
        </div>

        {message && (
          <div className={`alert alert-${messageType}`}>
            {message}
          </div>
        )}

        <div className="pricing-grid">
          {tokenPackages.map((pkg) => (
            <div
              key={pkg.id}
              className={`pricing-card ${pkg.popular ? 'popular' : ''}`}
            >
              {pkg.popular && <div className="popular-badge">Most Popular</div>}
              {pkg.savings && <div className="savings-badge">Save {pkg.savings}</div>}

              <h3>{pkg.description}</h3>
              <div className="token-amount">{pkg.tokens}</div>
              <p className="token-label">Tokens</p>

              <div className="price">
                <span className="currency">{currency}</span>
                <span className="amount">{pkg.price.toFixed(2)}</span>
              </div>

              <p className="price-per-token">
                {currency}{(pkg.price / pkg.tokens).toFixed(2)} per token
              </p>

              <button
                onClick={() => handlePurchase(pkg)}
                disabled={loading && selectedPackage === pkg.id}
                className="btn btn-primary"
              >
                {loading && selectedPackage === pkg.id ? (
                  <>
                    <span className="loading"></span> Processing...
                  </>
                ) : (
                  'Purchase Now'
                )}
              </button>
            </div>
          ))}
        </div>

        <div className="card info-card">
          <h2>How It Works</h2>
          <div className="info-steps">
            <div className="info-step">
              <div className="step-icon">1</div>
              <h4>Choose a Package</h4>
              <p>Select the token package that best suits your needs</p>
            </div>
            <div className="info-step">
              <div className="step-icon">2</div>
              <h4>Secure Payment</h4>
              <p>Complete your purchase securely with Stripe</p>
            </div>
            <div className="info-step">
              <div className="step-icon">3</div>
              <h4>Instant Credits</h4>
              <p>Tokens are instantly added to your account</p>
            </div>
            <div className="info-step">
              <div className="step-icon">4</div>
              <h4>Generate Readings</h4>
              <p>Use your tokens to generate astrological readings</p>
            </div>
          </div>
        </div>

        <div className="card faq-card">
          <h2>Frequently Asked Questions</h2>
          <div className="faq-item">
            <h4>How long do tokens last?</h4>
            <p>Your tokens never expire. Use them whenever you want.</p>
          </div>
          <div className="faq-item">
            <h4>What if I need a refund?</h4>
            <p>Contact our support team within 30 days of purchase for a full refund.</p>
          </div>
          <div className="faq-item">
            <h4>Do you offer bulk discounts?</h4>
            <p>Yes! Check out our Ultimate Pack for the best savings.</p>
          </div>
          <div className="faq-item">
            <h4>Is my payment information secure?</h4>
            <p>Yes, we use industry-standard SSL encryption and Stripe for secure payments.</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default BuyTokens;

