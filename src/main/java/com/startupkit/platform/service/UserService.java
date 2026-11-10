package com.startupkit.platform.service;

import com.startupkit.platform.dto.request.UpdateUserRequest;
import com.startupkit.platform.dto.request.UserCreateRequest;
import com.startupkit.platform.dto.response.UpdateUserResponse;
import com.startupkit.platform.dto.response.UserCreateResponse;
import com.startupkit.platform.entity.Investor;
import com.startupkit.platform.entity.Mentor;
import com.startupkit.platform.entity.Role;
import com.startupkit.platform.entity.Startup;
import com.startupkit.platform.entity.User;
import com.startupkit.platform.entity.UserIdentity;
import com.startupkit.platform.enums.IdentityProvider;
import com.startupkit.platform.enums.UserType;
import com.startupkit.platform.exception.AppException;
import com.startupkit.platform.exception.ErrorCode;
import com.startupkit.platform.mapper.UserMapper;
import com.startupkit.platform.repository.InvestorRepository;
import com.startupkit.platform.repository.MentorRepository;
import com.startupkit.platform.repository.RoleRepository;
import com.startupkit.platform.repository.StartupRepository;
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
    StartupRepository startupRepo;
    InvestorRepository investorRepo;
    MentorRepository mentorRepo;
    UserMapper userMapper;
    PasswordEncoder passwordEncoder;

    @Transactional
    public UserCreateResponse createUser(UserCreateRequest request) {
        if (userRepository.existsByContactEmail(request.getEmail())) {
            throw new AppException(ErrorCode.USER_ALREADY_EXISTED);
        }

        User user = userMapper.toUser(request);
        user.setContactEmail(request.getEmail());
        user.setUserType(request.getUserType());
        user.setVerified(true);

        if (request.getUserType() != null) {
            Role role = roleRepository.findById(request.getUserType().name()).orElse(null);
            user.setRoles(role);
        }

        UserIdentity userIdentity = UserIdentity.builder()
                .user(user)
                .provider(IdentityProvider.LOCAL)
                .providerUserId(request.getEmail())
                .email(request.getEmail())
                .password(passwordEncoder.encode(request.getPassword()))
                .verified(true)
                .build();

        user.setUserIdentity(userIdentity);
        user = userRepository.save(user);

        if (request.getUserType() == UserType.STARTUP) {
            startupRepo.save(Startup.builder()
                    .user(user)
                    .industry("Technology")
                    .description("Innovative startup on StartupKit")
                    .teamSize(1)
                    .build());
        } else if (request.getUserType() == UserType.INVESTOR) {
            investorRepo.save(Investor.builder()
                    .user(user)
                    .organizationName("Private Investor")
                    .bio("Active investor on StartupKit")
                    .investmentCriteria("Seed, Early Stage")
                    .preferredStages("Seed")
                    .investmentMin(10000.0)
                    .investmentMax(250000.0)
                    .build());
        } else if (request.getUserType() == UserType.MENTOR) {
            mentorRepo.save(Mentor.builder()
                    .user(user)
                    .bio("Ecosystem mentor on StartupKit")
                    .expertise("Product, Growth, Strategy")
                    .build());
        }

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
