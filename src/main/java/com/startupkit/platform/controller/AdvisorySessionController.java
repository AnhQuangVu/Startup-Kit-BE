package com.startupkit.platform.controller;

import com.startupkit.platform.dto.response.ApiResponse;
import com.startupkit.platform.entity.AdvisorySession;
import com.startupkit.platform.entity.Mentor;
import com.startupkit.platform.entity.Startup;
import com.startupkit.platform.enums.SessionFormat;
import com.startupkit.platform.enums.SessionStatus;
import com.startupkit.platform.repository.AdvisorySessionRepository;
import com.startupkit.platform.repository.MentorRepository;
import com.startupkit.platform.repository.StartupRepository;
import lombok.AccessLevel;
import lombok.Data;
import lombok.RequiredArgsConstructor;
import lombok.experimental.FieldDefaults;
import org.springframework.web.bind.annotation.*;

import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/v1/sessions")
@RequiredArgsConstructor
@FieldDefaults(level = AccessLevel.PRIVATE, makeFinal = true)
public class AdvisorySessionController {

    AdvisorySessionRepository sessionRepository;
    MentorRepository mentorRepository;
    StartupRepository startupRepository;

    @GetMapping
    public ApiResponse<List<Map<String, Object>>> listSessions(
            @RequestParam(required = false) UUID mentorId,
            @RequestParam(required = false) UUID startupId) {
        List<AdvisorySession> sessions;
        if (mentorId != null) {
            sessions = sessionRepository.findByMentorId(mentorId);
        } else if (startupId != null) {
            sessions = sessionRepository.findByStartupId(startupId);
        } else {
            sessions = sessionRepository.findAll();
        }
        List<Map<String, Object>> result = sessions.stream()
                .map(this::toDto)
                .collect(Collectors.toList());
        return ApiResponse.<List<Map<String, Object>>>builder()
                .code(1000)
                .result(result)
                .build();
    }

    @PostMapping
    public ApiResponse<Map<String, Object>> bookSession(@RequestBody BookSessionRequest req) {
        Mentor mentor = mentorRepository.findById(req.getMentorId()).orElse(null);
        Startup startup = startupRepository.findById(req.getStartupId()).orElse(null);
        if (mentor == null || startup == null) {
            return ApiResponse.<Map<String, Object>>builder()
                    .code(1002)
                    .message("Mentor or Startup not found")
                    .build();
        }
        Instant start = req.getStartTime() != null ? req.getStartTime() : Instant.now().plus(2, ChronoUnit.DAYS);
        Instant end = req.getEndTime() != null ? req.getEndTime() : start.plus(1, ChronoUnit.HOURS);

        AdvisorySession session = AdvisorySession.builder()
                .mentor(mentor)
                .startup(startup)
                .topic(req.getTopic())
                .startTime(start)
                .endTime(end)
                .format(req.getFormat() != null ? req.getFormat() : SessionFormat.ONLINE)
                .status(SessionStatus.PENDING)
                .build();
        AdvisorySession saved = sessionRepository.save(session);
        return ApiResponse.<Map<String, Object>>builder()
                .code(1000)
                .message("Advisory session booked successfully")
                .result(toDto(saved))
                .build();
    }

    @PutMapping("/{id}/status")
    public ApiResponse<Map<String, Object>> updateStatus(
            @PathVariable UUID id,
            @RequestParam SessionStatus status) {
        AdvisorySession session = sessionRepository.findById(id).orElse(null);
        if (session == null) {
            return ApiResponse.<Map<String, Object>>builder()
                    .code(1002)
                    .message("Session not found")
                    .build();
        }
        session.setStatus(status);
        return ApiResponse.<Map<String, Object>>builder()
                .code(1000)
                .result(toDto(sessionRepository.save(session)))
                .build();
    }

    @PostMapping("/{id}/review")
    public ApiResponse<Map<String, Object>> reviewSession(
            @PathVariable UUID id,
            @RequestBody ReviewSessionRequest req) {
        AdvisorySession session = sessionRepository.findById(id).orElse(null);
        if (session == null) {
            return ApiResponse.<Map<String, Object>>builder()
                    .code(1002)
                    .message("Session not found")
                    .build();
        }
        session.setRating(req.getRating());
        session.setReview(req.getReview());
        session.setStatus(SessionStatus.COMPLETED);
        return ApiResponse.<Map<String, Object>>builder()
                .code(1000)
                .message("Session review submitted")
                .result(toDto(sessionRepository.save(session)))
                .build();
    }

    private Map<String, Object> toDto(AdvisorySession s) {
        Map<String, Object> m = new HashMap<>();
        m.put("id", s.getId());
        m.put("mentorId", s.getMentor() != null ? s.getMentor().getId() : null);
        m.put("startupId", s.getStartup() != null ? s.getStartup().getId() : null);
        m.put("topic", s.getTopic());
        m.put("startTime", s.getStartTime());
        m.put("endTime", s.getEndTime());
        m.put("format", s.getFormat());
        m.put("rating", s.getRating());
        m.put("review", s.getReview());
        m.put("status", s.getStatus());
        return m;
    }

    @Data
    public static class BookSessionRequest {
        private UUID mentorId;
        private UUID startupId;
        private String topic;
        private Instant startTime;
        private Instant endTime;
        private SessionFormat format;
    }

    @Data
    public static class ReviewSessionRequest {
        private Double rating;
        private String review;
    }
}
