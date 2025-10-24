# Tài liệu API - Startup Kit

Chào mừng đến với tài liệu API của Startup Kit. API này tuân thủ theo tiêu chuẩn RESTful và sử dụng WebSocket cho các tính năng thời gian thực.

**Base URL**: `http://0.0.0.0:8000`

Tất cả các endpoint RESTful yêu cầu xác thực đều phải có header `Authorization: Bearer <YOUR_ACCESS_TOKEN>`. WebSocket yêu cầu token qua query parameter.

---

## 1. Authentication

Các endpoint dùng để đăng ký và đăng nhập.

### **`POST /auth/register`**

Tạo một tài khoản người dùng mới.

**Request Body:**
```json
{
  "full_name": "Nguyen Van A",
  "email": "a.nguyen@example.com",
  "password": "strongpassword123",
  "password_confirm": "strongpassword123",
  "role": "founder"
}
```
* `role` có thể là một trong các giá trị: `founder`, `investor`, `mentor`, `admin`.

**Success Response (201 Created):**
```json
{
  "id": 1,
  "full_name": "Nguyen Van A",
  "email": "a.nguyen@example.com",
  "role": "founder",
  "is_active": true,
  "created_at": "2025-10-04T20:36:00.000Z",
  "profile": {
    "user_id": 1,
    "avatar_url": null,
    "bio": null,
    "website_url": null,
    "location": null
  }
}
```

**Error Responses:**
- `400 Bad Request`: Email đã tồn tại hoặc mật khẩu không khớp.

---

### **`POST /auth/token`**

Đăng nhập để nhận Access Token (JWT). Request body phải ở dạng `form-data`.

**Request Form Data:**
- `username`: Email của người dùng.
- `password`: Mật khẩu của người dùng.

**Success Response (200 OK):**

```json
{
  "access_token": "ey...",
  "token_type": "bearer"
}
```

**Error Responses:**
- `401 Unauthorized`: Sai email hoặc mật khẩu.
- `400 Bad Request`: Tài khoản người dùng đã bị vô hiệu hóa.

---

## 2. Users

Các endpoint để quản lý thông tin người dùng.

### **`GET /users/me`**

Lấy thông tin chi tiết của người dùng đang đăng nhập.

**Authentication:** Required (Bearer Token)

**Success Response (200 OK):**
```json
{
  "id": 1,
  "full_name": "Nguyen Van A",
  "email": "a.nguyen@example.com",
  "role": "founder",
  "is_active": true,
  "created_at": "2025-10-04T20:36:00.000Z",
  "profile": {
    "user_id": 1,
    "avatar_url": "https://example.com/avatar.jpg",
    "bio": "Founder of Startup X.",
    "website_url": "https://startupx.com",
    "location": "Hanoi, Vietnam"
  }
}
```

---

### **`PATCH /users/me`**

Cập nhật thông tin cá nhân của người dùng đang đăng nhập. Chỉ cần gửi những trường bạn muốn thay đổi.

**Authentication:** Required (Bearer Token)

**Request Body:**
```json
{
  "full_name": "Nguyen Van A Updated",
  "bio": "Founder of Startup X. We are changing the world!",
  "location": "Ho Chi Minh City, Vietnam"
}
```

**Success Response (200 OK):**
*   Trả về object người dùng đã được cập nhật, tương tự như `GET /users/me`.

---

### **`PUT /users/me/password`**

Thay đổi mật khẩu của người dùng đang đăng nhập.

**Authentication:** Required (Bearer Token)

**Request Body:**
```json
{
  "current_password": "strongpassword123",
  "new_password": "newstrongerpassword456",
  "new_password_confirm": "newstrongerpassword456"
}
```

**Success Response (200 OK):**
```json
{
  "message": "Password updated successfully"
}
```

**Error Responses:**
- `400 Bad Request`: Mật khẩu mới không khớp hoặc mật khẩu hiện tại không đúng.

---

### **`DELETE /users/me`**

Vô hiệu hóa (xóa mềm) tài khoản của người dùng đang đăng nhập.

**Authentication:** Required (Bearer Token)

**Success Response (200 OK):**
```json
{
  "message": "Account deactivated successfully"
}
```

---

## 3. Projects (REST API)

Các endpoint để tạo và quản lý dự án khởi nghiệp.

### **`POST /projects`**

Tạo một dự án khởi nghiệp mới. Endpoint này sẽ tự động tạo ra các section mặc định cho dự án (Pitch Deck, BMC,...).

**Authentication:** Required (Bearer Token)
**Permissions:** Chỉ người dùng có vai trò `founder` mới có thể tạo.

**Request Body:**
```json
{
  "name": "Dự án AI Phân tích Thị trường",
  "tagline": "Sử dụng AI để đưa ra quyết định kinh doanh thông minh.",
  "stage": "idea"
}
```
* `stage` có thể là một trong các giá trị: `idea`, `prototype`, `seed`, `series_a`.

**Success Response (201 Created):**
```json
{
    "id": 1,
    "founder_id": 1,
    "name": "Dự án AI Phân tích Thị trường",
    "tagline": "Sử dụng AI để đưa ra quyết định kinh doanh thông minh.",
    "stage": "idea",
    "created_at": "2025-10-05T10:00:00Z",
    "updated_at": "2025-10-05T10:00:00Z",
    "sections": [
        {
            "id": 1,
            "type": "PITCH_DECK",
            "title": "Pitch Deck",
            "content": {},
            "file_url": null,
            "updated_at": "2025-10-05T10:00:00Z"
        },
        {
            "id": 2,
            "type": "BUSINESS_MODEL_CANVAS",
            "title": "Business Model Canvas (BMC)",
            "content": {},
            "file_url": null,
            "updated_at": "2025-10-05T10:00:00Z"
        }
    ]
}
```

