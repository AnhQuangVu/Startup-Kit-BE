package com.startupkit.platform.controller;

import com.startupkit.platform.dto.request.ForgotPasswordRequest;
import com.startupkit.platform.dto.request.LoginRequest;
import com.startupkit.platform.dto.request.RefreshTokenRequest;
import com.startupkit.platform.dto.request.ResetPasswordRequest;
import com.startupkit.platform.dto.response.ApiResponse;
import com.startupkit.platform.dto.response.LoginResponse;
import com.startupkit.platform.service.AuthenticationService;
import com.startupkit.platform.service.OAuth2AuthenticationService;
import jakarta.validation.Valid;
import lombok.AccessLevel;
import lombok.RequiredArgsConstructor;
import lombok.experimental.FieldDefaults;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.text.ParseException;

@RestController
@RequestMapping("/v1/auth")
@RequiredArgsConstructor
@FieldDefaults(level = AccessLevel.PRIVATE, makeFinal = true)
public class AuthController {
    AuthenticationService authenticationService;
    OAuth2AuthenticationService oAuth2AuthService;

    @PostMapping("/login")
    public ResponseEntity<ApiResponse<LoginResponse>> login(
            @RequestBody @Valid LoginRequest request) {

        LoginResponse data = authenticationService.login(request);

        return ResponseEntity.ok(
                ApiResponse.<LoginResponse>builder()
                        .code(1000)
                        .message("Login successful")
                        .result(data)
                        .build()
        );
    }

    @PostMapping("/forgot-password")
    public ApiResponse<String> forgotPassword(@RequestBody ForgotPasswordRequest request) {
        authenticationService.forgotPassword(request.getEmail());
        return ApiResponse.<String>builder()
                .result("Please check your email to reset password.")
                .build();
    }

    @PostMapping("/exchange")
    public ApiResponse<LoginResponse> exchangeCode(@RequestParam String code) {
        return ApiResponse.<LoginResponse>builder()
                .result(oAuth2AuthService.exchangeCode(code))
                .build();
    }

    @PostMapping("/reset-password")
    public ApiResponse<String> resetPassword(@RequestBody @Valid ResetPasswordRequest request) throws ParseException {
        authenticationService.resetPassword(request.getToken(), request.getPassword());
        return ApiResponse.<String>builder()
                .result("Password has been reset successfully.")
                .build();
    }

    @PostMapping({"/refresh-token", "/refresh"})
    public ApiResponse<LoginResponse> refreshToken(
            @RequestBody RefreshTokenRequest request) {
        return ApiResponse.<LoginResponse>builder()
                .result(authenticationService.refreshToken(request.getResolvedToken()))
                .build();
    }
}
