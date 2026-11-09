package com.startupkit.platform.repository;

import com.startupkit.platform.entity.BillingTransaction;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface BillingTransactionRepository extends JpaRepository<BillingTransaction, String> {
}