**Error Responses:**
- `403 Forbidden`: Người dùng không phải là `founder`.

---

### **`GET /projects`**

Lấy danh sách tất cả các dự án của người dùng đã đăng nhập.

**Authentication:** Required (Bearer Token)

**Success Response (200 OK):**
*   Trả về một mảng các đối tượng dự án, có cấu trúc tương tự response của `POST /projects`.

---

### **`GET /projects/{project_id}`**

Lấy thông tin chi tiết của một dự án cụ thể.

**Authentication:** Required (Bearer Token)

**Path Parameter:**
- `project_id` (integer): ID của dự án cần xem.

**Success Response (200 OK):**
*   Trả về một đối tượng dự án duy nhất.

**Error Responses:**
- `404 Not Found`: Không tìm thấy dự án hoặc người dùng không có quyền truy cập.

---

## 4. WebSocket API (Auto-Save)

Hệ thống sử dụng WebSocket để cung cấp chức năng tự động lưu nội dung dự án theo thời gian thực.

### **`WS /projects/ws/{section_id}`**

Thiết lập một kết nối WebSocket để chỉnh sửa một phần (section) của dự án.

**Giao thức**: `ws://` (hoặc `wss://` trong môi trường production)

**Endpoint URL Example:**
`ws://0.0.0.0:8000/projects/ws/1?token=<YOUR_ACCESS_TOKEN>`

**Authentication:**
-   Yêu cầu xác thực.
-   Access Token (JWT) phải được truyền qua một **query parameter** có tên là `token`.

**Luồng hoạt động:**
1.  Client khởi tạo kết nối đến endpoint với `section_id` và token hợp lệ.
2.  Server xác thực token và kiểm tra xem người dùng có phải là chủ sở hữu của `section_id` đó không. Nếu không, kết nối sẽ bị từ chối.
3.  Sau khi kết nối thành công, client có thể bắt đầu gửi các message cập nhật.

---

#### **Messages từ Client đến Server**

Client gửi một đối tượng JSON mỗi khi có thay đổi nội dung.

**Định dạng Message:**
```json
{
  "title": "Pitch Deck phiên bản mới",
  "content": {
    "slide1": "Nội dung slide 1 đã được cập nhật.",
    "slide2": "Nội dung slide 2."
  }
}
```
*   `title`: (Tùy chọn) Chuỗi string, tiêu đề mới của section.
*   `content`: (Tùy chọn) Một đối tượng JSON, chứa cấu trúc nội dung chi tiết của section.

---

#### **Messages từ Server đến Client**

**Xác nhận lưu thành công:**
Sau khi nhận và lưu thành công dữ liệu, server sẽ gửi lại:
```json
{
  "status": "saved",
  "section_id": 1
}
```

**Lỗi định dạng dữ liệu:**
Nếu client gửi dữ liệu không đúng định dạng:
```json
{
  "status": "error",
  "message": "Invalid data format"
}
```

---

### **`POST /projects/{project_id}/members`**

Thêm thành viên vào dự án.

**Authentication:** Required (Bearer Token)

**Path Parameter:**
- `project_id` (integer): ID của dự án

**Request Body:**
```json
{
  "user_id": 5,
  "name": "Nguyen Van B",
  "avatar_url": "https://example.com/avatar.jpg",
  "role_in_project": "CTO",
  "is_founder": false
}
```

**Success Response (201 Created):**
```json
{
  "id": 1,
  "project_id": 1,
  "user_id": 5,
  "name": "Nguyen Van B",
  "avatar_url": "https://example.com/avatar.jpg",
  "role_in_project": "CTO",
  "is_founder": false,
  "joined_at": "2025-10-05T10:30:00Z"
}
```

**Error Responses:**
- `404 Not Found`: Không tìm thấy dự án
- `500 Internal Server Error`: Lỗi server

---

### **`GET /projects/{project_id}/members`**

Lấy danh sách thành viên của dự án.

**Authentication:** Required (Bearer Token)

**Path Parameter:**
- `project_id` (integer): ID của dự án

**Success Response (200 OK):**
*   Trả về mảng các đối tượng member, cấu trúc tương tự response của `POST /projects/{project_id}/members`.

---

### **`POST /projects/{project_id}/posts`**

Tạo bài đăng mới cho dự án.

**Authentication:** Required (Bearer Token)

**Path Parameter:**
- `project_id` (integer): ID của dự án

**Request Body:**
```json
{
  "title": "Chúng tôi vừa ra mắt phiên bản Beta",
  "body": "Sau 6 tháng phát triển, chúng tôi vui mừng thông báo...",
  "media": [
    {
      "url": "https://example.com/image1.jpg",
      "public_id": "img_123",
      "media_type": "image"
    }
  ],
  "visibility": "public"
}
```
* `visibility` có thể là: `public`, `private`, `followers_only`

**Success Response (201 Created):**
```json
{
  "id": 1,
  "project_id": 1,
  "author_id": 1,
  "title": "Chúng tôi vừa ra mắt phiên bản Beta",
  "body": "Sau 6 tháng phát triển, chúng tôi vui mừng thông báo...",
  "visibility": "public",
  "media": [
    {
      "url": "https://example.com/image1.jpg",
      "public_id": "img_123",
      "media_type": "image"
    }
  ],
  "created_at": "2025-10-05T11:00:00Z",
  "updated_at": "2025-10-05T11:00:00Z"
}
```

