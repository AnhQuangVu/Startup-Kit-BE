package com.startupkit.platform.entity;

import jakarta.persistence.*;
import lombok.*;
import lombok.experimental.FieldDefaults;

import java.util.UUID;

@Entity
@Table(name = "project")
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
@FieldDefaults(level = AccessLevel.PRIVATE)
public class Project {
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    UUID id;

    @Column(name = "startup_id")
    UUID startupId;

    @Column(name = "project_name", nullable = false)
    String projectName;

    @Column(name = "project_description", columnDefinition = "TEXT")
    String projectDescription;
}
