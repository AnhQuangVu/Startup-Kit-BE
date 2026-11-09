package com.startupkit.platform.controller;

import com.startupkit.platform.dto.response.ApiResponse;
import com.startupkit.platform.entity.Project;
import com.startupkit.platform.repository.ProjectRepository;
import lombok.AccessLevel;
import lombok.Data;
import lombok.RequiredArgsConstructor;
import lombok.experimental.FieldDefaults;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/v1/projects")
@RequiredArgsConstructor
@FieldDefaults(level = AccessLevel.PRIVATE, makeFinal = true)
public class ProjectController {

    ProjectRepository projectRepository;

    @GetMapping
    public ApiResponse<List<Project>> listProjects(
            @RequestParam(required = false) UUID startupId) {
        List<Project> items = startupId != null
                ? projectRepository.findByStartupId(startupId)
                : projectRepository.findAll();
        return ApiResponse.<List<Project>>builder()
                .code(1000)
                .result(items)
                .build();
    }

    @GetMapping("/{id}")
    public ApiResponse<Project> getProject(@PathVariable UUID id) {
        Project project = projectRepository.findById(id).orElse(null);
        return ApiResponse.<Project>builder()
                .code(1000)
                .result(project)
                .build();
    }

    @PostMapping
    public ApiResponse<Project> createProject(@RequestBody ProjectPayload payload) {
        Project project = Project.builder()
                .startupId(payload.getStartupId())
                .projectName(payload.getProjectName())
                .projectDescription(payload.getProjectDescription())
                .build();
        return ApiResponse.<Project>builder()
                .code(1000)
                .message("Project created successfully")
                .result(projectRepository.save(project))
                .build();
    }

    @PutMapping("/{id}")
    public ApiResponse<Project> updateProject(
            @PathVariable UUID id,
            @RequestBody ProjectPayload payload) {
        Project existing = projectRepository.findById(id).orElse(null);
        if (existing == null) {
            return ApiResponse.<Project>builder()
                    .code(1002)
                    .message("Project not found")
                    .build();
        }
        if (payload.getProjectName() != null) {
            existing.setProjectName(payload.getProjectName());
        }
        if (payload.getProjectDescription() != null) {
            existing.setProjectDescription(payload.getProjectDescription());
        }
        if (payload.getStartupId() != null) {
            existing.setStartupId(payload.getStartupId());
        }
        return ApiResponse.<Project>builder()
                .code(1000)
                .message("Project updated successfully")
                .result(projectRepository.save(existing))
                .build();
    }

    @DeleteMapping("/{id}")
    public ApiResponse<String> deleteProject(@PathVariable UUID id) {
        if (projectRepository.existsById(id)) {
            projectRepository.deleteById(id);
        }
        return ApiResponse.<String>builder()
                .code(1000)
                .result("Project deleted successfully")
                .build();
    }

    @Data
    public static class ProjectPayload {
        private UUID startupId;
        private String projectName;
        private String projectDescription;
    }
}
