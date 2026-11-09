package com.startupkit.platform.repository;

import com.startupkit.platform.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;
import java.util.UUID;

public interface UserRepository extends JpaRepository<User, UUID> {
    Optional<User> findByContactEmail(String email);
    Optional<User> findById(UUID id);
    public boolean existsByContactEmail(String email);
}
