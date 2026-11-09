-- ========================
-- PLATFORM_REPORT & BILLING_TRANSACTION TABLES
-- ========================
CREATE TABLE IF NOT EXISTS platform_report (
    id              VARCHAR(50) PRIMARY KEY,
    report_type     VARCHAR(100) NOT NULL,
    target          VARCHAR(255) NOT NULL,
    reporter        VARCHAR(255) NOT NULL,
    reason          TEXT NOT NULL,
    severity        VARCHAR(50) NOT NULL,
    created_at      VARCHAR(50) NOT NULL,
    status          VARCHAR(50) NOT NULL,
    resolution_note TEXT
);

CREATE TABLE IF NOT EXISTS billing_transaction (
    id              VARCHAR(50) PRIMARY KEY,
    actor           VARCHAR(255) NOT NULL,
    tx_type         VARCHAR(100) NOT NULL,
    amount          VARCHAR(100) NOT NULL,
    gateway         VARCHAR(100) NOT NULL,
    status          VARCHAR(50) NOT NULL,
    created_at      VARCHAR(50) NOT NULL
);

-- ========================
-- SEED ROLES
-- ========================
INSERT INTO role (code, description) VALUES
    ('STARTUP', 'Startup Founder'),
    ('INVESTOR', 'Venture Capital / Angel Investor'),
    ('MENTOR', 'Ecosystem Mentor & Advisor'),
    ('ADMIN', 'Platform Administrator')
ON CONFLICT (code) DO NOTHING;

-- ========================
-- SEED CREDIBILITY SCORES
-- ========================
INSERT INTO credibility_score (id, entity_type, average_score, total_ratings, total_completed_sessions, update_at) VALUES
    ('11111111-1111-1111-1111-111111111101', 'STARTUP', 94.0, 18, 12, now()),
    ('11111111-1111-1111-1111-111111111102', 'STARTUP', 97.0, 29, 19, now()),
    ('11111111-1111-1111-1111-111111111103', 'INVESTOR', 96.0, 24, 0, now()),
    ('11111111-1111-1111-1111-111111111104', 'MENTOR', 97.0, 48, 142, now())
ON CONFLICT (id) DO NOTHING;

-- ========================
-- SEED USERS
-- ========================
INSERT INTO users (id, contact_email, contact_phone, full_name, verified, account_status, user_type, created_at, updated_at, roles_code, location) VALUES
    ('22222222-2222-2222-2222-222222222201', 'minh@agribot.vn', '0901234567', 'Nguyễn Văn Minh', true, 'ACTIVE', 'STARTUP', now(), now(), 'STARTUP', 'Hà Nội'),
    ('22222222-2222-2222-2222-222222222202', 'lan.tran@payease.vn', '0902345678', 'Trần Thị Lan', true, 'ACTIVE', 'STARTUP', now(), now(), 'STARTUP', 'TP. Hồ Chí Minh'),
    ('22222222-2222-2222-2222-222222222203', 'ngoc@mekong.vc', '0903456789', 'Trần Bảo Ngọc (Mekong Ventures)', true, 'ACTIVE', 'INVESTOR', now(), now(), 'INVESTOR', 'TP. Hồ Chí Minh'),
    ('22222222-2222-2222-2222-222222222204', 'an.le@mentor.vn', '0904567890', 'TS. Lê Hoàng An', true, 'ACTIVE', 'MENTOR', now(), now(), 'MENTOR', 'Hà Nội')
ON CONFLICT (id) DO NOTHING;

-- ========================
-- SEED STARTUPS
-- ========================
INSERT INTO startup (id, user_id, credibility_score_id, industry, description, team_size) VALUES
    ('33333333-3333-3333-3333-333333333301', '22222222-2222-2222-2222-222222222201', '11111111-1111-1111-1111-111111111101', 'Agritech', 'AI-driven crop monitoring for Vietnam 10M rice farmers. Reduces crop loss by 30% via solar IoT sensors.', 12),
    ('33333333-3333-3333-3333-333333333302', '22222222-2222-2222-2222-222222222202', '11111111-1111-1111-1111-111111111102', 'Fintech', 'B2B payment automation cutting reconciliation time by 90% across 22 Vietnamese banks.', 32)
ON CONFLICT (id) DO NOTHING;

-- ========================
-- SEED INVESTOR & MENTOR
-- ========================
INSERT INTO investor (id, user_id, credibility_score_id, investment_criteria, preferred_stages, organization_name, bio, investment_min, investment_max, linkedin_url, website_url) VALUES
    ('44444444-4444-4444-4444-444444444401', '22222222-2222-2222-2222-222222222203', '11111111-1111-1111-1111-111111111103', 'Fintech, Agritech, B2B SaaS, Healthtech', 'Pre-seed, Seed, Series A', 'Mekong Tech Ventures', 'Leading early-stage VC investing in Vietnam & SEA digital transformation.', 100000, 1500000, 'https://linkedin.com/in/tran-bao-ngoc-vc', 'https://mekongtechventures.vn')
