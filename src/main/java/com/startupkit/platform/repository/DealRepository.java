package com.startupkit.platform.repository;

import com.startupkit.platform.entity.Deal;
import com.startupkit.platform.enums.DealStatus;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.UUID;

public interface DealRepository extends JpaRepository<Deal, UUID> {

    // Lấy tất cả deal của 1 investor
    List<Deal> findByInvestorId(UUID investorId);

    // Lấy tất cả deal của 1 startup
    List<Deal> findByStartupId(UUID startupId);

    // Lấy deal đã ký của investor
    List<Deal> findByInvestorIdAndStatus(UUID investorId, DealStatus status);

    // Đếm số startup đã đầu tư
    long countByInvestorIdAndStatus(UUID investorId, DealStatus status);
}
