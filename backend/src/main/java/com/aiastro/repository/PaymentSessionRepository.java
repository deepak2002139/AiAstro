package com.aiastro.repository;

import com.aiastro.model.PaymentSession;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface PaymentSessionRepository extends JpaRepository<PaymentSession, Long> {
    Optional<PaymentSession> findByProviderSessionId(String providerSessionId);
}
