package com.startupkit.platform.entity;

import com.startupkit.platform.enums.AccountStatus;
import com.startupkit.platform.enums.UserType;
import jakarta.persistence.*;
import lombok.*;
import lombok.experimental.FieldDefaults;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

import java.time.Instant;
import java.util.Set;
import java.util.UUID;

@Entity
@Getter
@Setter
@Builder
@AllArgsConstructor
@NoArgsConstructor
@FieldDefaults(level = AccessLevel.PRIVATE)
@EqualsAndHashCode(onlyExplicitlyIncluded = true)
@Table(name = "users",
        indexes = {
                @Index(name = "idx_users_email", columnList = "contact_email"),
                @Index(name = "idx_users_phone", columnList = "contact_phone")
        }
)
public class User{
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    UUID id;

    String contactEmail;
    String contactPhone;
    String fullName;
    String avatarUrl;

    @Column(columnDefinition = "timestamptz")
    @Builder.Default
    Instant lastTimeChange = null;

    @Builder.Default
    boolean verified = false;

    @Enumerated(EnumType.STRING)
    AccountStatus accountStatus = AccountStatus.ACTIVE;

    @Enumerated(EnumType.STRING)
    UserType userType;

    @CreationTimestamp
    @Column(name = "created_at", columnDefinition = "timestamptz")
    Instant createdAt;

    @UpdateTimestamp
    @Column(name = "updated_at", columnDefinition = "timestamptz")
    Instant updatedAt;

    @OneToOne(mappedBy = "user" , cascade = CascadeType.ALL)
    UserIdentity userIdentity;

    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "roles_code")
    Role roles;

    @Column(name = "location")
    String location;


}
