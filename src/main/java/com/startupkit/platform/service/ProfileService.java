package com.startupkit.platform.service;


import com.startupkit.platform.dto.response.InvestorProfileResponse;
import com.startupkit.platform.dto.response.MentorProfileResponse;
import com.startupkit.platform.dto.response.StartupProfileResponse;
import com.startupkit.platform.entity.*;
import com.startupkit.platform.enums.DealStatus;
import com.startupkit.platform.enums.SessionStatus;
import com.startupkit.platform.exception.AppException;
import com.startupkit.platform.exception.ErrorCode;
import com.startupkit.platform.repository.*;
import lombok.AccessLevel;
import lombok.RequiredArgsConstructor;
import lombok.experimental.FieldDefaults;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.Arrays;
import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;


@Service
@RequiredArgsConstructor
@Slf4j
@FieldDefaults(level = AccessLevel.PRIVATE, makeFinal = true)
public class ProfileService {
    UserRepository userRepo;
    StartupRepository startupRepo;
    InvestorRepository investorRepo;
    MentorRepository mentorRepo;
    AdvisorySessionRepository sessionRepo;
    DealRepository dealRepo;

    public Object getProfile(UUID userId) {
        User user = userRepo.findById(userId)
                .orElseThrow(() -> new AppException(ErrorCode.USER_NOT_EXISTED));

        if (user.getUserType() == null) {
            throw new AppException(ErrorCode.PROFILE_NOT_FOUND);
        }

        return switch (user.getUserType()) {
            case STARTUP  -> getProfileStartup(user);
             case INVESTOR -> getProfileInvestor(user);
             case MENTOR   -> getProfileMentor(user);
            // case ADMIN    -> getProfileAdmin(user);
            default       -> throw new AppException(ErrorCode.PROFILE_NOT_FOUND);
        };
    }

    private StartupProfileResponse getProfileStartup(User user) {
        Startup profile = startupRepo.findByUserId(user.getId())
                .orElseThrow(() -> new AppException(ErrorCode.PROFILE_NOT_FOUND));


        CredibilityScore score = profile.getCredibilityScore();


        List<Project> project = profile.getProjects();

        return StartupProfileResponse.builder()
                // tài khoản
                .userId(user.getId())
                .userName(user.getFullName())
                .roles(user.getRoles())
                .location(user.getLocation())
                // startup
                .startupId(profile.getId())
                .industry(profile.getIndustry())
                .description(profile.getDescription())
                .teamSize(profile.getTeamSize())
                // chỉ số uy tín
                .averageScore(score != null ? score.getAverageScore() : 0)
                .totalRatings(score != null ? score.getTotalRatings() : 0)
                .totalCompletedSessions(score != null ? score.getTotalCompletedSessions() : 0)
                // dự án
                .totalProjects(project != null ? profile.getProjects().size() : 0)
                .project(project != null
                        ? project.stream()
                        .map(p -> StartupProfileResponse.ProjectDto.builder()
                                .projectId(p.getId())
                                .projectName(p.getProjectName())
                                .projectDescription(p.getProjectDescription())
                                .build())
                        .collect(Collectors.toList())
                        : List.of())
                .build();
    }

    private MentorProfileResponse getProfileMentor(User user) {
        Mentor profile = mentorRepo.findByUserId(user.getId())
                .orElseThrow(() -> new AppException(ErrorCode.PROFILE_NOT_FOUND));

        CredibilityScore score = profile.getCredibilityScore();

        List<String> tags = profile.getExpertise() != null
                ? Arrays.stream(profile.getExpertise().split(","))
                .map(String::trim)
                .filter(s -> !s.isEmpty())
                .collect(Collectors.toList())
                : List.of();

        List<MentorProfileResponse.SessionReviewDto> reviews =
                sessionRepo.findByMentorIdAndStatus(profile.getId(), SessionStatus.COMPLETED)
                        .stream()
                        .filter(s -> s.getRating() != null)
                        .map(s -> MentorProfileResponse.SessionReviewDto.builder()
                                .startupName(s.getStartup().getUser().getFullName())
                                .reviewContent(s.getReview())
                                .rating(s.getRating())
                                .build())
                        .collect(Collectors.toList());

        return MentorProfileResponse.builder()
                .userId(user.getId())
                .fullName(user.getFullName())
                .role(user.getRoles() != null ? user.getRoles().getCode() : null)
                .location(user.getLocation())
                .bio(profile.getBio())
                .expertiseTags(tags)
                .averageScore(score != null ? score.getAverageScore() : 0)
                .totalCompletedSessions(score != null ? score.getTotalCompletedSessions() : 0)
                .totalRatings(score != null ? score.getTotalRatings() : 0)
                .sessionReviews(reviews)
                .build();
    }

    private InvestorProfileResponse getProfileInvestor(User user) {
        Investor profile = investorRepo.findByUserId(user.getId())
                .orElseThrow(() -> new AppException(ErrorCode.PROFILE_NOT_FOUND));

        List<String> criteria = parseToList(profile.getInvestmentCriteria());
        List<String> stages   = parseToList(profile.getPreferredStages());

        // Lấy danh mục từ bảng deal
        List<Deal> deals = dealRepo.findByInvestorIdAndStatus(
                profile.getId(), DealStatus.SIGNED);

        List<InvestorProfileResponse.PortfolioItemDto> portfolio = deals.stream()
                .map(d -> InvestorProfileResponse.PortfolioItemDto.builder()
                        .startupId(d.getStartup().getId())
                        .startupName(d.getStartup().getUser().getFullName())
                        .industry(d.getStartup().getIndustry())
                        .build())
                .collect(Collectors.toList());

        return InvestorProfileResponse.builder()
                .userId(user.getId())
                .fullName(user.getFullName())
                .role(user.getRoles() != null ? user.getRoles().getCode() : null)
                .location(user.getLocation())
                .organizationName(profile.getOrganizationName())
                .bio(profile.getBio())
                .investmentCriteria(criteria)
                .preferredStages(stages)
                .investmentMin(profile.getInvestmentMin())
                .investmentMax(profile.getInvestmentMax())
                .linkedinUrl(profile.getLinkedinUrl())
                .websiteUrl(profile.getWebsiteUrl())
                .twitterUrl(profile.getTwitterUrl())
                .totalInvested(portfolio.size())
                .portfolio(portfolio)
                .build();
    }

    // Helper parse "Fintech, Blockchain" → ["Fintech", "Blockchain"]
    private List<String> parseToList(String value) {
        if (value == null || value.isBlank()) return List.of();
        return Arrays.stream(value.split(","))
                .map(String::trim)
                .filter(s -> !s.isEmpty())
                .collect(Collectors.toList());
    }
}