**Error Responses:**
- `404 Not Found`: Không tìm thấy dự án
- `500 Internal Server Error`: Lỗi server

---

### **`GET /projects/{project_id}/posts`**

Lấy danh sách bài đăng của dự án.

**Authentication:** Required (Bearer Token)

**Path Parameter:**
- `project_id` (integer): ID của dự án

**Query Parameters:**
- `limit` (integer, optional): Số lượng bài đăng tối đa (mặc định: 50, min: 1, max: 200)

**Success Response (200 OK):**
*   Trả về mảng các đối tượng post, cấu trúc tương tự response của `POST /projects/{project_id}/posts`.

---

### **`GET /projects/posts/{post_id}`**

Lấy thông tin chi tiết của một bài đăng.

**Authentication:** Required (Bearer Token)

**Path Parameter:**
- `post_id` (integer): ID của bài đăng

**Success Response (200 OK):**
*   Trả về một đối tượng post duy nhất.

**Error Responses:**
- `404 Not Found`: Không tìm thấy bài đăng

---

### **`POST /projects/posts/{post_id}/comments`**

Thêm comment vào bài đăng.

**Authentication:** Required (Bearer Token)

**Path Parameter:**
- `post_id` (integer): ID của bài đăng

**Request Body:**
```json
{
  "body": "Chúc mừng team! Sản phẩm trông rất tuyệt vời!",
  "parent_comment_id": null
}
```
* `parent_comment_id`: ID của comment cha (để reply comment), để `null` nếu là comment gốc

**Success Response (201 Created):**
```json
{
  "id": 1,
  "post_id": 1,
  "author_id": 2,
  "body": "Chúc mừng team! Sản phẩm trông rất tuyệt vời!",
  "parent_comment_id": null,
  "created_at": "2025-10-05T11:15:00Z"
}
```

**Error Responses:**
- `404 Not Found`: Không tìm thấy bài đăng
- `500 Internal Server Error`: Lỗi server

---

### **`POST /projects/posts/{post_id}/like`**

Like một bài đăng.

**Authentication:** Required (Bearer Token)

**Path Parameter:**
- `post_id` (integer): ID của bài đăng

**Request Body:** Không cần

**Success Response (200 OK):**
```json
{
  "id": 1,
  "post_id": 1,
  "user_id": 2,
  "created_at": "2025-10-05T11:20:00Z"
}
```

**Error Responses:**
- `404 Not Found`: Không tìm thấy bài đăng
- `500 Internal Server Error`: Lỗi server (có thể đã like trước đó)

---

### **`POST /projects/{project_id}/follow`**

Follow một dự án để nhận cập nhật.

**Authentication:** Required (Bearer Token)

**Path Parameter:**
- `project_id` (integer): ID của dự án

**Request Body:** Không cần

**Success Response (201 Created):**
```json
{
  "id": 1,
  "project_id": 1,
  "user_id": 2,
  "created_at": "2025-10-05T11:25:00Z"
}
```

**Error Responses:**
- `404 Not Found`: Không tìm thấy dự án
- `500 Internal Server Error`: Lỗi server (có thể đã follow trước đó)

---

### **`DELETE /projects/{project_id}/follow`**

Unfollow một dự án.

**Authentication:** Required (Bearer Token)

**Path Parameter:**
- `project_id` (integer): ID của dự án

**Success Response (204 No Content):**
*   Không có response body

**Error Responses:**
- `404 Not Found`: Không tìm thấy dự án hoặc chưa follow

---

### **`GET /projects/{project_id}/followers`**

Lấy danh sách người follow dự án.

**Authentication:** Required (Bearer Token)

**Path Parameter:**
- `project_id` (integer): ID của dự án

**Success Response (200 OK):**
```json
[
  {
    "id": 1,
    "project_id": 1,
    "user_id": 2,
    "created_at": "2025-10-05T11:25:00Z"
  },
  {
    "id": 2,
    "project_id": 1,
    "user_id": 3,
    "created_at": "2025-10-05T11:30:00Z"
  }
]
```

---

## 5. AI Assistant

Các endpoint để sử dụng AI hỗ trợ tạo và cải thiện nội dung dự án.

### **`POST /ai/generate-project`**

Tạo toàn bộ thông tin dự án từ mô tả ngắn sử dụng AI.

**Authentication:** Required (Bearer Token)

**Request Body:**
```json
{
  "description": "Tôi muốn tạo một ứng dụng di động giúp người dùng tìm kiếm và đặt chỗ tại các quán cà phê địa phương. Ứng dụng sẽ có tính năng đánh giá, chia sẻ trải nghiệm và chương trình khách hàng thân thiết."
}
```

