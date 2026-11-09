package com.startupkit.platform.dto.request;

import com.startupkit.platform.validator.PasswordMatch;

import jakarta.validation.constraints.Size;
import lombok.*;
import lombok.experimental.FieldDefaults;

import java.time.Instant;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
@FieldDefaults(level = AccessLevel.PRIVATE)
@PasswordMatch(message = "PASSWORD_NOT_MATCH")
public class ResetPasswordRequest {
    String token;
    @Size(min = 8 , message = "PASSWORD_INVALID")
    String password;
    String confirmPassword;
}