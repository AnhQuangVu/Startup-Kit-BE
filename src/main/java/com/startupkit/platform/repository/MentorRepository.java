package com.startupkit.platform.repository;

import com.startupkit.platform.entity.Mentor;
import com.startupkit.platform.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;
import java.util.UUID;

public interface MentorRepository extends JpaRepository<Mentor, UUID> {
    Optional<Mentor> findByUserId(UUID userId);
}
