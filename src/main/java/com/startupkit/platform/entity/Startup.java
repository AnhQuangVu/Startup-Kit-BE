package com.startupkit.platform.entity;

import jakarta.persistence.*;
import lombok.*;
import lombok.experimental.FieldDefaults;

import java.util.List;
import java.util.UUID;

@Entity
@Setter
@Getter
@Builder
@NoArgsConstructor
@AllArgsConstructor
@FieldDefaults(level = AccessLevel.PRIVATE)
public class Startup {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    UUID id;

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    User user;                    // ← đổi thành chữ thường

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "credibility_score_id")
    CredibilityScore credibilityScore;

    @OneToMany(fetch = FetchType.LAZY)
    @JoinColumn(name = "startup_id")
    List<Project> projects;

    @Column(name = "industry")
    String industry;

    @Column(name = "description", columnDefinition = "TEXT")
    String description;

    @Column(name = "team_size")      // ← snake_case theo convention DB
    Integer teamSize;
}
