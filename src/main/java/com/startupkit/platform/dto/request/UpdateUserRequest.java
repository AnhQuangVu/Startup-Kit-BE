package com.startupkit.platform.dto.request;

import com.startupkit.platform.enums.UserType;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class UpdateUserRequest {

    String fullName;
    String location;
    String avatarUrl;
    String contactPhone;

    UserType userType;
}
