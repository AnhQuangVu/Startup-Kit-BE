package com.startupkit.platform.dto.request;


import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.*;
import lombok.experimental.FieldDefaults;

@Data
@NoArgsConstructor
@AllArgsConstructor
@FieldDefaults(level = AccessLevel.PRIVATE)
@Builder
public class LoginRequest {
    @NotBlank(message = "Email must not be empty")
    @Email(message = "Email Email is not format")
    String email;

    @NotBlank(message = "Password must not be empty")
    @Size(min = 8, message = "Password has been least {min} character")
    String password;
}
