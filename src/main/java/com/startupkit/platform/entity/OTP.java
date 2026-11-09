package com.startupkit.platform.entity;

import com.startupkit.platform.enums.OtpType;
import jakarta.persistence.*;
import lombok.*;
import lombok.experimental.FieldDefaults;

import java.time.Instant;
import java.util.UUID;

@Entity
@Getter
@Setter
@Builder
@AllArgsConstructor
@NoArgsConstructor
@FieldDefaults(level = AccessLevel.PRIVATE)
public class OTP {
    @Id
    @GeneratedValue
    UUID id;

    @Column(nullable = false, length = 6)
    String code;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "user_id", nullable = false)
    User user;

    // Target — nơi gửi/áp dụng mã, có thể là email, phone, hoặc provider_user_id tùy context
    @Column(name = "target", length = 255)
    String target;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 32)
    OtpType type;

    @Column(nullable = false)
    Instant expiryTime;

    @Column(name = "is_used", nullable = false)
    @Builder.Default
    Boolean isUsed = false;

    @Column(nullable = false, updatable = false)
    @Builder.Default
    Instant createdAt = Instant.now();
}
