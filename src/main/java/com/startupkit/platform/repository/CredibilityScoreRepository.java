package com.startupkit.platform.repository;

import com.startupkit.platform.entity.CredibilityScore;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.UUID;

public interface CredibilityScoreRepository extends JpaRepository<CredibilityScore, UUID> {
}