ON CONFLICT (id) DO NOTHING;

INSERT INTO mentor (id, user_id, credibility_score_id, expertise, bio, hourly_rate, rating, review) VALUES
    ('55555555-5555-5555-5555-555555555501', '22222222-2222-2222-2222-222222222204', '11111111-1111-1111-1111-111111111104', 'Product Strategy, Fintech, Go-to-Market, Fundraising', '12 years scaling B2B fintech products across SEA. Advisor to 40+ startups.', 80.0, 4.9, 'Exceptional guidance on product roadmap and Series A fundraising.')
ON CONFLICT (id) DO NOTHING;

-- ========================
-- SEED PROJECTS
-- ========================
INSERT INTO project (id, startup_id, project_name, project_description) VALUES
    ('66666666-6666-6666-6666-666666666601', '33333333-3333-3333-3333-333333333301', 'AgriBot Vietnam — Solar IoT & AI Crop Intelligence', 'Trạm cảm biến IoT năng lượng mặt trời kết hợp AI cảnh báo sâu bệnh sớm 7 ngày cho 3,450 nông hộ và 18 hợp tác xã.'),
    ('66666666-6666-6666-6666-666666666602', '33333333-3333-3333-3333-333333333302', 'PayEase — B2B Payment Orchestration Engine', 'Nền tảng tự động hóa đối soát hóa đơn VAT và thanh toán đa ngân hàng cho 210 doanh nghiệp ($1.74M ARR).')
ON CONFLICT (id) DO NOTHING;

-- ========================
-- SEED DEALS & SESSIONS
-- ========================
INSERT INTO deal (id, startup_id, investor_id, project_id, contract_value, success_fee, status, signed_at, updated_at) VALUES
    ('77777777-7777-7777-7777-777777777701', '33333333-3333-3333-3333-333333333301', '44444444-4444-4444-4444-444444444401', '66666666-6666-6666-6666-666666666601', 300000.0, 30000.0, 'SIGNED', now(), now()),
    ('77777777-7777-7777-7777-777777777702', '33333333-3333-3333-3333-333333333302', '44444444-4444-4444-4444-444444444401', '66666666-6666-6666-6666-666666666602', 800000.0, 80000.0, 'NEGOTIATING', now(), now())
ON CONFLICT (id) DO NOTHING;

INSERT INTO advisory_session (id, mentor_id, startup_id, topic, start_time, end_time, format, rating, review, status) VALUES
    ('88888888-8888-8888-8888-888888888801', '55555555-5555-5555-5555-555555555501', '33333333-3333-3333-3333-333333333301', 'Chiến lược Go-to-Market qua kênh Hợp tác xã & chuẩn bị vòng Seed $500k', now() - interval '3 days', now() - interval '3 days' + interval '1 hour', 'ONLINE', 5.0, 'Cố vấn cực kỳ sát thực tế vận hành nông nghiệp ĐBSCL.', 'COMPLETED')
ON CONFLICT (id) DO NOTHING;

-- ========================
-- SEED REPORTS & BILLING TRANSACTIONS
-- ========================
INSERT INTO platform_report (id, report_type, target, reporter, reason, severity, created_at, status, resolution_note) VALUES
    ('RPT-1001', 'Fake Startup', 'CryptoGain AI X100', 'Trần Bảo Ngọc (Mekong Ventures)', 'Hồ sơ dự án cam kết lợi nhuận cố định 30%/tháng, số liệu ARR không có chứng từ.', 'High', '2026-11-09', 'Open', ''),
    ('RPT-1002', 'Scam', 'FastFund Global Syndicate', 'Nguyễn Văn Minh (AgriBot Vietnam)', 'Yêu cầu startup chuyển trước $2,000 phí thẩm định hồ sơ cá nhân ngoài Deal Room.', 'High', '2026-11-08', 'Investigating', 'Đang tạm khóa quyền nhắn tin.'),
    ('RPT-1003', 'Plagiarized Deck', 'CopyPay VN', 'Trần Thị Lan (PayEase)', 'Sao chép nguyên văn 8 slides kiến trúc thanh toán từ Pitch Deck của PayEase.', 'Medium', '2026-11-07', 'Investigating', '')
ON CONFLICT (id) DO NOTHING;

INSERT INTO billing_transaction (id, actor, tx_type, amount, gateway, status, created_at) VALUES
    ('PAY-8821', 'AgriBot Vietnam', 'Subscription (PRO_FOUNDER)', '499.000 ₫', 'PayOS VietQR', 'Completed', '2026-11-09'),
    ('PAY-8822', 'Mekong Tech Ventures', 'Subscription (INVESTOR_CLUB)', '999.000 ₫', 'PayOS VietQR', 'Completed', '2026-11-08'),
    ('PAY-8823', 'PayEase VN', 'Deal Success Fee (10%)', '75.000.000 ₫', 'VNPay / Bank Wire', 'Completed', '2026-11-07')
ON CONFLICT (id) DO NOTHING;
