package com.startupkit.platform.dto.request;

import com.startupkit.platform.enums.UserType;
import com.startupkit.platform.validator.PasswordMatch;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.*;
import lombok.experimental.FieldDefaults;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
@FieldDefaults(level = AccessLevel.PRIVATE)
@PasswordMatch(message = "PASSWORD_NOT_MATCH")
public class UserCreateRequest {
    String fullName;
    @Email(message = "EMAIL_INVALID")
    String email;

    @Size(min = 8 , message = "PASSWORD_INVALID")
    String password;
    String confirmPassword;

    @NotNull(message = "User type must not be empty")
    UserType userType;
}
