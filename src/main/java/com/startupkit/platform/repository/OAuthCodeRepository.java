package com.startupkit.platform.repository;

import com.startupkit.platform.entity.OAuthCode;
import org.springframework.data.jpa.repository.JpaRepository;

import java.time.Instant;

public interface OAuthCodeRepository extends JpaRepository<OAuthCode, String> {

    // Xóa các code đã hết hạn — dùng cho cleanup job
    void deleteByExpiryTimeBefore(Instant now);
}