**Success Response (200 OK):**
```json
{
  "name": "CoffeeFinder",
  "tagline": "Khám phá và đặt chỗ tại các quán cà phê yêu thích",
  "industry": "F&B Technology",
  "pain_point": "Khó khăn trong việc tìm kiếm quán cà phê phù hợp và đặt chỗ trước",
  "solution": "Ứng dụng di động tích hợp tìm kiếm, đặt chỗ và đánh giá",
  "product": "Ứng dụng mobile iOS/Android với tính năng tìm kiếm, đặt chỗ, đánh giá và loyalty program",
  "customer_segment": "Dân văn phòng, sinh viên, freelancer từ 18-40 tuổi sống tại thành phố lớn",
  "market_size": "Thị trường F&B Việt Nam trị giá 20 tỷ USD, phân khúc cà phê chiếm 15%",
  "business_model": "Commission-based model và subscription",
  "revenue_method": "Hoa hồng từ đặt chỗ (10-15%), phí subscription cho quán (299k/tháng)",
  "distribution_channel": "App Store, Google Play, social media marketing",
  "partners": "Các chuỗi quán cà phê, cửa hàng độc lập, payment gateway",
  "cost_estimate": "150,000 USD cho năm đầu",
  "member_count": 5,
  "member_skills": "Mobile developer, Backend developer, UI/UX designer, Marketing, Business development"
}
```

**Error Responses:**
- `500 Internal Server Error`: Lỗi khi tạo dự án

---

### **`POST /ai/suggest`**

Lấy gợi ý AI cho một trường cụ thể khi đang nhập liệu.

**Authentication:** Required (Bearer Token)

**Request Body:**
```json
{
  "field_name": "pain_point",
  "current_text": "Người dùng khó khăn trong việc",
  "project_id": 1,
  "project_context": {
    "name": "CoffeeFinder",
    "industry": "F&B Technology"
  }
}
```

**Success Response (200 OK):**
```json
{
  "suggestions": [
    {
      "suggestion": "Người dùng khó khăn trong việc tìm kiếm quán cà phê phù hợp với sở thích và nhu cầu của mình",
      "confidence": 0.92
    },
    {
      "suggestion": "Người dùng khó khăn trong việc đặt chỗ trước tại các quán cà phê đông khách",
      "confidence": 0.88
    },
    {
      "suggestion": "Người dùng khó khăn trong việc tìm thông tin đánh giá chính xác về chất lượng quán",
      "confidence": 0.85
    }
  ]
}
```

**Error Responses:**
- `500 Internal Server Error`: Lỗi khi tạo gợi ý

---

### **`POST /ai/autocomplete`**

Tự động hoàn thiện văn bản đang nhập (giống autocomplete trong IDE).

**Authentication:** Required (Bearer Token)

**Request Body:**
```json
{
  "field_name": "solution",
  "current_text": "Chúng tôi sẽ phát triển một ứng dụng",
  "project_context": {
    "name": "CoffeeFinder",
    "pain_point": "Khó khăn trong việc tìm kiếm và đặt chỗ quán cà phê"
  }
}
```

**Success Response (200 OK):**
```json
{
  "completion": " di động kết nối người dùng với các quán cà phê địa phương, cho phép tìm kiếm theo vị trí, đánh giá và đặt chỗ trực tiếp.",
  "full_text": "Chúng tôi sẽ phát triển một ứng dụng di động kết nối người dùng với các quán cà phê địa phương, cho phép tìm kiếm theo vị trí, đánh giá và đặt chỗ trực tiếp."
}
```

**Error Responses:**
- `500 Internal Server Error`: Lỗi khi autocomplete

---

### **`POST /ai/generate-bmc/{project_id}`**

Tạo Business Model Canvas (BMC) cho dự án dựa trên thông tin hiện có.

**Authentication:** Required (Bearer Token)

**Path Parameter:**
- `project_id` (integer): ID của dự án

**Request Body:** Không cần

**Success Response (200 OK):**
```json
{
  "bmc": [
    {
      "block": "Customer Segments",
      "value": "Dân văn phòng 25-40 tuổi, sinh viên, freelancer có nhu cầu làm việc tại quán cà phê"
    },
    {
      "block": "Value Propositions",
      "value": "Tìm kiếm dễ dàng, đặt chỗ nhanh chóng, đánh giá chân thực, chương trình tích điểm"
    },
    {
      "block": "Channels",
      "value": "App Store, Google Play, Social Media (Facebook, Instagram), KOLs, partnerships với quán cà phê"
    },
    {
      "block": "Customer Relationships",
      "value": "Self-service app, chatbot hỗ trợ 24/7, email marketing, push notifications"
    },
    {
      "block": "Revenue Streams",
      "value": "Hoa hồng đặt chỗ 10-15%, subscription fee từ quán (299k/tháng), quảng cáo"
    },
    {
      "block": "Key Resources",
      "value": "Mobile app platform, database quán cà phê, đội ngũ tech, quan hệ đối tác"
    },
    {
      "block": "Key Activities",
      "value": "Phát triển app, onboard quán cà phê mới, marketing, chăm sóc khách hàng"
    },
    {
      "block": "Key Partners",
      "value": "Quán cà phê, payment gateways (Momo, VNPay), dịch vụ delivery, influencers"
    },
    {
      "block": "Cost Structure",
      "value": "Chi phí phát triển app ($80k), server & hosting ($1k/tháng), marketing ($3k/tháng), lương team ($5k/tháng)"
    }
  ]
}
```

**Error Responses:**
- `404 Not Found`: Không tìm thấy dự án
- `500 Internal Server Error`: Lỗi khi tạo BMC

---

### **`POST /ai/generate-financial/{project_id}`**

Tạo kế hoạch tài chính chi tiết cho dự án.

**Authentication:** Required (Bearer Token)

**Path Parameter:**
- `project_id` (integer): ID của dự án

**Request Body:** Không cần

