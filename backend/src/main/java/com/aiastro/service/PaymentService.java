package com.aiastro.service;

import com.aiastro.model.PaymentSession;
import com.aiastro.repository.PaymentSessionRepository;
import org.springframework.stereotype.Service;

import java.util.UUID;

@Service
public class PaymentService {
    private final PaymentSessionRepository paymentSessionRepository;

    public PaymentService(PaymentSessionRepository paymentSessionRepository) {
        this.paymentSessionRepository = paymentSessionRepository;
    }

    /**
     * Create a mock checkout session and persist a PaymentSession entity.
     * In a real implementation this would call Stripe API to create a Checkout Session.
     */
    public PaymentSession createMockCheckout(Long userId, int amountMinor, String currency, int credits) {
        PaymentSession ps = new PaymentSession();
        ps.setUserId(userId);
        ps.setProvider("MOCK");
        String providerSessionId = "mock_" + UUID.randomUUID().toString();
        ps.setProviderSessionId(providerSessionId);
        ps.setAmountMinor(amountMinor);
        ps.setCurrency(currency);
        ps.setStatus("PENDING");
        ps.setMetadata("{\"credits\":" + credits + "}");
        paymentSessionRepository.save(ps);
        return ps;
    }

    public PaymentSession markCompletedByProviderSessionId(String providerSessionId) {
        PaymentSession ps = paymentSessionRepository.findByProviderSessionId(providerSessionId).orElse(null);
        if (ps == null) return null;
        ps.setStatus("COMPLETED");
        paymentSessionRepository.save(ps);
        return ps;
    }
}

