package com.startupkit.platform.entity;

import com.startupkit.platform.enums. IdentityProvider;
import jakarta.persistence.*;
import lombok.*;
import lombok.experimental.FieldDefaults;
import org.hibernate.annotations.CreationTimestamp;

import java.time.Instant;
import java.util.UUID;

@Entity
@Getter
@Setter
@Builder
@AllArgsConstructor
@Table(
        uniqueConstraints = {
                @UniqueConstraint(columnNames = {"provider", "provider_user_id"})
        }, // MỘT provider + MỘT định danh đăng nhập CHỈ ĐƯỢC TỒN TẠI DUY NHẤT 1 LẦN
        indexes = {
                @Index(name = "idx_user_identities_user_id", columnList = "user_id")
        }
)
@NoArgsConstructor
@FieldDefaults(level = AccessLevel.PRIVATE)
public class UserIdentity {
    @Id
    @GeneratedValue
    UUID id;

    @OneToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "user_id", nullable = false, unique = true)
    User user;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    IdentityProvider provider;

    /**
     * Định danh đăng nhập:
     * - username
     * - email
     * - phone
     * - oauth sub
     */
    @Column(nullable = false)
    String providerUserId;

    String email;

    /**
     * Chỉ dùng khi provider = LOCAL (hash của mật khẩu)
     */
    String password;

    @Builder.Default
    Boolean verified = false;

    @Column(columnDefinition = "timestamptz")
    Instant lastPasswordChange;

    @CreationTimestamp
    @Column(name = "created_at", columnDefinition = "timestamptz")
    Instant createdAt;
}