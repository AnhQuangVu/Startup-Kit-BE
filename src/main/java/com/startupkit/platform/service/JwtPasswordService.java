package com.startupkit.platform.service;

import com.nimbusds.jose.*;
import com.nimbusds.jose.crypto.MACSigner;
import com.nimbusds.jwt.JWTClaimsSet;
import com.nimbusds.jwt.SignedJWT;
import com.startupkit.platform.entity.InvalidatedToken;
import com.startupkit.platform.entity.UserIdentity;
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
import org.springframework.stereotype.Service;

import java.text.ParseException;
import java.time.Instant;
import java.util.Date;
import java.util.UUID;

import static java.time.temporal.ChronoUnit.MINUTES;

@Service
@Slf4j
@RequiredArgsConstructor
@FieldDefaults(level = AccessLevel.PRIVATE, makeFinal = true)
public class JwtPasswordService {
    private final UserIdentityRepository userIdentityRepository;
    private final InvalidatedTokenRepository invalidatedTokenRepository;
    private final JwtService jwtService;
    @NonFinal
    @Value("${jwt.signerKey}")
    String secretKey;

    // tạo token reset password
    public String generateResetPasswordToKen (UUID userIdentityId) {
        JWSHeader jwsHeader = new JWSHeader(JWSAlgorithm.HS512);

        JWTClaimsSet jwtClaimsSet = new JWTClaimsSet.Builder()
                .jwtID(String.valueOf(UUID.randomUUID()))
                .subject(userIdentityId.toString())
                .issuer("startupkit.com")
                .issueTime(new Date())
                .expirationTime(Date.from(Instant.now().plus(15, MINUTES)))
                .claim("token_type","reset_password")
                .build();

        Payload payload = new Payload(jwtClaimsSet.toJSONObject());

        JWSObject jwsObject = new JWSObject(jwsHeader , payload);

        try {
            jwsObject.sign(new MACSigner(secretKey.getBytes()));
            return jwsObject.serialize();
        } catch (JOSEException e) {
            log.error("Cannot create token", e);
            throw new RuntimeException(e);
        }
    }

    public void validateTokenPassword(String token) throws ParseException {
        SignedJWT jwt = jwtService.verifyToken(token, "reset_password");

        UserIdentity userIdentity = userIdentityRepository
                .findById(UUID.fromString(jwt.getJWTClaimsSet().getSubject()))
                .orElseThrow(() -> new AppException(ErrorCode.USER_NOT_EXISTED));

        Instant lastChange = userIdentity.getLastPasswordChange();
        if (lastChange != null && jwt.getJWTClaimsSet().getIssueTime().before(Date.from(lastChange)))
            throw new AppException(ErrorCode.INVALID_TOKEN);

        invalidatedTokenRepository.save(InvalidatedToken.builder()
                .id(UUID.fromString(jwt.getJWTClaimsSet().getJWTID()))
                .expiryTime(jwt.getJWTClaimsSet().getExpirationTime())
                .build());
    }

}
