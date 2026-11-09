package com.startupkit.platform.config;

import com.startupkit.platform.entity.User;
import com.startupkit.platform.repository.UserRepository;
import lombok.AccessLevel;
import lombok.RequiredArgsConstructor;
import lombok.experimental.FieldDefaults;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;

import java.util.UUID;

@Component
@RequiredArgsConstructor
@FieldDefaults(level = AccessLevel.PRIVATE, makeFinal = true)
public class SecurityUtils {
    UserRepository userRepository;

    public String getCurrentUserId() {

        var authentication = SecurityContextHolder
                .getContext()
                .getAuthentication();

        return authentication.getName();
    }

    public User getCurrentUser() {
        String name = getCurrentUserId();

        UUID userId = UUID.fromString(name);

        return userRepository.findById(userId)
                .orElseThrow(() -> new RuntimeException("User not found"));
    }


}
