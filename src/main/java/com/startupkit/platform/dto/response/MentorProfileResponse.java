package com.startupkit.platform.dto.response;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;
import java.util.UUID;

@Data @Builder @NoArgsConstructor @AllArgsConstructor
public class MentorProfileResponse {

    // ──info ──────────────────────────────────────
    UUID userId;
    String fullName;
    String role;
    String location;
    String bio;
    List<String> expertiseTags;

    // ── Stats ────────────────────────────────────────
    Double averageScore;
    Integer totalCompletedSessions;
    Integer totalRatings;

    // ── Đánh giá phiên ──────────────────────────────
    List<SessionReviewDto> sessionReviews;

    @Data @Builder @NoArgsConstructor @AllArgsConstructor
    public static class SessionReviewDto {
        String startupName;
        String reviewContent;
        Double rating;
    }
}
