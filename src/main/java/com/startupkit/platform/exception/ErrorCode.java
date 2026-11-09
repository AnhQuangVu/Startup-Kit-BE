package com.startupkit.platform.exception;

import lombok.Getter;
import org.springframework.http.HttpStatus;
import org.springframework.http.HttpStatusCode;

@Getter
public enum ErrorCode {
    // SYSTEM
    UNCATEGORIZED_EXCEPTION(9999, "Uncategorized error", HttpStatus.INTERNAL_SERVER_ERROR),
    INVALID_KEY(1000, "Invalid key", HttpStatus.BAD_REQUEST),

    // USER MODULE (1001 - 1099)
    USER_ALREADY_EXISTED(1001, "User already existed", HttpStatus.CONFLICT),
    USER_NOT_EXISTED(1002, "User not existed", HttpStatus.NOT_FOUND),
    USERNAME_INVALID(1003, "Username must be at least {min} characters", HttpStatus.BAD_REQUEST),
    USERNAME_INVALID_FORMAT(1004, "Username invalid format", HttpStatus.BAD_REQUEST),
    PASSWORD_INVALID(1005, "Password must be at least {min} characters", HttpStatus.BAD_REQUEST),
    PASSWORD_NOT_MATCH(1006, "Password and confirm password do not match", HttpStatus.BAD_REQUEST),
    EMAIL_INVALID(1007, "Email is not in correct format", HttpStatus.BAD_REQUEST),
    USER_TYPE_REQUIRED(1008, "User type must not be empty", HttpStatus.BAD_REQUEST),
    INVALID_DOB(1009, "Your age must be at least {min}", HttpStatus.BAD_REQUEST),

    // AUTH MODULE (1101 - 1199)
    UNAUTHENTICATED(1101, "Unauthenticated", HttpStatus.UNAUTHORIZED),
    UNAUTHORIZED(1102, "You do not have permission", HttpStatus.FORBIDDEN),
    INVALID_CREDENTIALS(1103, "Email or password is incorrect", HttpStatus.UNAUTHORIZED),
    EMAIL_NOT_VERIFIED(1104, "Email is not verified. Please check your inbox", HttpStatus.FORBIDDEN),
    ACCOUNT_BANNED(1105, "Your account has been banned", HttpStatus.FORBIDDEN),
    ACCOUNT_INACTIVE(1106, "Your account is inactive", HttpStatus.FORBIDDEN),
    MUST_CHANGE_PASSWORD(1107, "You must change your password before continuing", HttpStatus.FORBIDDEN),
    INVALID_TOKEN(1108, "Invalid or expired token", HttpStatus.UNAUTHORIZED),
    TOKEN_EXPIRED(1109, "Token has expired", HttpStatus.UNAUTHORIZED),

    PROFILE_NOT_FOUND(1015, "Profile not found", HttpStatus.NOT_FOUND),
    ;
    ErrorCode(int code, String message, HttpStatusCode statusCode) {
        this.code = code;
        this.message = message;
        this.statusCode = statusCode;
    }

    private final int code;
    private final String message;
    private final HttpStatusCode statusCode;
}
