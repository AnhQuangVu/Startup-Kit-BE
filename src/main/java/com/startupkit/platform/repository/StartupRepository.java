package com.startupkit.platform.repository;

import com.startupkit.platform.entity.Startup;
import com.startupkit.platform.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;
import java.util.UUID;

public interface StartupRepository extends JpaRepository<Startup, UUID> {
    Optional<Startup> findByUserId(UUID userId);
}
