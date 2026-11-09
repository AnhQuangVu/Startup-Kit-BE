package com.startupkit.platform.controller;

import com.startupkit.platform.dto.response.ApiResponse;
import com.startupkit.platform.entity.Deal;
import com.startupkit.platform.entity.Investor;
import com.startupkit.platform.entity.Project;
import com.startupkit.platform.entity.Startup;
import com.startupkit.platform.enums.DealStatus;
import com.startupkit.platform.repository.DealRepository;
import com.startupkit.platform.repository.InvestorRepository;
import com.startupkit.platform.repository.ProjectRepository;
import com.startupkit.platform.repository.StartupRepository;
import lombok.AccessLevel;
import lombok.Data;
import lombok.RequiredArgsConstructor;
import lombok.experimental.FieldDefaults;
import org.springframework.web.bind.annotation.*;

import java.time.Instant;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/v1/deals")
@RequiredArgsConstructor
@FieldDefaults(level = AccessLevel.PRIVATE, makeFinal = true)
public class DealController {

    DealRepository dealRepository;
    StartupRepository startupRepository;
    InvestorRepository investorRepository;
    ProjectRepository projectRepository;

    @GetMapping
    public ApiResponse<List<Map<String, Object>>> listDeals(
            @RequestParam(required = false) UUID startupId,
            @RequestParam(required = false) UUID investorId) {
        List<Deal> deals;
        if (startupId != null) {
            deals = dealRepository.findByStartupId(startupId);
        } else if (investorId != null) {
            deals = dealRepository.findByInvestorId(investorId);
        } else {
            deals = dealRepository.findAll();
        }
        List<Map<String, Object>> result = deals.stream()
                .map(this::toDto)
                .collect(Collectors.toList());
        return ApiResponse.<List<Map<String, Object>>>builder()
                .code(1000)
                .result(result)
                .build();
    }

    @GetMapping("/{id}")
    public ApiResponse<Map<String, Object>> getDeal(@PathVariable UUID id) {
        Deal deal = dealRepository.findById(id).orElse(null);
        return ApiResponse.<Map<String, Object>>builder()
                .code(1000)
                .result(deal != null ? toDto(deal) : null)
                .build();
    }

    @PostMapping
    public ApiResponse<Map<String, Object>> createDeal(@RequestBody CreateDealRequest req) {
        Startup startup = startupRepository.findById(req.getStartupId()).orElse(null);
        Investor investor = investorRepository.findById(req.getInvestorId()).orElse(null);
        Project project = projectRepository.findById(req.getProjectId()).orElse(null);
        if (startup == null || investor == null || project == null) {
            return ApiResponse.<Map<String, Object>>builder()
                    .code(1002)
                    .message("Startup, Investor, or Project not found")
                    .build();
        }
        double value = req.getContractValue() != null ? req.getContractValue() : 100000.0;
        Deal deal = Deal.builder()
                .startup(startup)
                .investor(investor)
                .project(project)
                .contractValue(value)
                .successFee(value * 0.10) // 10% platform success fee
                .status(DealStatus.PENDING)
                .signedAt(Instant.now())
                .build();
        Deal saved = dealRepository.save(deal);
        return ApiResponse.<Map<String, Object>>builder()
                .code(1000)
                .message("Deal created successfully")
                .result(toDto(saved))
                .build();
    }

    @PutMapping("/{id}/status")
    public ApiResponse<Map<String, Object>> updateStatus(
            @PathVariable UUID id,
            @RequestParam DealStatus status) {
        Deal deal = dealRepository.findById(id).orElse(null);
        if (deal == null) {
            return ApiResponse.<Map<String, Object>>builder()
                    .code(1002)
                    .message("Deal not found")
                    .build();
        }
        deal.setStatus(status);
        return ApiResponse.<Map<String, Object>>builder()
                .code(1000)
                .message("Deal status updated")
                .result(toDto(dealRepository.save(deal)))
                .build();
    }

    @PostMapping("/{id}/sign-nda")
    public ApiResponse<Map<String, Object>> signNda(@PathVariable UUID id) {
        return ApiResponse.<Map<String, Object>>builder()
                .code(1000)
                .message("Electronic Mutual NDA signed successfully")
                .result(Map.of(
                        "dealId", id,
                        "ndaSigned", true,
                        "signedAt", Instant.now().toString()
                ))
                .build();
    }

    private Map<String, Object> toDto(Deal d) {
        Map<String, Object> m = new HashMap<>();
        m.put("id", d.getId());
        m.put("startupId", d.getStartup() != null ? d.getStartup().getId() : null);
        m.put("investorId", d.getInvestor() != null ? d.getInvestor().getId() : null);
        m.put("projectId", d.getProject() != null ? d.getProject().getId() : null);
        m.put("projectName", d.getProject() != null ? d.getProject().getProjectName() : null);
        m.put("contractValue", d.getContractValue());
        m.put("successFee", d.getSuccessFee());
        m.put("status", d.getStatus());
        m.put("signedAt", d.getSignedAt());
        return m;
    }

    @Data
    public static class CreateDealRequest {
        private UUID startupId;
        private UUID investorId;
        private UUID projectId;
        private Double contractValue;
    }
}
