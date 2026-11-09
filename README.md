# 🚀 StartupKit Platform Backend (Spring Boot 4 / Java 21)

> **Backend API chính thức cho nền tảng Hệ sinh thái Khởi nghiệp StartupKit (`https://github.com/startupkit-team/be`)**

---

## 🌐 1. Liên Kết Web & Tài Liệu API (Web & API Links)

- **Swagger UI (Local Backend):** [http://localhost:8080/swagger-ui/index.html](http://localhost:8080/swagger-ui/index.html)
- **OpenAPI JSON Spec:** [http://localhost:8080/v3/api-docs](http://localhost:8080/v3/api-docs)
- **Giao diện Frontend Next.js 16 (Local):** [http://localhost:3000/vi](http://localhost:3000/vi)
- **Giao diện Frontend (Vercel):** [https://startup-kit-fe.vercel.app](https://startup-kit-fe.vercel.app)
- **Cloud API Mirror (Render):** [https://startup-kit-be.onrender.com/docs](https://startup-kit-be.onrender.com/docs)
- **GitHub Backend Repo:** [https://github.com/startupkit-team/be](https://github.com/startupkit-team/be)
- **GitHub Frontend Repo:** [https://github.com/startupkit-team/fe](https://github.com/startupkit-team/fe)

---

## 🛠 2. Công Nghệ Sử Dụng

| Thành phần | Công nghệ |
| :--- | :--- |
| **Ngôn ngữ** | Java 21 LTS |
| **Framework** | Spring Boot 4.0.5 |
| **Cơ sở dữ liệu** | PostgreSQL 14+ & Flyway Migration (`V1`, `V2`) |
| **Bảo mật** | JWT (Nimbus JOSE + OAuth2 Google / LinkedIn + Spring Resource Server) |
| **API Docs** | springdoc-openapi (Swagger UI) |
| **Tiện ích** | MapStruct, Lombok, Maven |

---

## 📋 3. Danh Mục API Đã Hoàn Thiện

| Phân hệ | Method | Endpoint | Mô tả chức năng |
| :--- | :--- | :--- | :--- |
| **Auth & OAuth2** | `POST` | `/v1/auth/login` | Đăng nhập cấp Access Token & Refresh Token |
| **Auth & OAuth2** | `POST` | `/v1/auth/refresh-token` | Làm mới JWT Token |
| **Auth & OAuth2** | `POST` | `/v1/auth/exchange` | Đổi mã OAuth2 Google sang JWT Token |
| **Auth & OAuth2** | `POST` | `/v1/auth/forgot-password` | Gửi OTP / Link khôi phục mật khẩu |
| **Auth & OAuth2** | `POST` | `/v1/auth/reset-password` | Đặt lại mật khẩu mới |
| **Users & Profile** | `POST` | `/v1/users` | Đăng ký tài khoản (`STARTUP`, `INVESTOR`, `MENTOR`) |
| **Users & Profile** | `GET` | `/v1/users` | Lấy hồ sơ chi tiết theo vai trò |
| **Users & Profile** | `PUT` | `/v1/users` | Cập nhật thông tin cá nhân |
| **Marketplace** | `GET` | `/v1/market/startups` | Danh sách Startup & Điểm tín nhiệm AI |
| **Marketplace** | `GET` | `/v1/market/investors` | Danh sách Quỹ đầu tư & Khẩu vị đầu tư |
| **Marketplace** | `GET` | `/v1/market/mentors` | Danh sách Cố vấn chuyên gia & Đánh giá |
| **Projects** | `GET/POST` | `/v1/projects` | Danh sách & Tạo mới dự án khởi nghiệp |
| **Projects** | `GET/PUT/DELETE` | `/v1/projects/{id}` | Chi tiết, cập nhật, xóa dự án |
| **AI Engine** | `POST` | `/v1/ai/generate-description` | AI tự động viết Problem, Solution, Value Proposition & Product Description |
| **AI Engine** | `POST` | `/v1/ai/evaluate-pitch` | Chấm điểm tín nhiệm AI & Gợi ý ghép đôi Investor/Mentor |
| **Deals & NDA** | `GET/POST` | `/v1/deals` | Quản lý thương vụ đầu tư & Tính phí 10% Success Fee |
| **Deals & NDA** | `PUT` | `/v1/deals/{id}/status` | Cập nhật trạng thái Deal (`PENDING`, `NEGOTIATING`, `SIGNED`, `CANCELLED`) |
| **Deals & NDA** | `POST` | `/v1/deals/{id}/sign-nda` | Ký thỏa thuận bảo mật điện tử (Mutual e-NDA) trong Deal Room |
| **Mentorship** | `GET/POST` | `/v1/sessions` | Danh sách & Đặt lịch phiên cố vấn 1-1 |
| **Mentorship** | `PUT` | `/v1/sessions/{id}/status` | Cập nhật trạng thái phiên cố vấn |
| **Mentorship** | `POST` | `/v1/sessions/{id}/review` | Đánh giá & chấm điểm chất lượng phiên cố vấn |
| **Admin (`qqa_ManageReport`)** | `GET/POST` | `/v1/admin/reports` | Quản lý báo cáo vi phạm (Fake Startup, Scam, Spam, Plagiarized Deck) |
| **Admin (`qqa_ManageReport`)** | `PUT` | `/v1/admin/reports/{id}/status` | Xử lý, điều tra, gỡ nội dung hoặc khóa tài khoản vi phạm |
| **Billing (PayOS/VietQR)** | `GET` | `/v1/billing/plans` | Danh sách gói hội viên (`FREE`, `FOUNDER_PRO`, `VC_ENTERPRISE`) |
| **Billing (PayOS/VietQR)** | `GET` | `/v1/billing/transactions` | Lịch sử giao dịch & đối soát thanh toán |
| **Billing (PayOS/VietQR)** | `POST` | `/v1/billing/checkout-vietqr` | Tạo mã thanh toán VietQR Napas247 & xác thực giao dịch |

---

## 🌿 4. Các Nhánh Chức Năng Backend (Git Branches)

- `main` & `develop`: Nhánh tích hợp chính chứa toàn bộ API và Flyway migrations (`V1`, `V2`).
- `qqa_ManageReport`: Phân hệ quản trị báo cáo vi phạm (`/v1/admin/reports`).
- `feature/project-and-ai-pitch`: Phân hệ CRUD dự án (`/v1/projects`) & Động cơ AI sinh mô tả/chấm điểm (`/v1/ai/*`).
- `feature/marketplace-and-deals`: Phân hệ Sàn giao dịch (`/v1/market/*`) & Phòng đàm phán Deal Room + e-NDA (`/v1/deals/*`).
- `feature/mentorship-sessions`: Phân hệ đặt lịch và đánh giá phiên cố vấn (`/v1/sessions/*`).
- `feature/billing-vietqr`: Phân hệ gói hội viên & thanh toán VietQR PayOS (`/v1/billing/*`).

---

## 🚀 5. Hướng Dẫn Chạy Dự Án

1. **Khởi động PostgreSQL:**
   ```bash
   docker compose up -d
   ```
2. **Biên dịch & Chạy ứng dụng:**
   ```bash
   ./mvnw spring-boot:run
   ```
3. **Truy cập Swagger UI:**
   - `http://localhost:8080/swagger-ui/index.html`
