# API Documentation

Base URL: `http://localhost:8080`

---

## 1. Auth APIs — `/v1/auth`

### POST `/v1/auth/login`

**Request Body:**
| Field | Type | Bắt buộc | Mô tả |
|-------|------|-----------|-------|
| email | String | ✅ | Định dạng email hợp lệ |
| password | String | ✅ | Tối thiểu 8 ký tự |

**Response:**
```json
{
  "code": 1000,
  "message": null,
  "result": {
    "accessToken": "string",
    "refreshToken": "string",
    "tokenType": "string"
  }
}
```

---

### POST `/v1/auth/forgot-password`

**Request Body:**
| Field | Type | Bắt buộc | Mô tả |
|-------|------|-----------|-------|
| email | String | ✅ | Email đã đăng ký |

**Response:**
```json
{
  "code": 1000,
  "message": null,
  "result": "Please check your email to reset password."
}
```

---

### POST `/v1/auth/reset-password`

**Request Body:**
| Field | Type | Bắt buộc | Mô tả |
|-------|------|-----------|-------|
| token | String | ✅ | Token nhận từ email |
| password | String | ✅ | Tối thiểu 8 ký tự |
| confirmPassword | String | ✅ | Phải khớp với password |

**Response:**
```json
{
  "code": 1000,
  "message": null,
  "result": "Password has been reset successfully."
}
```

---

## 2. User APIs — `/v1/users`

### POST `/v1/users`

Tạo tài khoản người dùng mới.

**Request Body:**
| Field | Type | Bắt buộc | Mô tả |
|-------|------|-----------|-------|
| fullName | String | ✅ | Họ và tên |
| email | String | ✅ | Định dạng email hợp lệ |
| password | String | ✅ | Tối thiểu 8 ký tự |
| confirmPassword | String | ✅ | Phải khớp với password |
| userType | Enum | ✅ | `STARTUP` / `INVESTOR` / `MENTOR` |

**Response:**
```json
{
  "code": 1000,
  "message": null,
  "result": {
    "id": "uuid",
    "email": "string"
  }
}
```

---

### GET `/v1/users/profile`

Lấy thông tin profile của người dùng đang đăng nhập.

**Headers:**
| Key | Value |
|-----|-------|
| Authorization | `Bearer <accessToken>` |

**Response theo từng loại user:**

#### STARTUP
```json
{
  "code": 1000,
  "result": {
    "userId": "uuid",
    "userName": "string",
    "roles": "STARTUP",
    "location": "string",
    "startupId": "uuid",
    "industry": "string",
    "description": "string",
    "teamSize": 0,
    "averageScore": 0.0,
    "totalRatings": 0,
    "totalCompletedSessions": 0,
    "totalProjects": 0,
    "project": [
      {
        "projectId": "uuid",
        "projectName": "string",
        "projectDescription": "string"
      }
    ]
  }
}
```

#### INVESTOR
```json
{
  "code": 1000,
  "result": {
    "userId": "uuid",
    "fullName": "string",
    "role": "string",
    "location": "string",
    "organizationName": "string",
    "bio": "string",
    "investmentCriteria": ["string"],
    "preferredStages": ["string"],
    "investmentMin": 0.0,
    "investmentMax": 0.0,
    "linkedinUrl": "string",
    "websiteUrl": "string",
    "twitterUrl": "string",
    "totalInvested": 0,
    "portfolio": [
      {
        "startupId": "uuid",
        "startupName": "string",
        "industry": "string"
      }
    ]
  }
}
```

#### MENTOR
```json
{
  "code": 1000,
  "result": {
    "userId": "uuid",
    "fullName": "string",
    "role": "string",
    "location": "string",
    "bio": "string",
    "expertiseTags": ["string"],
    "averageScore": 0.0,
    "totalCompletedSessions": 0,
    "totalRatings": 0,
    "sessionReviews": [
      {
        "startupName": "string",
        "reviewContent": "string",
        "rating": 0.0
      }
    ]
  }
}
```

---

## Tổng quan

| Method | Endpoint | Mô tả | Auth |
|--------|----------|-------|------|
| POST | `/v1/auth/login` | Đăng nhập | Không |
| POST | `/v1/auth/forgot-password` | Quên mật khẩu | Không |
| POST | `/v1/auth/reset-password` | Đặt lại mật khẩu | Không |
| POST | `/v1/users` | Đăng ký tài khoản | Không |
| GET | `/v1/users/profile` | Lấy profile cá nhân | ✅ Bearer Token |
