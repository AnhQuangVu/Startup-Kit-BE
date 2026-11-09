package com.startupkit.platform.mapper;

import com.startupkit.platform.dto.request.UserCreateRequest;
import com.startupkit.platform.dto.response.UserCreateResponse;
import com.startupkit.platform.entity.User;
import com.startupkit.platform.entity.UserIdentity;
import org.mapstruct.Mapper;
import org.mapstruct.Mapping;

@Mapper(componentModel = "spring")
public interface UserMapper {
    @Mapping(target = "userIdentity" , ignore = true)
    User toUser(UserCreateRequest userCreateRequest);

    UserCreateResponse toUserCreateResponse(UserIdentity userIdentity);
}
