package com.startupkit.platform.entity;


import jakarta.persistence.*;
import lombok.*;
import lombok.experimental.FieldDefaults;

import java.util.UUID;

@Entity
@Getter @Setter @Builder
@NoArgsConstructor @AllArgsConstructor
@FieldDefaults(level = AccessLevel.PRIVATE)
public class Mentor {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    UUID id;

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    User user;                          // ← chữ thường

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "credibility_score_id")   // ← thêm _id
    CredibilityScore credibilityScore;

    @Column(name = "expertise", nullable = false)
    String expertise;

    @Column(name = "bio", columnDefinition = "TEXT")
    String bio;

    @Column(name = "hourly_rate")
    Double hourlyRate;

    @Column(name = "rating")
    Double rating;

    @Column(name = "review", columnDefinition = "TEXT")
    String review;
}