**Success Response (200 OK):**
```json
{
  "startup_costs": {
    "initial_investment": "$150,000",
    "breakdown": [
      {"item": "App Development (iOS & Android)", "amount": "$80,000"},
      {"item": "UI/UX Design", "amount": "$15,000"},
      {"item": "Server & Infrastructure Setup", "amount": "$10,000"},
      {"item": "Legal & Company Registration", "amount": "$5,000"},
      {"item": "Initial Marketing & Branding", "amount": "$20,000"},
      {"item": "Office Equipment & Setup", "amount": "$10,000"},
      {"item": "Reserve Fund", "amount": "$10,000"}
    ]
  },
  "operating_costs": {
    "monthly": "$10,000",
    "breakdown": [
      {"item": "Team Salaries (5 members)", "amount": "$5,000"},
      {"item": "Server & Cloud Services", "amount": "$1,000"},
      {"item": "Marketing & Advertising", "amount": "$2,500"},
      {"item": "Office Rent & Utilities", "amount": "$800"},
      {"item": "Payment Gateway Fees", "amount": "$300"},
      {"item": "Miscellaneous", "amount": "$400"}
    ]
  },
  "revenue_projection": {
    "year1": "$180,000",
    "year2": "$520,000",
    "year3": "$1,200,000",
    "assumptions": "Năm 1: 200 quán partner, 50,000 users. Năm 2: 500 quán, 150,000 users. Năm 3: 1,000 quán, 400,000 users. Commission rate 12%, subscription 299k/tháng"
  },
  "funding_needs": {
    "total": "$250,000",
    "sources": [
      {"source": "Angel Investors", "amount": "$150,000", "percentage": "60%"},
      {"source": "Founders", "amount": "$50,000", "percentage": "20%"},
      {"source": "Government Grant", "amount": "$30,000", "percentage": "12%"},
      {"source": "Pre-seed Fund", "amount": "$20,000", "percentage": "8%"}
    ]
  },
  "breakeven_analysis": "Dự kiến đạt break-even sau 18 tháng với 300 quán partner và 80,000 active users"
}
```

**Error Responses:**
- `404 Not Found`: Không tìm thấy dự án
- `500 Internal Server Error`: Lỗi khi tạo kế hoạch tài chính

---

### **`POST /ai/generate-market-research/{project_id}`**

Tạo báo cáo nghiên cứu thị trường cho dự án.

**Authentication:** Required (Bearer Token)

**Path Parameter:**
- `project_id` (integer): ID của dự án

**Request Body:** Không cần

**Success Response (200 OK):**
```json
{
  "market_overview": "Thị trường F&B Technology tại Việt Nam đang trong giai đoạn tăng trưởng mạnh mẽ với CAGR 25% từ 2023-2027. Đặc biệt, phân khúc cà phê chiếm 15% tổng giá trị thị trường F&B trị giá 20 tỷ USD.",
  "market_size": "$3 tỷ USD (phân khúc cà phê), với 150,000+ quán cà phê trên toàn quốc",
  "market_trends": [
    "Tăng trưởng mạnh mẽ của thương mại điện tử và app đặt đồ ăn/uống",
    "Xu hướng làm việc từ xa và flexible workspace tại các quán cà phê",
    "Người tiêu dùng trẻ ưa chuộng trải nghiệm và sự tiện lợi",
    "Thanh toán không tiếp xúc và digital loyalty programs ngày càng phổ biến"
  ],
  "target_audience": {
    "demographics": "18-40 tuổi, thu nhập trung bình-cao, sống tại TP.HCM, Hà Nội và các thành phố lớn",
    "behaviors": "Sử dụng smartphone thường xuyên, thích khám phá địa điểm mới, đọc review trước khi quyết định",
    "pain_points": "Khó tìm quán phù hợp, mất thời gian đặt chỗ, thông tin đánh giá không đầy đủ"
  },
  "competitors": [
    {
      "name": "Foody/ShopeeFood",
      "strengths": "Brand lớn, user base rộng, đa dạng dịch vụ",
      "weaknesses": "Focus vào delivery, không chuyên về đặt chỗ tại quán"
    },
    {
      "name": "TableNow",
      "strengths": "Chuyên về booking, giao diện đẹp",
      "weaknesses": "Ít quán cà phê, focus vào nhà hàng cao cấp"
    },
    {
      "name": "Google Maps/Facebook",
      "strengths": "Phổ biến, nhiều thông tin",
      "weaknesses": "Không có tính năng đặt chỗ trực tiếp, không có loyalty program"
    }
  ],
  "opportunities": [
    "Thị trường chưa có leader rõ ràng trong phân khúc coffee booking",
    "Nhu cầu làm việc tại quán cà phê tăng cao hậu Covid",
    "Các quán độc lập muốn digitalize nhưng chưa có giải pháp phù hợp",
    "Tiềm năng mở rộng sang các dịch vụ khác (coworking, event)"
  ],
  "threats": [
    "Các ứng dụng lớn như Grab, Shopee có thể copy model",
    "Chi phí marketing cao để cạnh tranh với các brand lớn",
    "Thay đổi hành vi người dùng sau pandemic",
    "Khó khăn trong việc onboard quán cà phê nhỏ"
  ],
  "competitive_advantage": "Focus 100% vào phân khúc cà phê, hiểu sâu nhu cầu của cả user lẫn quán, loyalty program hấp dẫn, UI/UX được tối ưu cho trải nghiệm tìm kiếm và đặt chỗ"
}
```

**Error Responses:**
- `404 Not Found`: Không tìm thấy dự án
- `500 Internal Server Error`: Lỗi khi tạo nghiên cứu thị trường

