package com.startupkit.platform.repository;

import com.startupkit.platform.entity.Role;
import org.springframework.data.jpa.repository.JpaRepository;

public interface RoleRepository extends JpaRepository<Role, String> {
}