package com.startupkit.platform.repository;

import com.startupkit.platform.entity.UserIdentity;
import com.startupkit.platform.enums.IdentityProvider;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;
import java.util.UUID;

public interface UserIdentityRepository extends JpaRepository<UserIdentity, UUID> {
    Optional<UserIdentity> findByProviderAndProviderUserId(IdentityProvider provider, String providerUserId);
}
