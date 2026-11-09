package com.startupkit.platform.entity;

import com.startupkit.platform.enums.SessionFormat;
import com.startupkit.platform.enums.SessionStatus;
import jakarta.persistence.*;
import lombok.*;
import lombok.experimental.FieldDefaults;

import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "advisory_session")
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
@FieldDefaults(level = AccessLevel.PRIVATE)
public class AdvisorySession {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    UUID id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "mentor_id", nullable = false)
    Mentor mentor;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "startup_id", nullable = false)
    Startup startup;

    @Column(name = "topic")
    String topic;

    @Column(name = "start_time", nullable = false,
            columnDefinition = "timestamptz")
    Instant startTime;

    @Column(name = "end_time", nullable = false,
            columnDefinition = "timestamptz")
    Instant endTime;

    @Enumerated(EnumType.STRING)
    @Column(name = "format")
    SessionFormat format;

    @Column(name = "rating")
    Double rating;

    @Column(name = "review", columnDefinition = "TEXT")
    String review;

    @Enumerated(EnumType.STRING)
    @Column(name = "status")
    SessionStatus status;
}
