package com.startupkit.platform.controller;

import com.startupkit.platform.dto.response.ApiResponse;
import com.startupkit.platform.entity.BillingTransaction;
import com.startupkit.platform.repository.BillingTransactionRepository;
import lombok.AccessLevel;
import lombok.RequiredArgsConstructor;
import lombok.experimental.FieldDefaults;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/v1/billing")
@RequiredArgsConstructor
@FieldDefaults(level = AccessLevel.PRIVATE, makeFinal = true)
public class BillingController {

    BillingTransactionRepository transactionRepository;

    @GetMapping("/plans")
    public ApiResponse<List<Map<String, Object>>> getPlans() {
        return ApiResponse.<List<Map<String, Object>>>builder()
                .code(1000)
                .result(List.of(
                        Map.of(
                                "id", "STARTER",
                                "name", "Starter Free",
                                "priceVnd", 0,
                                "priceLabel", "0 ₫ / tháng",
                                "features", List.of("Tạo tối đa 2 dự án", "Xem danh bạ Investor & Mentor", "AI Pitch cơ bản")
                        ),
                        Map.of(
                                "id", "PRO_FOUNDER",
                                "name", "Founder Pro",
                                "priceVnd", 499000,
                                "priceLabel", "499.000 ₫ / tháng",
                                "features", List.of("Không giới hạn dự án & Data Room", "AI Pitch & Credibility chuyên sâu", "Mở khóa Deal Room e-NDA", "Ưu tiên Matching VC")
                        ),
                        Map.of(
                                "id", "INVESTOR_CLUB",
                                "name", "Investor VIP Club",
                                "priceVnd", 999000,
                                "priceLabel", "999.000 ₫ / tháng",
                                "features", List.of("Truy cập sớm Deal Flow độc quyền", "Báo cáo thẩm định Due Diligence", "Mời Co-invest Syndicate")
                        )
                ))
                .build();
    }

    @GetMapping("/transactions")
    public ApiResponse<List<BillingTransaction>> getTransactions() {
        return ApiResponse.<List<BillingTransaction>>builder()
                .code(1000)
                .result(transactionRepository.findAll())
                .build();
    }

    @PostMapping("/checkout-vietqr")
    public ApiResponse<Map<String, Object>> createVietQrCheckout(@RequestBody Map<String, String> payload) {
        String planId = payload.getOrDefault("planId", "PRO_FOUNDER");
        String actor = payload.getOrDefault("actor", "Founder (Startup)");
        String amount = "INVESTOR_CLUB".equalsIgnoreCase(planId) ? "999.000 ₫" : "499.000 ₫";
        int rawAmount = "INVESTOR_CLUB".equalsIgnoreCase(planId) ? 999000 : 499000;
        String txId = "PAY-" + (8825 + transactionRepository.count());

        BillingTransaction tx = BillingTransaction.builder()
                .id(txId)
                .actor(actor)
                .type("Subscription (" + planId + ")")
                .amount(amount)
                .gateway("PayOS VietQR")
                .status("Completed")
                .createdAt(LocalDate.now().toString())
                .build();
        transactionRepository.save(tx);

        String qrUrl = "https://img.vietqr.io/image/MB-0388999999-compact2.png?amount=" + rawAmount
                + "&addInfo=" + txId + "&accountName=STARTUPKIT%20PLATFORM";

        return ApiResponse.<Map<String, Object>>builder()
                .code(1000)
                .message("VietQR payment processed")
                .result(Map.of(
                        "transaction", tx,
                        "qrUrl", qrUrl
                ))
                .build();
    }
}
