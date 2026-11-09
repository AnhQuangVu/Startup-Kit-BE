package com.startupkit.platform.entity;

import com.startupkit.platform.enums.DealStatus;
import jakarta.persistence.*;
import lombok.*;
import lombok.experimental.FieldDefaults;
import org.hibernate.annotations.UpdateTimestamp;

import java.time.Instant;
import java.util.UUID;

@Entity
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
@FieldDefaults(level = AccessLevel.PRIVATE)
public class Deal {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    UUID id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "startup_id", nullable = false)
    Startup startup;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "investor_id", nullable = false)
    Investor investor;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "project_id", nullable = false)
    Project project;

    @Column(name = "contract_value", nullable = false)
    Double contractValue;

    @Column(name = "success_fee", nullable = false)
    Double successFee;

    @Enumerated(EnumType.STRING)
    @Column(name = "status", nullable = false)
    DealStatus status;

    @Column(name = "signed_at", nullable = false,
            columnDefinition = "timestamptz")
    Instant signedAt;

    @Column(name = "updated_at",
            columnDefinition = "timestamptz")
    @UpdateTimestamp
    Instant updatedAt;
}
