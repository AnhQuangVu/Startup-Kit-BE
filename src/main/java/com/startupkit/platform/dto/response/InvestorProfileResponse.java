package com.startupkit.platform.dto.response;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;
import java.util.UUID;

@Data @Builder @NoArgsConstructor @AllArgsConstructor
public class InvestorProfileResponse {

    // ── Header ───────────────────────────────────────
    UUID userId;
    String fullName;
    String role;
    String location;
    String organizationName;
    String bio;

    // ── Lĩnh vực đầu tư ─────────────────────────────
    List<String> investmentCriteria;

    // ── Giai đoạn ưa thích ──────────────────────────
    List<String> preferredStages;

    // ── Quy mô đầu tư ───────────────────────────────
    Double investmentMin;
    Double investmentMax;

    // ── Liên kết xã hội ─────────────────────────────
    String linkedinUrl;
    String websiteUrl;
    String twitterUrl;

    // ── Danh mục đầu tư ─────────────────────────────
    Integer totalInvested;
    List<PortfolioItemDto> portfolio;

    @Data @Builder @NoArgsConstructor @AllArgsConstructor
    public static class PortfolioItemDto {
        UUID startupId;
        String startupName;
        String industry;
    }
}
