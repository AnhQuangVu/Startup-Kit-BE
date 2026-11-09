package com.startupkit.platform.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.*;
import lombok.experimental.FieldDefaults;

@Entity
@Table(name = "billing_transaction")
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
@FieldDefaults(level = AccessLevel.PRIVATE)
public class BillingTransaction {

    @Id
    @Column(name = "id", length = 50)
    String id;

    @Column(name = "actor", nullable = false)
    String actor;

    @Column(name = "tx_type", nullable = false)
    String type;

    @Column(name = "amount", nullable = false)
    String amount;

    @Column(name = "gateway", nullable = false)
    String gateway;

    @Column(name = "status", nullable = false)
    String status;

    @Column(name = "created_at", nullable = false)
    String createdAt;
}
