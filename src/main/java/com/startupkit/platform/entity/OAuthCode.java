package com.startupkit.platform.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.*;
import lombok.experimental.FieldDefaults;


import java.time.Instant;

@Entity
@Table(name = "oauth_code")
@Getter @Setter @Builder
@NoArgsConstructor @AllArgsConstructor
@FieldDefaults(level = AccessLevel.PRIVATE)
public class OAuthCode {

    @Id
    @Column(nullable = false)
    String code;

    @Column(nullable = false, columnDefinition = "TEXT")
    String accessToken;

    @Column(columnDefinition = "TEXT")
    private String refreshToken;

    @Column(nullable = false, columnDefinition = "timestamptz")
    Instant expiryTime;

    @Builder.Default
    @Column(nullable = false)
    Boolean used = false;
}
