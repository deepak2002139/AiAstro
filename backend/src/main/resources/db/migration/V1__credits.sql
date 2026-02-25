-- Flyway migration: add credits and payment tables

CREATE TABLE IF NOT EXISTS user_credits (
  user_id BIGINT PRIMARY KEY,
  balance INT NOT NULL DEFAULT 0,
  version INT NOT NULL DEFAULT 0,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS credit_transactions (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  user_id BIGINT NOT NULL,
  credits INT NOT NULL,
  change_type VARCHAR(20) NOT NULL,
  source VARCHAR(100),
  provider_payment_id VARCHAR(255),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS payment_sessions (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  user_id BIGINT,
  provider VARCHAR(50),
  provider_session_id VARCHAR(255) UNIQUE,
  amount_minor INT,
  currency VARCHAR(3),
  status VARCHAR(20),
  metadata TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

