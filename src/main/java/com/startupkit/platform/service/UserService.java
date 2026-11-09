package com.startupkit.platform.service;

import com.startupkit.platform.dto.request.UpdateUserRequest;
import com.startupkit.platform.dto.request.UserCreateRequest;
import com.startupkit.platform.dto.response.UpdateUserResponse;
import com.startupkit.platform.dto.response.UserCreateResponse;
import com.startupkit.platform.entity.Role;
import com.startupkit.platform.entity.User;
import com.startupkit.platform.entity.UserIdentity;
import com.startupkit.platform.enums.IdentityProvider;
import com.startupkit.platform.exception.AppException;
import com.startupkit.platform.exception.ErrorCode;
import com.startupkit.platform.mapper.UserMapper;
import com.startupkit.platform.repository.RoleRepository;
import com.startupkit.platform.repository.UserRepository;
import jakarta.transaction.Transactional;
import lombok.AccessLevel;
import lombok.RequiredArgsConstructor;
import lombok.experimental.FieldDefaults;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.util.UUID;

@Service
@RequiredArgsConstructor
@FieldDefaults(level = AccessLevel.PRIVATE, makeFinal = true)
@Slf4j
public class UserService {

    UserRepository userRepository;
    RoleRepository roleRepository;
    UserMapper userMapper;
    PasswordEncoder passwordEncoder;

    public UserCreateResponse createUser(UserCreateRequest request) {
        if (userRepository.existsByContactEmail(request.getEmail())) {
            throw new AppException(ErrorCode.USER_ALREADY_EXISTED);
        }

        User user = userMapper.toUser(request);
        user.setContactEmail(request.getEmail());

        UserIdentity userIdentity = UserIdentity.builder()
                .user(user)
                .provider(IdentityProvider.LOCAL)
                .providerUserId(request.getEmail())
                .email(request.getEmail())
                .password(passwordEncoder.encode(request.getPassword()))
                .verified(false)
                .build();

        user.setUserIdentity(userIdentity);
        userRepository.save(user);

        return userMapper.toUserCreateResponse(userIdentity);
    }

    @Transactional
    public UpdateUserResponse updateUser(UUID userId, UpdateUserRequest request) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new AppException(ErrorCode.USER_NOT_EXISTED));

        // Cập nhật các field nếu có giá trị
        if (request.getFullName() != null) {
            user.setFullName(request.getFullName());
        }
        if (request.getLocation() != null) {
            user.setLocation(request.getLocation());
        }
        if (request.getAvatarUrl() != null) {
            user.setAvatarUrl(request.getAvatarUrl());
        }
        if (request.getContactPhone() != null) {
            user.setContactPhone(request.getContactPhone());
        }


        if (request.getUserType() != null && user.getUserType() == null) {
            user.setUserType(request.getUserType());

            Role role = roleRepository.findById(request.getUserType().name())
                    .orElseThrow(() -> new AppException(ErrorCode.USER_NOT_EXISTED));
            user.setRoles(role);
        }

        userRepository.save(user);
        log.info("Updated user userId={}", userId);

        return UpdateUserResponse.builder()
                .userId(user.getId())
                .fullName(user.getFullName())
                .location(user.getLocation())
                .avatarUrl(user.getAvatarUrl())
                .contactPhone(user.getContactPhone())
                .userType(user.getUserType() != null ? user.getUserType().name() : null)
                .role(user.getRoles() != null ? user.getRoles().getCode() : null)
                .build();
    }

}
