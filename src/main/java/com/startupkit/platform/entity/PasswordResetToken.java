package com.startupkit.platform.entity;

import jakarta.persistence.*;
import lombok.*;
import lombok.experimental.FieldDefaults;

import java.time.Instant;
import java.util.UUID;

@Entity
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
@FieldDefaults(level = AccessLevel.PRIVATE)
public class PasswordResetToken {
    @Id
    UUID id;

    String token;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_identity_id", nullable = false)
    UserIdentity userIdentity;

    Instant expiryTime;

    boolean used;
}