---

### **`POST /ai/generate-gtm/{project_id}`**

Tạo chiến lược Go-to-Market (GTM) cho dự án.

**Authentication:** Required (Bearer Token)

**Path Parameter:**
- `project_id` (integer): ID của dự án

**Request Body:** Không cần

**Success Response (200 OK):**
```json
{
  "target_market": "TP.HCM và Hà Nội, focus vào quận trung tâm có mật độ quán cà phê cao (Q1, Q3, Ba Đình, Cầu Giấy)",
  "positioning": "The #1 coffee discovery & booking platform for urban professionals and students",
  "launch_phases": [
    {
      "phase": "Pre-Launch (Tháng 1-2)",
      "timeline": "2 tháng",
      "objectives": [
        "Onboard 50 quán partner tại TP.HCM",
        "Build waitlist 5,000 users",
        "Hoàn thiện MVP"
      ],
      "activities": [
        "Direct sales tới các quán cà phê",
        "Landing page + social media teaser",
        "Beta testing với 100 early users",
        "PR trên tech media"
      ]
    },
    {
      "phase": "Soft Launch (Tháng 3-4)",
      "timeline": "2 tháng",
      "objectives": [
        "Reach 10,000 downloads",
        "100 quán partner",
        "1,000 successful bookings"
      ],
      "activities": [
        "Launch App Store & Google Play",
        "Influencer marketing campaign",
        "In-store promotion tại quán partner",
        "Referral program"
      ]
    },
    {
      "phase": "Growth Phase (Tháng 5-12)",
      "timeline": "8 tháng",
      "objectives": [
        "Reach 100,000 users",
        "500 quán partner",
        "Expand to Hà Nội"
      ],
      "activities": [
        "Performance marketing (Facebook, Google Ads)",
        "Partnership với coworking spaces",
        "Launch loyalty program",
        "PR & media coverage"
      ]
    }
  ],
  "marketing_channels": [
    {
      "channel": "Social Media Marketing (Facebook, Instagram, TikTok)",
      "budget": "$2,000/month",
      "expected_roi": "CAC $2, LTV $50"
    },
    {
      "channel": "Influencer Marketing (KOLs, Micro-influencers)",
      "budget": "$1,500/month",
      "expected_roi": "10,000 reach per campaign"
    },
    {
      "channel": "Performance Ads (Google, Facebook)",
      "budget": "$2,500/month",
      "expected_roi": "CAC $3, conversion rate 8%"
    },
    {
      "channel": "PR & Content Marketing",
      "budget": "$1,000/month",
      "expected_roi": "Brand awareness, SEO boost"
    },
    {
      "channel": "Partnership & Referral Program",
      "budget": "$500/month",
      "expected_roi": "Viral coefficient 1.5"
    }
  ],
  "sales_strategy": "B2B2C model: (1) Direct sales team onboard quán cà phê với zero commission trong 3 tháng đầu, (2) Self-service portal cho quán đăng ký, (3) Focus vào các chuỗi và quán có >1000 followers trên social media",
  "customer_acquisition": {
    "strategy": "Viral loop: User gets 20,000 VND voucher cho mỗi friend referral, friend được 30,000 VND welcome bonus. In-app gamification với badges và exclusive perks.",
    "cost_per_acquisition": "$2.50",
    "conversion_rate": "8% (from app install to first booking)"
  },
  "milestones": [
    {"milestone": "Launch MVP tại TP.HCM", "target_date": "Tháng 3/2025"},
    {"milestone": "10,000 users", "target_date": "Tháng 5/2025"},
    {"milestone": "Break-even monthly", "target_date": "Tháng 9/2025"},
    {"milestone": "Launch Hà Nội market", "target_date": "Tháng 10/2025"},
    {"milestone": "100,000 users", "target_date": "Tháng 12/2025"},
    {"milestone": "Series A fundraising", "target_date": "Q1 2026"}
  ]
}
```

**Error Responses:**
- `404 Not Found`: Không tìm thấy dự án
- `500 Internal Server Error`: Lỗi khi tạo chiến lược GTM

---

### **`POST /ai/enhance-text`**

Cải thiện văn bản để chuyên nghiệp và rõ ràng hơn.

**Authentication:** Required (Bearer Token)

**Request Body:**
```json
{
  "text": "App giúp tìm quán cafe và đặt chỗ, có thể xem review",
  "context": "Đây là phần mô tả solution cho pitch deck"
}
```

**Success Response (200 OK):**
```json
{
  "original": "App giúp tìm quán cafe và đặt chỗ, có thể xem review",
  "enhanced": "Nền tảng di động tích hợp công nghệ AI giúp người dùng khám phá các quán cà phê phù hợp với sở thích cá nhân, đặt chỗ trước trực tiếp trên ứng dụng, và tiếp cận hệ thống đánh giá chân thực từ cộng đồng người dùng.",
  "improvements": [
    "Thêm chi tiết về công nghệ (AI)",
    "Làm rõ giá trị cá nhân hóa",
    "Sử dụng ngôn ngữ chuyên nghiệp hơn",
    "Nhấn mạnh tính năng đặt chỗ trực tiếp",
    "Highlight tính xác thực của review"
  ]
}
```

**Error Responses:**
- `500 Internal Server Error`: Lỗi khi cải thiện văn bản

---

## 6. AI RAG (Retrieval-Augmented Generation)

Các endpoint cho việc upload tài liệu và chat với AI sử dụng RAG.

### **`POST /ai/documents/upload`**

