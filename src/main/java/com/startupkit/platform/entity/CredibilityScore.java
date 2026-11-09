package com.startupkit.platform.entity;

import jakarta.persistence.*;
import lombok.*;
import lombok.experimental.FieldDefaults;
import org.hibernate.annotations.UpdateTimestamp;

import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "credibility_score")
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
@FieldDefaults(level = AccessLevel.PRIVATE)
public class CredibilityScore {
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    UUID id;

    @Column(name = "entity_type", nullable = false)
    String entityType;

    @Column(name = "average_score")
    Double averageScore;

    @Column(name = "total_ratings")
    Integer totalRatings;

    @Column(name = "total_completed_sessions")
    Integer totalCompletedSessions;

    @UpdateTimestamp
    @Column(name = "update_at", columnDefinition = "timestamptz")
    Instant updateAt;
}
