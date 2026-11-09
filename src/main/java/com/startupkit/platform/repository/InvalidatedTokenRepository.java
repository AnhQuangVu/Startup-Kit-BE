package com.startupkit.platform.repository;

import com.startupkit.platform.entity.InvalidatedToken;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.UUID;

public interface InvalidatedTokenRepository extends JpaRepository<InvalidatedToken, UUID> {
}