Upload tài liệu để AI có thể sử dụng làm nguồn tham khảo.

**Authentication:** Required (Bearer Token)

**Request:** `multipart/form-data`

**Form Fields:**
- `file` (file, required): File tài liệu (PDF, TXT, DOCX, DOC)
- `project_id` (integer, optional): ID của dự án liên quan

**Success Response (200 OK):**
```json
{
  "id": 1,
  "filename": "market_research_2025.pdf",
  "file_type": "pdf",
  "file_size": 2458624,
  "is_processed": true,
  "chunks_created": 45,
  "message": "Upload và xử lý thành công! Tạo 45 chunks."
}
```

**Error Responses:**
- `400 Bad Request`: Định dạng file không hỗ trợ
- `404 Not Found`: Không tìm thấy dự án (nếu có project_id)
- `500 Internal Server Error`: Lỗi upload hoặc xử lý tài liệu

**Supported File Types:**
- PDF (.pdf)
- Text (.txt)
- Word (.docx, .doc)

**Notes:**
- Tài liệu sẽ được tự động phân tách thành các chunks và lưu vào vector database
- AI sẽ sử dụng nội dung này khi trả lời câu hỏi thông qua RAG

---

### **`GET /ai/documents`**

Lấy danh sách tài liệu đã upload.

**Authentication:** Required (Bearer Token)

**Query Parameters:**
- `project_id` (integer, optional): Lọc theo dự án cụ thể

**Success Response (200 OK):**
```json
[
  {
    "id": 1,
    "filename": "market_research_2025.pdf",
    "file_type": "pdf",
    "file_size": 2458624,
    "uploaded_by": 1,
    "project_id": 1,
    "content_preview": "Báo cáo nghiên cứu thị trường F&B Technology Việt Nam năm 2025...",
    "is_processed": true,
    "created_at": "2025-10-05T12:00:00Z"
  },
  {
    "id": 2,
    "filename": "competitor_analysis.docx",
    "file_type": "docx",
    "file_size": 156824,
    "uploaded_by": 1,
    "project_id": 1,
    "content_preview": "Phân tích đối thủ cạnh tranh trong lĩnh vực booking...",
    "is_processed": true,
    "created_at": "2025-10-05T13:00:00Z"
  }
]
```

---

### **`DELETE /ai/documents/{document_id}`**

Xóa tài liệu và các embeddings liên quan.

**Authentication:** Required (Bearer Token)

**Path Parameter:**
- `document_id` (integer): ID của tài liệu

**Success Response (200 OK):**
```json
{
  "message": "Xóa document thành công"
}
```

**Error Responses:**
- `404 Not Found`: Không tìm thấy tài liệu
- `500 Internal Server Error`: Lỗi khi xóa

---

### **`POST /ai/chat`**

Chat với AI sử dụng RAG - AI sẽ tham khảo tài liệu đã upload và có thể search Google.

**Authentication:** Required (Bearer Token)

**Request Body:**
```json
{
  "message": "Phân tích đối thủ cạnh tranh chính của tôi trong thị trường booking cà phê là ai?",
  "project_id": 1,
  "use_google": true,
  "conversation_history": [
    {
      "role": "user",
      "content": "Tôi đang làm dự án về booking quán cà phê"
    },
    {
      "role": "assistant",
      "content": "Nghe có vẻ thú vị! Bạn cần tôi hỗ trợ gì về dự án này?"
    }
  ]
}
```

**Request Fields:**
- `message` (string, required): Tin nhắn từ người dùng
- `project_id` (integer, optional): ID dự án để lọc tài liệu liên quan
- `use_google` (boolean, default: true): Có sử dụng Google Search không
- `conversation_history` (array, optional): Lịch sử hội thoại trước đó

**Success Response (200 OK):**
```json
{
  "answer": "Dựa trên tài liệu bạn đã upload và kết quả tìm kiếm, các đối thủ cạnh tranh chính của bạn bao gồm:\n\n1. **Foody/ShopeeFood**: Mặc dù focus chủ yếu vào delivery, nhưng họ có user base lớn và brand mạnh. Điểm yếu là không chuyên về booking tại chỗ.\n\n2. **TableNow**: Chuyên về booking nhưng focus vào nhà hàng cao cấp, ít quán cà phê.\n\n3. **Pasgo**: Có tính năng booking nhà hàng và quán cà phê, nhưng UX chưa tối ưu cho phân khúc coffee shop.\n\n4. **Google Maps/Facebook**: Được sử dụng rộng rãi để tìm kiếm thông tin quán, nhưng không có tính năng booking trực tiếp.\n\nĐiểm khác biệt của bạn nên là: (1) Focus 100% vào coffee segment, (2) Loyalty program tốt hơn, (3) UI/UX được optimize cho trải nghiệm tìm kiếm và đặt chỗ coffee shop.",
  "sources": {
    "documents": [
      {
        "filename": "competitor_analysis.docx",
        "relevance_score": 0.89,
        "excerpt": "TableNow hiện là ứng dụng booking nhà hàng lớn nhất tại VN..."
      }
    ],
    "google_results": [
      {
        "title": "Top 10 Food Booking Apps in Vietnam 2025",
        "url": "https://example.com/article",
        "snippet": "Foody and ShopeeFood dominate the market..."
      }
    ]
  },
  "context_used": {
    "documents": true,
    "google_search": true,
    "project_context": true
  }
}
```

**Error Responses:**
- `500 Internal Server Error`: Lỗi chat

