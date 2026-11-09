package com.startupkit.platform.service;

import com.startupkit.platform.dto.response.LoginResponse;
import com.startupkit.platform.entity.OAuthCode;
import com.startupkit.platform.entity.Role;
import com.startupkit.platform.entity.User;
import com.startupkit.platform.entity.UserIdentity;
import com.startupkit.platform.enums.AccountStatus;
import com.startupkit.platform.enums.IdentityProvider;
import com.startupkit.platform.enums.UserType;
import com.startupkit.platform.exception.AppException;
import com.startupkit.platform.exception.ErrorCode;
import com.startupkit.platform.repository.OAuthCodeRepository;
import com.startupkit.platform.repository.RoleRepository;
import com.startupkit.platform.repository.UserIdentityRepository;
import com.startupkit.platform.repository.UserRepository;
import lombok.AccessLevel;
import lombok.RequiredArgsConstructor;
import lombok.experimental.FieldDefaults;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.oauth2.core.user.OAuth2User;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.util.UUID;

@Service
@RequiredArgsConstructor
@Slf4j
@FieldDefaults(level = AccessLevel.PRIVATE, makeFinal = true)
public class OAuth2AuthenticationService {

    UserRepository userRepo;
    UserIdentityRepository identityRepo;
    RoleRepository roleRepo;
    JwtService jwtService;
    OAuthCodeRepository oauthCodeRepo;

    @Transactional
    public User loginWithGoogle(OAuth2User oAuth2User) {
        return loginWithOAuth2("google", oAuth2User);
    }

    @Transactional
    public User loginWithOAuth2(String registrationId, OAuth2User oAuth2User) {
        IdentityProvider provider = "linkedin".equalsIgnoreCase(registrationId)
                ? IdentityProvider.LINKEDIN
                : IdentityProvider.GOOGLE;

        String providerId = oAuth2User.getAttribute("sub");
        if (providerId == null) {
            Object idAttr = oAuth2User.getAttribute("id");
            providerId = idAttr != null ? String.valueOf(idAttr) : oAuth2User.getName();
        }
        String email = oAuth2User.getAttribute("email");
        String name = oAuth2User.getAttribute("name");
        if (name == null) {
            String given = oAuth2User.getAttribute("given_name");
            String family = oAuth2User.getAttribute("family_name");
            name = ((given != null ? given : "") + " " + (family != null ? family : "")).trim();
            if (name.isEmpty()) {
                name = email != null ? email.split("@")[0] : "StartupKit User";
            }
        }
        String avatarUrl = oAuth2User.getAttribute("picture");

        log.info("OAuth2 login: provider={}, providerId={}, email={}", provider, providerId, email);

        final String finalProviderId = providerId;
        final String finalName = name;
        UserIdentity identity = identityRepo
                .findByProviderAndProviderUserId(provider, finalProviderId)
                .orElseGet(() -> createNewOAuthUser(provider, finalProviderId, email, finalName, avatarUrl));

        User user = identity.getUser();

        if (avatarUrl != null && !avatarUrl.equals(user.getAvatarUrl())) {
            user.setAvatarUrl(avatarUrl);
            userRepo.save(user);
        }

        return user;
    }

    @Transactional
    public String createShortCode(User user) {
        String accessToken  = jwtService.generateAccessToken(user);
        String refreshToken = jwtService.generateRefreshToken(user);
        String code = UUID.randomUUID().toString().replace("-", "");

        OAuthCode oauthCode = OAuthCode.builder()
                .code(code)
                .accessToken(accessToken)
                .refreshToken(refreshToken)
                .expiryTime(Instant.now().plusSeconds(300))
                .build();

        oauthCodeRepo.save(oauthCode);
        log.info("Created short code, expires in 5 minutes");
        return code;
    }

    @Transactional
    public LoginResponse exchangeCode(String code) {
        OAuthCode oauthCode = oauthCodeRepo.findById(code)
                .orElseThrow(() -> {
                    log.warn("OAuth code not found: {}", code);
                    return new AppException(ErrorCode.UNAUTHENTICATED);
                });

        if (oauthCode.getExpiryTime().isBefore(Instant.now())) {
            oauthCodeRepo.delete(oauthCode);
            log.warn("OAuth code expired");
            throw new AppException(ErrorCode.UNAUTHENTICATED);
        }

        if (Boolean.TRUE.equals(oauthCode.getUsed())) {
            log.warn("OAuth code already used");
            throw new AppException(ErrorCode.UNAUTHENTICATED);
        }

        oauthCode.setUsed(true);
        oauthCodeRepo.save(oauthCode);

        return LoginResponse.builder()
                .accessToken(oauthCode.getAccessToken())
                .refreshToken(oauthCode.getRefreshToken())
                .tokenType("Bearer")
                .build();
    }

    private UserIdentity createNewOAuthUser(
            IdentityProvider provider, String providerId, String email, String name, String avatarUrl) {

        Role defaultRole = roleRepo.findById("STARTUP").orElse(null);

        User user = (email != null ? userRepo.findByContactEmail(email) : java.util.Optional.<User>empty())
                .orElseGet(() -> {
                    User newUser = User.builder()
                            .contactEmail(email)
                            .fullName(name)
                            .avatarUrl(avatarUrl)
                            .accountStatus(AccountStatus.ACTIVE)
                            .userType(UserType.STARTUP)
                            .roles(defaultRole)
                            .verified(true)
                            .build();
                    return userRepo.save(newUser);
                });

        UserIdentity newIdentity = UserIdentity.builder()
                .user(user)
                .provider(provider)
                .providerUserId(providerId)
                .email(email)
                .verified(true)
                .build();

        log.info("Created new {} identity for userId={}", provider, user.getId());
        return identityRepo.save(newIdentity);
    }
}
