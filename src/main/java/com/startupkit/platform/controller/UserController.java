package com.startupkit.platform.controller;

import com.startupkit.platform.dto.request.UpdateUserRequest;
import com.startupkit.platform.dto.request.UserCreateRequest;
import com.startupkit.platform.dto.response.ApiResponse;
import com.startupkit.platform.dto.response.UpdateUserResponse;
import com.startupkit.platform.dto.response.UserCreateResponse;
import com.startupkit.platform.service.ProfileService;
import com.startupkit.platform.service.UserService;
import jakarta.validation.Valid;
import lombok.AccessLevel;
import lombok.RequiredArgsConstructor;
import lombok.experimental.FieldDefaults;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.web.bind.annotation.*;

import java.util.UUID;

@RestController
@RequestMapping("/v1/users")
@RequiredArgsConstructor
@FieldDefaults(level = AccessLevel.PRIVATE, makeFinal = true)
public class UserController {
    UserService userService;
    ProfileService profileService;

    @PostMapping
    public ApiResponse<UserCreateResponse> createUser(@RequestBody @Valid UserCreateRequest userCreateRequest) {
        return ApiResponse.<UserCreateResponse>builder()
                .result(userService.createUser(userCreateRequest))
                .build();
    }
    
     @GetMapping()
    public ApiResponse<Object> getProfile(
            @AuthenticationPrincipal Jwt jwt) {

        UUID userId = UUID.fromString(jwt.getSubject());

        return ApiResponse.builder()
                .result(profileService.getProfile(userId))
                .build();
    }

    @PutMapping()
    public ApiResponse<UpdateUserResponse> updateUser(
            @AuthenticationPrincipal Jwt jwt,
            @RequestBody UpdateUserRequest request) {

        UUID userId = UUID.fromString(jwt.getSubject());

        return ApiResponse.<UpdateUserResponse>builder()
                .result(userService.updateUser(userId, request))
                .build();
    }
}