---

### **`POST /ai/ask`**

Hỏi đáp đơn giản với RAG (không có conversation history).

**Authentication:** Required (Bearer Token)

**Request Body:**
```json
{
  "question": "Thị trường F&B Technology Việt Nam có quy mô bao nhiêu?",
  "project_id": 1,
  "use_google": true
}
```

**Success Response (200 OK):**
*   Cấu trúc response tương tự như endpoint `/ai/chat`

**Error Responses:**
- `500 Internal Server Error`: Lỗi trả lời câu hỏi

---

### **`GET /ai/vector-store/stats`**

Lấy thống kê về vector store (database lưu trữ embeddings).

**Authentication:** Required (Bearer Token)

**Success Response (200 OK):**
```json
{
  "total_vectors": 1250,
  "dimension": 1536,
  "unique_documents": 28,
  "unique_projects": 5
}
```

**Error Responses:**
- `500 Internal Server Error`: Lỗi lấy thống kê

---

## 7. Error Codes & Status Codes

### **HTTP Status Codes**

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Request thành công |
| 201 | Created | Tạo resource thành công |
| 204 | No Content | Xóa thành công, không có response body |
| 400 | Bad Request | Dữ liệu request không hợp lệ |
| 401 | Unauthorized | Token không hợp lệ hoặc hết hạn |
| 403 | Forbidden | Không có quyền truy cập |
| 404 | Not Found | Không tìm thấy resource |
| 500 | Internal Server Error | Lỗi server |

### **Common Error Response Format**

```json
{
  "detail": "Error message description"
}
```

Hoặc với traceback (trong development):

```json
{
  "detail": {
    "error": "Error message",
    "trace": "Full traceback..."
  }
}
```

---

## 8. Authentication & Authorization

### **Bearer Token**

Tất cả các endpoint (trừ `/auth/register` và `/auth/token`) đều yêu cầu authentication.

**Header Format:**
```
Authorization: Bearer <YOUR_ACCESS_TOKEN>
```

**Example:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### **Token Expiration**

- Access Token có thời gian sống giới hạn (cấu hình trong `ACCESS_TOKEN_EXPIRE_MINUTES`)
- Khi token hết hạn, client cần đăng nhập lại thông qua `/auth/token`

### **WebSocket Authentication**

Với WebSocket, token được truyền qua query parameter:

```
ws://0.0.0.0:8000/projects/ws/1?token=<YOUR_ACCESS_TOKEN>
```

---

## 9. Rate Limiting & Best Practices

### **Best Practices**

1. **Caching**: Cache các response từ GET requests khi có thể
2. **Batch Operations**: Gom nhiều operations nhỏ thành một request lớn
3. **Pagination**: Sử dụng `limit` parameter cho các list endpoints
4. **Error Handling**: Luôn handle các error codes và retry với exponential backoff
5. **WebSocket**: Sử dụng WebSocket cho auto-save thay vì polling
6. **File Upload**: Compress files trước khi upload khi có thể

### **Request Size Limits**

- **JSON Body**: Max 10MB
- **File Upload**: Max 50MB per file
- **WebSocket Message**: Max 1MB per message

---

## 10. Examples & Use Cases

### **Use Case 1: Tạo dự án mới với AI**

```javascript
// 1. Generate project from description
const generateResponse = await fetch('http://0.0.0.0:8000/ai/generate-project', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    description: "Ứng dụng đặt chỗ quán cà phê với tích hợp AI"
  })
});

const projectData = await generateResponse.json();

// 2. Create project with generated data
const createResponse = await fetch('http://0.0.0.0:8000/projects/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(projectData)
});

const project = await createResponse.json();
console.log('Created project:', project);
```

### **Use Case 2: Real-time editing với WebSocket**

```javascript
// Connect to WebSocket
const ws = new WebSocket(`ws://0.0.0.0:8000/projects/ws/${sectionId}?token=${token}`);

ws.onopen = () => {
  console.log('Connected to WebSocket');
};

// Send updates (debounced)
const sendUpdate = debounce((title, content) => {
  ws.send(JSON.stringify({ title, content }));
}, 1000);

// Listen for confirmations
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.status === 'saved') {
    console.log('Changes saved!');
  }
};

// Update content
editor.addEventListener('input', () => {
  sendUpdate(editor.title, editor.content);
});
```

### **Use Case 3: Chat with RAG**

```javascript
// 1. Upload documents
const formData = new FormData();
formData.append('file', pdfFile);
formData.append('project_id', projectId);

await fetch('http://0.0.0.0:8000/ai/documents/upload', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
  },
  body: formData
});

// 2. Chat with AI
const conversationHistory = [];

async function chat(message) {
  conversationHistory.push({ role: 'user', content: message });
  
  const response = await fetch('http://0.0.0.0:8000/ai/chat', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      message,
      project_id: projectId,
      use_google: true,
      conversation_history: conversationHistory
    })
  });
  
  const result = await response.json();
  conversationHistory.push({ role: 'assistant', content: result.answer });
  
  return result;
}

// Use it
const answer = await chat("Phân tích thị trường của tôi như thế nào?");
console.log(answer.answer);
console.log(answer.sources);
```

---

## 11. Support & Contact

Nếu bạn gặp vấn đề hoặc có câu hỏi về API, vui lòng:

- Tạo issue trên GitHub repository
- Liên hệ qua email: support@startupkit.com
- Tham gia Discord community: [link]

**API Version**: 1.0  
**Last Updated**: October 24, 2025
