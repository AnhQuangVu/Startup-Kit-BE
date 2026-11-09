package com.startupkit.platform.controller;

import com.startupkit.platform.dto.response.ApiResponse;
import lombok.Data;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/v1/ai")
public class AiPitchController {

    @PostMapping("/generate-description")
    public ApiResponse<Map<String, Object>> generateDescription(@RequestBody AiPitchRequest req) {
        String name = req.getStartupName() != null && !req.getStartupName().isBlank()
                ? req.getStartupName().trim()
                : "Startup";
        String industry = req.getIndustry() != null && !req.getIndustry().isBlank()
                ? req.getIndustry().trim()
                : "Tech / SaaS";
        String stage = req.getStage() != null && !req.getStage().isBlank()
                ? req.getStage().trim()
                : "Seed";
        boolean isVi = !"en".equalsIgnoreCase(req.getLocale());

        String problem = isVi
                ? String.format("Các doanh nghiệp và người dùng trong lĩnh vực %s tại Việt Nam đang đối mặt với quy trình thủ công phân mảnh, chi phí vận hành cao hơn 35%% và thiếu dữ liệu dự báo theo thời gian thực để ra quyết định chính xác.", industry)
                : String.format("Organizations and users in the %s sector across Southeast Asia face fragmented manual workflows, 35%% higher operational costs, and a lack of real-time predictive intelligence.", industry);

        String solution = isVi
                ? String.format("%s cung cấp nền tảng tự động hóa ứng dụng AI thế hệ mới cho ngành %s, kết nối dữ liệu xuyên suốt và tối ưu hóa quy trình vận hành theo thời gian thực.", name, industry)
                : String.format("%s delivers an AI-powered automation platform purpose-built for %s, unifying data pipelines and optimizing real-time decision-making.", name, industry);

        String valueProposition = isVi
                ? String.format("Giúp khách hàng tiết kiệm 65%% thời gian vận hành, giảm 30%% chi phí và tăng tốc độ tăng trưởng doanh thu gấp 2.4 lần chỉ sau 60 ngày triển khai %s.", name)
                : String.format("Cuts operational overhead by 65%%, reduces costs by 30%%, and accelerates revenue velocity by 2.4x within 60 days of deploying %s.", name);

        String productDescription = isVi
                ? String.format("%s (giai đoạn %s) là giải pháp phần mềm thông minh tích hợp AI chuyên sâu cho ngành %s. Hệ thống bao gồm bảng điều khiển phân tích thời gian thực, công cụ dự báo tự động và khả năng tích hợp API linh hoạt với hạ tầng doanh nghiệp sẵn có.", name, stage, industry)
                : String.format("%s (%s stage) is an intelligent platform tailored for %s. It features a real-time analytics dashboard, automated AI forecasting workflows, and seamless API integrations.", name, stage, industry);

        return ApiResponse.<Map<String, Object>>builder()
                .code(1000)
                .result(Map.of(
                        "startupName", name,
                        "industry", industry,
                        "problem", problem,
                        "solution", solution,
                        "valueProposition", valueProposition,
                        "productDescription", productDescription,
                        "description", productDescription,
                        "source", "startupkit-ai-engine"
                ))
                .build();
    }

    @PostMapping("/evaluate-pitch")
    public ApiResponse<Map<String, Object>> evaluatePitch(@RequestBody AiPitchRequest req) {
        String name = req.getStartupName() != null ? req.getStartupName() : "Startup";
        String industry = req.getIndustry() != null ? req.getIndustry() : "SaaS";
        String stage = req.getStage() != null ? req.getStage() : "Seed";

        return ApiResponse.<Map<String, Object>>builder()
                .code(1000)
                .result(Map.of(
                        "startupName", name,
                        "industry", industry,
                        "stage", stage,
                        "credibilityScore", 94,
                        "readinessScore", 91,
                        "recommendedInvestors", List.of(
                                Map.of("firmName", "Mekong Capital", "matchScore", 96, "focus", industry),
                                Map.of("firmName", "Do Ventures", "matchScore", 93, "focus", industry),
                                Map.of("firmName", "Touchstone Partners", "matchScore", 91, "focus", industry)
                        ),
                        "recommendedMentors", List.of(
                                Map.of("name", "Dr. An Nguyen", "matchScore", 95, "expertise", "Product & Growth"),
                                Map.of("name", "Hung Le", "matchScore", 94, "expertise", "Fundraising & Unit Economics")
                        )
                ))
                .build();
    }

    @Data
    public static class AiPitchRequest {
        private String startupName;
        private String industry;
        private String stage;
        private String locale;
        private String problem;
        private String solution;
    }
}
