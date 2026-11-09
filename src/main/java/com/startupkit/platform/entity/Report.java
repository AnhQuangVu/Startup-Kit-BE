package com.startupkit.platform.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.*;
import lombok.experimental.FieldDefaults;

@Entity
@Table(name = "platform_report")
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
@FieldDefaults(level = AccessLevel.PRIVATE)
public class Report {

    @Id
    @Column(name = "id", length = 50)
    String id;

    @Column(name = "report_type", nullable = false)
    String type;

    @Column(name = "target", nullable = false)
    String target;

    @Column(name = "reporter", nullable = false)
    String reporter;

    @Column(name = "reason", columnDefinition = "TEXT", nullable = false)
    String reason;

    @Column(name = "severity", nullable = false)
    String severity;

    @Column(name = "created_at", nullable = false)
    String createdAt;

    @Column(name = "status", nullable = false)
    String status;

    @Column(name = "resolution_note", columnDefinition = "TEXT")
    String resolutionNote;
}
