package com.startupkit.platform.controller;

import com.startupkit.platform.dto.response.ApiResponse;
import com.startupkit.platform.entity.Investor;
import com.startupkit.platform.entity.Mentor;
import com.startupkit.platform.entity.Startup;
import com.startupkit.platform.repository.InvestorRepository;
import com.startupkit.platform.repository.MentorRepository;
import com.startupkit.platform.repository.StartupRepository;
import lombok.AccessLevel;
import lombok.RequiredArgsConstructor;
import lombok.experimental.FieldDefaults;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/v1/market")
@RequiredArgsConstructor
@FieldDefaults(level = AccessLevel.PRIVATE, makeFinal = true)
public class MarketplaceController {

    StartupRepository startupRepository;
    InvestorRepository investorRepository;
    MentorRepository mentorRepository;

    @GetMapping("/startups")
    public ApiResponse<List<Map<String, Object>>> getStartups(
            @RequestParam(required = false) String industry) {
        List<Map<String, Object>> result = startupRepository.findAll().stream()
                .filter(s -> industry == null || industry.isBlank() || industry.equalsIgnoreCase(s.getIndustry()))
                .map(this::mapStartup)
                .collect(Collectors.toList());
        return ApiResponse.<List<Map<String, Object>>>builder()
                .code(1000)
                .result(result)
                .build();
    }

    @GetMapping("/investors")
    public ApiResponse<List<Map<String, Object>>> getInvestors() {
        List<Map<String, Object>> result = investorRepository.findAll().stream()
                .map(this::mapInvestor)
                .collect(Collectors.toList());
        return ApiResponse.<List<Map<String, Object>>>builder()
                .code(1000)
                .result(result)
                .build();
    }

    @GetMapping("/mentors")
    public ApiResponse<List<Map<String, Object>>> getMentors() {
        List<Map<String, Object>> result = mentorRepository.findAll().stream()
                .map(this::mapMentor)
                .collect(Collectors.toList());
        return ApiResponse.<List<Map<String, Object>>>builder()
                .code(1000)
                .result(result)
                .build();
    }

    private Map<String, Object> mapStartup(Startup s) {
        Map<String, Object> m = new HashMap<>();
        m.put("id", s.getId());
        m.put("founderName", s.getUser() != null ? s.getUser().getFullName() : "Founder");
        m.put("location", s.getUser() != null ? s.getUser().getLocation() : "Việt Nam");
        m.put("industry", s.getIndustry());
        m.put("description", s.getDescription());
        m.put("teamSize", s.getTeamSize());
        m.put("score", s.getCredibilityScore() != null ? s.getCredibilityScore().getAverageScore() : 90.0);
        return m;
    }

    private Map<String, Object> mapInvestor(Investor i) {
        Map<String, Object> m = new HashMap<>();
        m.put("id", i.getId());
        m.put("fullName", i.getUser() != null ? i.getUser().getFullName() : "Investor");
        m.put("organizationName", i.getOrganizationName());
        m.put("investmentCriteria", i.getInvestmentCriteria());
        m.put("preferredStages", i.getPreferredStages());
        m.put("investmentMin", i.getInvestmentMin());
        m.put("investmentMax", i.getInvestmentMax());
        m.put("bio", i.getBio());
        return m;
    }

    private Map<String, Object> mapMentor(Mentor mt) {
        Map<String, Object> m = new HashMap<>();
        m.put("id", mt.getId());
        m.put("fullName", mt.getUser() != null ? mt.getUser().getFullName() : "Mentor");
        m.put("expertise", mt.getExpertise());
        m.put("bio", mt.getBio());
        m.put("hourlyRate", mt.getHourlyRate());
        m.put("rating", mt.getRating());
        return m;
    }
}
