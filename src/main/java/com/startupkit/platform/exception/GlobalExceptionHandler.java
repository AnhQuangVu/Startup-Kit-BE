package com.startupkit.platform.exception;

import com.startupkit.platform.dto.response.ApiResponse;
import jakarta.validation.ConstraintViolation;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import java.util.Map;
import java.util.Objects;

@RestControllerAdvice
@Slf4j
public class GlobalExceptionHandler {

    @ExceptionHandler(value = RuntimeException.class)
    ResponseEntity<ApiResponse> handlingRuntimeException(RuntimeException exception) {
        log.error("RuntimeException: ", exception);
        if (exception instanceof AppException appEx) {
            return handlingAppException(appEx);
        }
        ApiResponse apiResponse = new ApiResponse();
        apiResponse.setCode(ErrorCode.UNCATEGORIZED_EXCEPTION.getCode());
        apiResponse.setMessage(exception.getMessage() != null && !exception.getMessage().isBlank()
                ? exception.getMessage()
                : ErrorCode.UNCATEGORIZED_EXCEPTION.getMessage());
        return ResponseEntity.badRequest().body(apiResponse);
    }

    @ExceptionHandler(value = AppException.class)
    ResponseEntity<ApiResponse> handlingAppException(AppException exception) {
        ErrorCode errorCode = exception.getErrorCode();
        ApiResponse apiResponse = new ApiResponse();
        apiResponse.setCode(errorCode.getCode());
        apiResponse.setMessage(errorCode.getMessage());
        return ResponseEntity.status(errorCode.getStatusCode()).body(apiResponse);
    }

    @ExceptionHandler(value = AccessDeniedException.class)
    ResponseEntity<ApiResponse> handlingAccessDeniedException(AccessDeniedException exception) {
        ErrorCode errorCode = ErrorCode.UNAUTHORIZED;
        return ResponseEntity.status(errorCode.getStatusCode())
                .body(ApiResponse.builder()
                        .code(errorCode.getCode())
                        .message(errorCode.getMessage())
                        .build());
    }

    @ExceptionHandler(value = MethodArgumentNotValidException.class)
    ResponseEntity<ApiResponse> handlingValidation(MethodArgumentNotValidException exception) {

        var globalErrors = exception.getBindingResult().getGlobalErrors();
        if (!globalErrors.isEmpty()) {
            String enumKey = globalErrors.get(0).getDefaultMessage();
            log.info("Global error key: {}", enumKey);
            try {
                ErrorCode errorCode = ErrorCode.valueOf(enumKey);
                return ResponseEntity.status(errorCode.getStatusCode())
                        .body(ApiResponse.builder()
                                .code(errorCode.getCode())
                                .message(errorCode.getMessage())
                                .build());
            } catch (IllegalArgumentException e) {
                log.warn("Unknown global ErrorCode: {}", enumKey);
            }
        }



        var fieldError = exception.getFieldError();
        String enumKey = (fieldError != null) ? fieldError.getDefaultMessage() : "INVALID_KEY";

        ErrorCode errorCode = ErrorCode.INVALID_KEY;
        Map<String, Object> attributes = null;

        try {
            errorCode = ErrorCode.valueOf(enumKey);
            var allErrors = exception.getBindingResult().getAllErrors();
            if (!allErrors.isEmpty()) {
                var constraintViolation = allErrors.get(0).unwrap(ConstraintViolation.class);
                attributes = constraintViolation.getConstraintDescriptor().getAttributes();
                log.info("Validation attributes: {}", attributes);
            }
        } catch (IllegalArgumentException | ClassCastException e) {
            log.warn("Could not parse ErrorCode or Attributes: {}", e.getMessage());
        }

        ApiResponse apiResponse = ApiResponse.builder()
                .code(errorCode.getCode())
                .message(Objects.nonNull(attributes)
                        ? mapAttribute(errorCode.getMessage(), attributes)
                        : errorCode.getMessage())
                .build();

        return ResponseEntity.status(errorCode.getStatusCode()).body(apiResponse);
    }

    private String mapAttribute(String message, Map<String, Object> attributes) {
        if (!message.contains("{")) return message;
        for (Map.Entry<String, Object> entry : attributes.entrySet()) {
            String key = "{" + entry.getKey() + "}";
            if (message.contains(key)) {
                message = message.replace(key, String.valueOf(entry.getValue()));
            }
        }
        return message;
    }
}