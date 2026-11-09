package com.startupkit.platform.dto.request;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class RefreshTokenRequest {
    private String token;
    private String refreshToken;

    public String getResolvedToken() {
        return (token != null && !token.isBlank()) ? token : refreshToken;
    }
}
