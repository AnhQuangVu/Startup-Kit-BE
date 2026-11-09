package com.startupkit.platform.entity;

import jakarta.persistence.*;
import lombok.*;
import lombok.experimental.FieldDefaults;

import java.util.UUID;

@Entity
@Getter @Setter @Builder
@NoArgsConstructor @AllArgsConstructor
@FieldDefaults(level = AccessLevel.PRIVATE)
public class Investor {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    UUID id;

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    User user;                          // ← chữ thường

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "credibility_score_id")
    CredibilityScore credibilityScore;

    @Column(name = "investment_criteria")
    String investmentCriteria;          // "Fintech, Blockchain"

    @Column(name = "preferred_stages")
    String preferredStages;             // "Seed, Series A"

    @Column(name = "organization_name")
    String organizationName;            // "Investment Fund Manager"

    @Column(name = "bio", columnDefinition = "TEXT")
    String bio;

    @Column(name = "investment_min")
    Double investmentMin;

    @Column(name = "investment_max")
    Double investmentMax;

    // Liên kết xã hội
    @Column(name = "linkedin_url")
    String linkedinUrl;

    @Column(name = "website_url")
    String websiteUrl;

    @Column(name = "twitter_url")
    String twitterUrl;
}
