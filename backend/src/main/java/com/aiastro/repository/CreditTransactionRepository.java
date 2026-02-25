package com.aiastro.repository;

import com.aiastro.model.CreditTransaction;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface CreditTransactionRepository extends JpaRepository<CreditTransaction, Long> {
}

