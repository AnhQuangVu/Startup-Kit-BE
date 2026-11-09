package com.startupkit.platform.service;

import com.nimbusds.jose.*;
import com.nimbusds.jose.crypto.*;
import com.nimbusds.jwt.*;
import com.startupkit.platform.entity.Role;
import com.startupkit.platform.entity.User;
import com.startupkit.platform.exception.AppException;
import com.startupkit.platform.exception.ErrorCode;
import com.startupkit.platform.repository.InvalidatedTokenRepository;
import com.startupkit.platform.repository.UserIdentityRepository;
import lombok.AccessLevel;
import lombok.RequiredArgsConstructor;
import lombok.experimental.FieldDefaults;
import lombok.experimental.NonFinal;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.text.ParseException;
import java.time.Instant;
import java.util.Date;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;

import static java.time.temporal.ChronoUnit.MINUTES;

@Service
@Slf4j
@RequiredArgsConstructor
@FieldDefaults(level = AccessLevel.PRIVATE, makeFinal = true)
public class JwtService {

    InvalidatedTokenRepository invalidatedTokenRepo;
    UserIdentityRepository userIdentityRepository;

    // Dùng @NonFinal vì @Value không inject được vào final field
    @NonFinal
    @Value("${jwt.signerKey}")
    String secretKey;

    @NonFinal
    @Value("${jwt.valid-duration}")
    long accessTokenExpiry;

    @NonFinal
    @Value("${jwt.refreshable-duration}")
    long refreshTokenExpiry;

    // ── Generate ──────────────────────────────────────────────────────────
    public String generateAccessToken(User user) {
        return buildToken(user, accessTokenExpiry, "access");
    }

    public String generateRefreshToken(User user) {
        return buildToken(user, refreshTokenExpiry, "refresh");
    }

    private String buildToken(User user, long expirySeconds, String tokenType) {
        try {
            log.info("=== BUILD TOKEN START: userId={}, type={}", user.getId(), tokenType);
            log.info("=== KEY length={}", secretKey.length());

            JWSSigner signer = new MACSigner(secretKey.getBytes());
            log.info("=== SIGNER OK");

            Set<String> roles = (user.getRoles() == null)
                    ? Set.of()
                    : Set.of(user.getRoles().getCode()); // Tạo Set chứa 1 phần tử duy nhất
            log.info("=== ROLES OK: {}", roles);

            JWTClaimsSet claims = new JWTClaimsSet.Builder()
                    .jwtID(UUID.randomUUID().toString())
                    .subject(user.getId().toString())
                    .issuer("startupkit")
                    .issueTime(new Date())
                    .expirationTime(Date.from(Instant.now().plusSeconds(expirySeconds)))
                    .claim("email", user.getContactEmail())
                    .claim("roles", roles)
                    .claim("token_type", tokenType)
                    .build();
            log.info("=== CLAIMS OK");

            SignedJWT jwt = new SignedJWT(new JWSHeader(JWSAlgorithm.HS256), claims);
            jwt.sign(signer);
            log.info("=== SIGNED OK");

            return jwt.serialize();

        } catch (JOSEException e) {
            log.error("=== JOSE ERROR: {}", e.getMessage(), e);
            throw new AppException(ErrorCode.UNCATEGORIZED_EXCEPTION);
        }
    }

    // ── Verify ────────────────────────────────────────────────────────────
    public SignedJWT verifyToken(String token, String expectedType) {
        try {
            SignedJWT jwt = SignedJWT.parse(token);

            JWSVerifier verifier = new MACVerifier(secretKey.getBytes());
            if (!jwt.verify(verifier))
                throw new AppException(ErrorCode.UNAUTHENTICATED);

            if (jwt.getJWTClaimsSet().getExpirationTime().before(new Date()))
                throw new AppException(ErrorCode.TOKEN_EXPIRED);

            UUID jwtId = UUID.fromString(jwt.getJWTClaimsSet().getJWTID());
            if (invalidatedTokenRepo.existsById(jwtId))
                throw new AppException(ErrorCode.INVALID_TOKEN);

            if (expectedType != null) {
                String tokenType = (String) jwt.getJWTClaimsSet().getClaim("token_type");
                if (!expectedType.equals(tokenType))
                    throw new AppException(ErrorCode.INVALID_TOKEN);
            }

            return jwt;

        } catch (ParseException | JOSEException e) {
            throw new AppException(ErrorCode.UNAUTHENTICATED);
        }
    }



}