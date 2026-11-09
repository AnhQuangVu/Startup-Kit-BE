package com.startupkit.platform.dto.response;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.UUID;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class UpdateUserResponse {
    UUID userId;
    String fullName;
    String location;
    String avatarUrl;
    String contactPhone;
    String userType;
    String role;
}
