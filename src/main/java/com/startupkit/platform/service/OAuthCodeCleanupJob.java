package com.startupkit.platform.service;

import com.startupkit.platform.repository.OAuthCodeRepository;
import jakarta.transaction.Transactional;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import java.time.Instant;

@Component
@RequiredArgsConstructor
@Slf4j
public class OAuthCodeCleanupJob {

    private final OAuthCodeRepository oauthCodeRepo;

    @Scheduled(fixedRate = 60_000) // chạy mỗi 1 phút
    @Transactional
    public void cleanExpiredCodes() {
        oauthCodeRepo.deleteByExpiryTimeBefore(Instant.now());
        log.debug("Cleaned expired OAuth codes");
    }
}
