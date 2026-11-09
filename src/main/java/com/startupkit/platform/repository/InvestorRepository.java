package com.startupkit.platform.repository;

import com.startupkit.platform.entity.Investor;
import com.startupkit.platform.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;
import java.util.UUID;

public interface InvestorRepository extends JpaRepository<Investor, UUID> {
    Optional<Investor> findByUserId(UUID userId);
}
