package com.aiastro.repository;

import com.aiastro.model.UserCredits;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface UserCreditsRepository extends JpaRepository<UserCredits, Long> {
}

