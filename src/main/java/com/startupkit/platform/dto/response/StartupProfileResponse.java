package com.startupkit.platform.dto.response;

import com.startupkit.platform.entity.Role;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;
import java.util.Set;
import java.util.UUID;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class StartupProfileResponse {
    // ── Thông tin tài khoản ─────────────────────────
    UUID userId;
    String userName;
    Role roles;
    String location;

    // ── Thông tin startup ────────────────────────────
    UUID startupId;
    String industry;
    String description;
    Integer teamSize;

    // ── Chỉ số uy tín (UI: ĐIỂM AI, CUỘC GẶP) ──────
    Double averageScore;        // 94 — thanh progress bar
    Integer totalRatings;           // tổng lượt đánh giá
    Integer totalCompletedSessions; // 47 CUỘC GẶP

    // ── Dự án (UI: DỰ ÁN section) ───────────────────
    Integer totalProjects;          // 1 DỰ ÁN (đếm)
    List<ProjectDto> project;             // chi tiết dự án

    // ── Inner DTO cho dự án ──────────────────────────
    @Data @Builder @NoArgsConstructor @AllArgsConstructor
    public static class ProjectDto {
        UUID projectId;
        String projectName;
        String projectDescription;
    }
}
