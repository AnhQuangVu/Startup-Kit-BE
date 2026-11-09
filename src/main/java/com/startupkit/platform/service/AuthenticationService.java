package com.startupkit.platform.service;

import com.nimbusds.jwt.SignedJWT;
import com.startupkit.platform.dto.request.LoginRequest;
import com.startupkit.platform.dto.response.LoginResponse;
import com.startupkit.platform.entity.InvalidatedToken;
import com.startupkit.platform.entity.Role;
import com.startupkit.platform.entity.User;
import com.startupkit.platform.entity.UserIdentity;
import com.startupkit.platform.enums.IdentityProvider;
import com.startupkit.platform.exception.AppException;
import com.startupkit.platform.exception.ErrorCode;
import com.startupkit.platform.repository.InvalidatedTokenRepository;
import com.startupkit.platform.repository.UserIdentityRepository;
import com.startupkit.platform.repository.UserRepository;
import jakarta.transaction.Transactional;
import lombok.AccessLevel;
import lombok.RequiredArgsConstructor;
import lombok.experimental.FieldDefaults;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.text.ParseException;
import java.time.Instant;
import java.util.Date;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Slf4j
@FieldDefaults(level = AccessLevel.PRIVATE, makeFinal = true)
public class AuthenticationService {
    UserIdentityRepository identityRepo;
    UserRepository userRepo;
    JwtService jwtService;
    PasswordEncoder passwordEncoder;
    UserIdentityRepository userIdentityRepository;
    EmailService emailService;
    JwtPasswordService jwtPasswordService;
    InvalidatedTokenRepository invalidatedTokenRepo;

    public LoginResponse login(LoginRequest request) {

        //tìm user theo provider LOCAL + EMAIL
        UserIdentity identity = identityRepo
                .findByProviderAndProviderUserId(IdentityProvider.LOCAL, request.getEmail())
                .orElseThrow(() -> {
                    log.warn("Login failed: identity not found for email={}", request.getEmail());
                    return new AppException(ErrorCode.INVALID_CREDENTIALS);
                });
        // kiểm tra mật khẩu
        if (!passwordEncoder.matches(request.getPassword(), identity.getPassword())) {
            log.warn("Login failed: wrong password for email={}", request.getEmail());
            throw new AppException(ErrorCode.INVALID_CREDENTIALS);
        }

        User user = identity.getUser();

        //kiểm tra trạng thái của tài khoản
        switch (user.getAccountStatus()) {
            case BANNED -> throw new AppException(ErrorCode.ACCOUNT_BANNED);
            case INACTIVE -> throw new AppException(ErrorCode.ACCOUNT_INACTIVE);
        }

        //kiểm tra đã verify chưa
        if (!user.isVerified()) {
            // Gợi ý user kiểm tra email, không chặn mãi mãi
            throw new AppException(ErrorCode.EMAIL_NOT_VERIFIED);
        }

        //kiểm tra có yêu cầu đổi mật khẩu không(dùng khi admin reset mật khẩu tạm cho user)
        log.info("=== ALL CHECKS PASSED, building response...");
        try {
            LoginResponse response = buildLoginResponse(user);
            log.info("=== RESPONSE BUILT OK");
            return response;
        } catch (Exception e) {
            log.error("=== ERROR in buildLoginResponse: {}", e.getMessage(), e);
            throw e;
        }

    }

    private LoginResponse buildLoginResponse(User user) {
        String accessToken = jwtService.generateAccessToken(user);
        String refreshToken = jwtService.generateRefreshToken(user);

        Set<String> roles = (user.getRoles() == null)
                ? Set.of()
                : Set.of(user.getRoles().getCode()); // Tạo Set chứa 1 phần tử duy nhất

        return LoginResponse.builder()
                .accessToken(accessToken)
                .refreshToken(refreshToken)
                .tokenType("Bearer")
                .build();
    }

    public void resetPassword(String token, String newPassword) throws ParseException {
        jwtPasswordService.validateTokenPassword(token);

        SignedJWT jwt = SignedJWT.parse(token);
        UUID userIdentityId = UUID.fromString(jwt.getJWTClaimsSet().getSubject());

        UserIdentity userIdentity = userIdentityRepository.findById(userIdentityId)
                .orElseThrow(() -> new AppException(ErrorCode.USER_NOT_EXISTED));

        userIdentity.setPassword(passwordEncoder.encode(newPassword));
        userIdentity.setLastPasswordChange(Instant.now());
        userIdentityRepository.save(userIdentity);
    }

    public void forgotPassword(String email) {
        var identityOptional = userIdentityRepository
                .findByProviderAndProviderUserId(IdentityProvider.LOCAL, email);

        identityOptional.ifPresent(userIdentity -> {
            String token = jwtPasswordService.generateResetPasswordToKen(userIdentity.getId());
            emailService.sendLinkResetPassword(email, token);
        });
    }

    @Transactional
    public LoginResponse refreshToken(String token) {
        SignedJWT jwt = jwtService.verifyToken(token, "refresh");

        try {
            String userId  = jwt.getJWTClaimsSet().getSubject();
            UUID jwtId     = UUID.fromString(jwt.getJWTClaimsSet().getJWTID());
            Date expiryTime = jwt.getJWTClaimsSet().getExpirationTime();

            // Invalidate refresh token cũ (rotation)
            invalidatedTokenRepo.save(InvalidatedToken.builder()
                    .id(jwtId)
                    .expiryTime(expiryTime)
                    .build());

            User user = userRepo.findById(UUID.fromString(userId))
                    .orElseThrow(() -> new AppException(ErrorCode.USER_NOT_EXISTED));

            log.info("Refresh token rotated for userId={}", userId);

            return buildLoginResponse(user);

        } catch (ParseException e) {
            throw new AppException(ErrorCode.UNAUTHENTICATED);
        }
    }
}
