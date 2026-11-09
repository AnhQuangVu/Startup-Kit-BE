package com.startupkit.platform.repository;

import com.startupkit.platform.entity.AdvisorySession;
import com.startupkit.platform.enums.SessionStatus;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.UUID;

public interface AdvisorySessionRepository
        extends JpaRepository<AdvisorySession, UUID> {

    List<AdvisorySession> findByMentorId(UUID mentorId);

    List<AdvisorySession> findByStartupId(UUID startupId);

    // Lấy các phiên đã hoàn thành của mentor
    List<AdvisorySession> findByMentorIdAndStatus(
            UUID mentorId, SessionStatus status);

    // Đếm số phiên hoàn thành
    long countByMentorIdAndStatus(UUID mentorId, SessionStatus status);
}
