package com.aiastro.model;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import jakarta.persistence.Column;
import jakarta.persistence.Version;
import java.time.Instant;

@Entity
@Table(name = "user_credits")
public class UserCredits {
    @Id
    private Long userId;

    @Column(nullable = false)
    private int balance = 0;

    @Version
    private int version = 0;

    @Column(name = "updated_at")
    private Instant updatedAt = Instant.now();

    // Getters and setters
    public Long getUserId() { return userId; }
    public void setUserId(Long userId) { this.userId = userId; }

    public int getBalance() { return balance; }
    public void setBalance(int balance) { this.balance = balance; }

    public int getVersion() { return version; }
    public void setVersion(int version) { this.version = version; }

    public Instant getUpdatedAt() { return updatedAt; }
    public void setUpdatedAt(Instant updatedAt) { this.updatedAt = updatedAt; }
}

