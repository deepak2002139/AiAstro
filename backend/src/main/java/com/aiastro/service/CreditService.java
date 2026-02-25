package com.aiastro.service;

import com.aiastro.model.UserCredits;
import com.aiastro.model.CreditTransaction;
import com.aiastro.repository.UserCreditsRepository;
import com.aiastro.repository.CreditTransactionRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Optional;

@Service
public class CreditService {
    private final UserCreditsRepository userCreditsRepository;
    private final CreditTransactionRepository creditTransactionRepository;

    public CreditService(UserCreditsRepository userCreditsRepository, CreditTransactionRepository creditTransactionRepository) {
        this.userCreditsRepository = userCreditsRepository;
        this.creditTransactionRepository = creditTransactionRepository;
    }

    public int getBalance(Long userId) {
        Optional<UserCredits> uc = userCreditsRepository.findById(userId);
        return uc.map(UserCredits::getBalance).orElse(0);
    }

    @Transactional
    public int grantCredits(Long userId, int credits, String source, String providerPaymentId) {
        UserCredits uc = userCreditsRepository.findById(userId).orElseGet(() -> {
            UserCredits n = new UserCredits();
            n.setUserId(userId);
            n.setBalance(0);
            return n;
        });
        uc.setBalance(uc.getBalance() + credits);
        userCreditsRepository.save(uc);

        CreditTransaction tx = new CreditTransaction();
        tx.setUserId(userId);
        tx.setCredits(credits);
        tx.setChangeType("GRANT");
        tx.setSource(source);
        tx.setProviderPaymentId(providerPaymentId);
        creditTransactionRepository.save(tx);

        return uc.getBalance();
    }

    @Transactional
    public int consumeCredits(Long userId, int credits, String reason) throws IllegalArgumentException {
        UserCredits uc = userCreditsRepository.findById(userId).orElseGet(() -> {
            UserCredits n = new UserCredits();
            n.setUserId(userId);
            n.setBalance(0);
            return n;
        });
        if (uc.getBalance() < credits) {
            throw new IllegalArgumentException("Insufficient credits");
        }
        uc.setBalance(uc.getBalance() - credits);
        userCreditsRepository.save(uc);

        CreditTransaction tx = new CreditTransaction();
        tx.setUserId(userId);
        tx.setCredits(-credits);
        tx.setChangeType("CONSUME");
        tx.setSource(reason);
        creditTransactionRepository.save(tx);

        return uc.getBalance();
    }
}

