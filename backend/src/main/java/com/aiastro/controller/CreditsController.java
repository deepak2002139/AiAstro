package com.aiastro.controller;

import com.aiastro.service.CreditService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/credits")
public class CreditsController {
    private final CreditService creditService;

    public CreditsController(CreditService creditService) {
        this.creditService = creditService;
    }

    @GetMapping("/balance")
    public ResponseEntity<Map<String, Object>> getBalance(@RequestParam("userId") Long userId) {
        int balance = creditService.getBalance(userId);
        return ResponseEntity.ok(Map.of("userId", userId, "balance", balance));
    }

    @PostMapping("/consume")
    public ResponseEntity<Map<String, Object>> consume(@RequestBody Map<String, Object> body) {
        Long userId = Long.valueOf(String.valueOf(body.get("userId")));
        Integer credits = Integer.valueOf(String.valueOf(body.getOrDefault("credits", 1)));
        String reason = String.valueOf(body.getOrDefault("reason", "prompt"));
        try {
            int balance = creditService.consumeCredits(userId, credits, reason);
            return ResponseEntity.ok(Map.of("success", true, "balance", balance));
        } catch (IllegalArgumentException e) {
            return ResponseEntity.status(402).body(Map.of("success", false, "message", e.getMessage()));
        }
    }
}

