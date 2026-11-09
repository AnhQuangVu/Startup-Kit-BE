package com.startupkit.platform.config;

import com.startupkit.platform.entity.User;
import com.startupkit.platform.service.OAuth2AuthenticationService;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.AccessLevel;
import lombok.RequiredArgsConstructor;
import lombok.experimental.FieldDefaults;
import lombok.experimental.NonFinal;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.core.Authentication;
import org.springframework.security.oauth2.client.authentication.OAuth2AuthenticationToken;
import org.springframework.security.oauth2.core.user.OAuth2User;
import org.springframework.security.web.authentication.SimpleUrlAuthenticationSuccessHandler;
import org.springframework.stereotype.Component;
import org.springframework.web.util.UriComponentsBuilder;

import java.io.IOException;

@Component
@RequiredArgsConstructor
@Slf4j
@FieldDefaults(level = AccessLevel.PRIVATE, makeFinal = true)
public class OAuth2SuccessHandler extends SimpleUrlAuthenticationSuccessHandler {

    OAuth2AuthenticationService oAuth2AuthService;

    @NonFinal
    @Value("${app.oauth2-redirect-uri}")
    String redirectUri;

    @Override
    public void onAuthenticationSuccess(
            HttpServletRequest request,
            HttpServletResponse response,
            Authentication authentication) throws IOException {
        log.info("=== OAuth2SuccessHandler triggered ===");
        OAuth2User oAuth2User = (OAuth2User) authentication.getPrincipal();
        String registrationId = "google";
        if (authentication instanceof OAuth2AuthenticationToken oauthToken) {
            registrationId = oauthToken.getAuthorizedClientRegistrationId();
        }

        User user = oAuth2AuthService.loginWithOAuth2(registrationId, oAuth2User);
        String shortCode = oAuth2AuthService.createShortCode(user);

        String targetUrl = UriComponentsBuilder.fromUriString(redirectUri)
                .queryParam("code", shortCode)
                .build().toUriString();

        log.info("OAuth2 ({}) success, redirecting with short code", registrationId);
        getRedirectStrategy().sendRedirect(request, response, targetUrl);
    }
}
