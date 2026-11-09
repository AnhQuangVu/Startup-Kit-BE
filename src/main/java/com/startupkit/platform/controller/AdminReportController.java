package com.startupkit.platform.controller;

import com.startupkit.platform.dto.response.ApiResponse;
import com.startupkit.platform.entity.Report;
import com.startupkit.platform.repository.ReportRepository;
import lombok.AccessLevel;
import lombok.RequiredArgsConstructor;
import lombok.experimental.FieldDefaults;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/v1/admin")
@RequiredArgsConstructor
@FieldDefaults(level = AccessLevel.PRIVATE, makeFinal = true)
public class AdminReportController {

    ReportRepository reportRepository;

    @GetMapping("/reports")
    public ApiResponse<List<Report>> getReports(@RequestParam(required = false) String status) {
        if (status == null || status.isBlank() || "ALL".equalsIgnoreCase(status)) {
            return ApiResponse.<List<Report>>builder()
                    .code(1000)
                    .result(reportRepository.findAll())
                    .build();
        }
        return ApiResponse.<List<Report>>builder()
                .code(1000)
                .result(reportRepository.findByStatusIgnoreCase(status))
                .build();
    }

    @PostMapping("/reports")
    public ApiResponse<Report> createReport(@RequestBody Report payload) {
        String id = payload.getId() != null && !payload.getId().isBlank()
                ? payload.getId()
                : "RPT-" + (1000 + reportRepository.count() + 1);
        Report item = Report.builder()
                .id(id)
                .type(payload.getType() != null ? payload.getType() : "Fake Startup")
                .target(payload.getTarget())
                .reporter(payload.getReporter() != null ? payload.getReporter() : "User")
                .reason(payload.getReason())
                .severity(payload.getSeverity() != null ? payload.getSeverity() : "High")
                .createdAt(LocalDate.now().toString())
                .status("Open")
                .resolutionNote("")
                .build();
        return ApiResponse.<Report>builder()
                .code(1000)
                .message("Report created successfully")
                .result(reportRepository.save(item))
                .build();
    }

    @PutMapping("/reports/{id}/status")
    public ApiResponse<Report> updateReportStatus(
            @PathVariable String id,
            @RequestBody Map<String, String> body) {
        Report item = reportRepository.findById(id).orElse(null);
        if (item == null) {
            return ApiResponse.<Report>builder()
                    .code(1002)
                    .message("Report not found")
                    .build();
        }
        item.setStatus(body.getOrDefault("status", "Resolved"));
        if (body.containsKey("resolutionNote")) {
            item.setResolutionNote(body.get("resolutionNote"));
        }
        return ApiResponse.<Report>builder()
                .code(1000)
                .message("Report status updated")
                .result(reportRepository.save(item))
                .build();
    }
}
