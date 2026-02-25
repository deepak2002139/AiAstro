package com.aiastro.controller;

import com.aiastro.model.PaymentSession;
import com.aiastro.service.PaymentService;
import com.aiastro.service.CreditService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/payments")
public class PaymentsController {
    private final PaymentService paymentService;
    private final CreditService creditService;

    public PaymentsController(PaymentService paymentService, CreditService creditService) {
        this.paymentService = paymentService;
        this.creditService = creditService;
    }

    @PostMapping("/create-session")
    public ResponseEntity<Map<String, Object>> createSession(@RequestBody Map<String, Object> body) {
        Long userId = Long.valueOf(String.valueOf(body.get("userId")));
        String currency = String.valueOf(body.getOrDefault("currency", "USD"));
        // pack default 10 credits
        int credits = Integer.valueOf(String.valueOf(body.getOrDefault("credits", 10)));

        int amountMinor = 100; // default $1.00
        if ("INR".equalsIgnoreCase(currency)) amountMinor = 2000; // ₹20 => 2000 paise
        else if ("EUR".equalsIgnoreCase(currency)) amountMinor = 100; // €1 => 100 cents

        PaymentSession ps = paymentService.createMockCheckout(userId, amountMinor, currency, credits);

        // For mock, build a fake checkout URL that calls simulated webhook endpoint when "completed"
        String checkoutUrl = "/api/payments/mock-checkout?sessionId=" + ps.getProviderSessionId();
        return ResponseEntity.ok(Map.of("checkoutUrl", checkoutUrl, "sessionId", ps.getProviderSessionId()));
    }

    /**
     * Simulate a user completing checkout (for local testing). In real world, Stripe will call webhook.
     */
    @PostMapping("/mock-complete")
    public ResponseEntity<Map<String, Object>> mockComplete(@RequestBody Map<String, Object> body) {
        String sessionId = String.valueOf(body.get("sessionId"));
        PaymentSession ps = paymentService.markCompletedByProviderSessionId(sessionId);
        if (ps == null) return ResponseEntity.badRequest().body(Map.of("success", false, "message", "invalid session"));

        // grant credits based on metadata (simple parse)
        int credits = 10;
        try {
            String meta = ps.getMetadata();
            if (meta != null && meta.contains("credits")) credits = Integer.parseInt(meta.replaceAll(".*\\\"credits\\\":(\\d+).*", "$1"));
        } catch (Exception ignored) {}

        int balance = creditService.grantCredits(ps.getUserId(), credits, "MOCK", sessionId);
        return ResponseEntity.ok(Map.of("success", true, "balance", balance));
    }
}

