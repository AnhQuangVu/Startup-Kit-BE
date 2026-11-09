package com.startupkit.platform.repository;

import com.startupkit.platform.entity.Report;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ReportRepository extends JpaRepository<Report, String> {
    List<Report> findByStatusIgnoreCase(String status);
}
