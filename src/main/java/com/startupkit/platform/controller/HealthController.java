package com.startupkit.platform.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.time.Instant;
import java.util.Map;

@RestController
public class HealthController {

    @GetMapping({"/", "/v1/health"})
    public Map<String, Object> health() {
        return Map.of(
                "code", 1000,
                "status", "UP",
                "service", "StartupKit Platform Backend (Spring Boot 4 / Java 21)",
                "swagger_ui", "/swagger-ui/index.html",
                "openapi_json", "/v3/api-docs",
                "timestamp", Instant.now().toString()
        );
    }
}
