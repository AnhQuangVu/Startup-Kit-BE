-- ========================================================
-- V3__seed_real_vietnam_ecosystem.sql
-- Authentic Vietnam Tech Ecosystem Seed Data (Startups, VCs, Mentors)
-- ========================================================

-- 1. CREDIBILITY SCORES FOR TOP TIER STARTUPS & LEADERS
INSERT INTO credibility_score (id, entity_type, average_score, total_ratings, total_completed_sessions, update_at) VALUES
    ('11111111-1111-1111-1111-111111111111', 'STARTUP', 98.0, 45, 32, now()), -- Coolmate
    ('11111111-1111-1111-1111-111111111112', 'STARTUP', 97.0, 38, 26, now()), -- Dat Bike
    ('11111111-1111-1111-1111-111111111113', 'STARTUP', 98.0, 52, 40, now()), -- BuyMed
    ('11111111-1111-1111-1111-111111111114', 'STARTUP', 97.0, 48, 35, now()), -- TopCV
    ('11111111-1111-1111-1111-111111111115', 'INVESTOR', 98.0, 60, 0, now()),  -- Do Ventures
    ('11111111-1111-1111-1111-111111111116', 'INVESTOR', 96.0, 50, 0, now()),  -- ThinkZone Ventures
    ('11111111-1111-1111-1111-111111111117', 'MENTOR', 98.0, 75, 165, now()),  -- Pham Chi Nhu
    ('11111111-1111-1111-1111-111111111118', 'MENTOR', 98.0, 88, 240, now())   -- Le Han Tue Lam
ON CONFLICT (id) DO NOTHING;

-- 2. USERS
INSERT INTO users (id, contact_email, contact_phone, full_name, verified, account_status, user_type, created_at, updated_at, roles_code, location) VALUES
    ('22222222-2222-2222-2222-222222222211', 'nhu.pham@coolmate.me', '0912345678', 'Phạm Chí Nhu', true, 'ACTIVE', 'STARTUP', now(), now(), 'STARTUP', 'Hà Nội'),
    ('22222222-2222-2222-2222-222222222212', 'son@dat.bike', '0923456789', 'Nguyễn Bá Cảnh Sơn', true, 'ACTIVE', 'STARTUP', now(), now(), 'STARTUP', 'TP. Hồ Chí Minh'),
    ('22222222-2222-2222-2222-222222222213', 'hoang.nguyen@buymed.com', '0934567890', 'Hoàng Nguyễn', true, 'ACTIVE', 'STARTUP', now(), now(), 'STARTUP', 'TP. Hồ Chí Minh'),
    ('22222222-2222-2222-2222-222222222214', 'hieu.tran@topcv.vn', '0945678901', 'Trần Trung Hiếu', true, 'ACTIVE', 'STARTUP', now(), now(), 'STARTUP', 'Hà Nội'),
    ('22222222-2222-2222-2222-222222222215', 'tuelam@doventures.vc', '0956789012', 'Lê Hàn Tuệ Lâm (Do Ventures)', true, 'ACTIVE', 'INVESTOR', now(), now(), 'INVESTOR', 'Hà Nội'),
    ('22222222-2222-2222-2222-222222222216', 'thanhdo@thinkzone.vn', '0967890123', 'Bùi Thành Đô (ThinkZone Ventures)', true, 'ACTIVE', 'INVESTOR', now(), now(), 'INVESTOR', 'Hà Nội'),
    ('22222222-2222-2222-2222-222222222217', 'nhu.mentor@startupkit.vn', '0978901234', 'Phạm Chí Nhu (Mentor D2C)', true, 'ACTIVE', 'MENTOR', now(), now(), 'MENTOR', 'Hà Nội'),
    ('22222222-2222-2222-2222-222222222218', 'tuelam.mentor@startupkit.vn', '0989012345', 'Lê Hàn Tuệ Lâm (Mentor VC)', true, 'ACTIVE', 'MENTOR', now(), now(), 'MENTOR', 'Hà Nội')
ON CONFLICT (id) DO NOTHING;

-- 3. STARTUPS
INSERT INTO startup (id, user_id, credibility_score_id, industry, description, team_size) VALUES
    ('33333333-3333-3333-3333-333333333311', '22222222-2222-2222-2222-222222222211', '11111111-1111-1111-1111-111111111111', 'E-commerce', 'Thương hiệu thời trang nam ứng dụng công nghệ D2C đạt $26M ARR, hơn 1.5 triệu khách hàng thân thiết.', 180),
    ('33333333-3333-3333-3333-333333333312', '22222222-2222-2222-2222-222222222212', '11111111-1111-1111-1111-111111111112', 'CleanTech', 'Hãng xe máy điện công nghệ cao tiên phong tại Đông Nam Á, tầm hoạt động 200km và sạc nhanh 20 phút.', 220),
    ('33333333-3333-3333-3333-333333333313', '22222222-2222-2222-2222-222222222213', '11111111-1111-1111-1111-111111111113', 'Healthtech', 'Sàn phân phối dược phẩm B2B minh bạch phục vụ hơn 35,000 nhà thuốc và phòng khám trên 63 tỉnh thành.', 450),
    ('33333333-3333-3333-3333-333333333314', '22222222-2222-2222-2222-222222222214', '11111111-1111-1111-1111-111111111114', 'SaaS', 'Hệ sinh thái HRTech & nền tảng tuyển dụng thông minh ứng dụng AI số 1 kết nối 6 triệu ứng viên.', 310)
ON CONFLICT (id) DO NOTHING;

-- 4. INVESTORS
INSERT INTO investor (id, user_id, credibility_score_id, investment_criteria, preferred_stages, organization_name, bio, investment_min, investment_max, linkedin_url, website_url) VALUES
    ('44444444-4444-4444-4444-444444444411', '22222222-2222-2222-2222-222222222215', '11111111-1111-1111-1111-111111111115', 'Fintech, SaaS, Edtech, E-commerce', 'Pre-seed, Seed, Series A', 'Do Ventures', 'Quỹ đầu tư mạo hiểm giai đoạn sớm quy mô $50M tập trung vào các công ty khởi nghiệp công nghệ Việt Nam.', 200000, 2000000, 'https://linkedin.com/company/doventures', 'https://doventures.vc'),
    ('44444444-4444-4444-4444-444444444412', '22222222-2222-2222-2222-222222222216', '11111111-1111-1111-1111-111111111116', 'Edtech, Fintech, Logistics, SaaS', 'Seed, Series A', 'ThinkZone Ventures', 'Quỹ đầu tư bản địa lớn nhất Việt Nam quy mô $60M Fund II hỗ trợ các startup giai đoạn tăng tốc quy mô.', 200000, 1500000, 'https://linkedin.com/company/thinkzoneventures', 'https://thinkzone.vn')
ON CONFLICT (id) DO NOTHING;

-- 5. MENTORS
INSERT INTO mentor (id, user_id, credibility_score_id, expertise, bio, hourly_rate, rating, review) VALUES
    ('55555555-5555-5555-5555-555555555511', '22222222-2222-2222-2222-222222222217', '11111111-1111-1111-1111-111111111117', 'Go-to-Market, Marketing, Operations, D2C', 'Co-founder & CEO Coolmate. Cố vấn chiến lược D2C, quản trị tồn kho và gọi vốn Series A/B.', 90.0, 5.0, 'Chia sẻ thực chiến sâu sắc về tối ưu chi phí vận hành và giữ chân khách hàng.'),
    ('55555555-5555-5555-5555-555555555512', '22222222-2222-2222-2222-222222222218', '11111111-1111-1111-1111-111111111118', 'Finance, Fundraising, SaaS Valuation', 'General Partner Do Ventures. Cố vấn thẩm định tài chính, định giá và đàm phán Term Sheet quốc tế.', 120.0, 5.0, 'Định hướng chiến lược gọi vốn quốc tế cực kỳ sắc bén và chuyên nghiệp.')
ON CONFLICT (id) DO NOTHING;

-- 6. PROJECTS
INSERT INTO project (id, startup_id, project_name, project_description) VALUES
    ('66666666-6666-6666-6666-666666666611', '33333333-3333-3333-3333-333333333311', 'Coolmate D2C Platform & Supply Chain Automation', 'Nền tảng mua sắm thời trang nam ứng dụng công nghệ D2C ($26M ARR, 1.5M khách hàng).'),
    ('66666666-6666-6666-6666-666666666612', '33333333-3333-3333-3333-333333333312', 'Dat Bike High-Performance Clean Mobility Ecosystem', 'Xe máy điện thông minh tầm hoạt động 200km và hạ tầng sạc siêu nhanh Dat Charge.'),
    ('66666666-6666-6666-6666-666666666613', '33333333-3333-3333-3333-333333333313', 'BuyMed Thuocsi B2B Healthcare Marketplace', 'Sàn phân phối dược phẩm minh bạch cho 35,000 nhà thuốc và phòng khám trên 63 tỉnh.'),
    ('66666666-6666-6666-6666-666666666614', '33333333-3333-3333-3333-333333333314', 'TopCV AI Smart Matching & HR Tech Platform', 'Hệ sinh thái tuyển dụng và nhân sự thông minh ứng dụng AI với 6 triệu ứng viên.')
ON CONFLICT (id) DO NOTHING;

-- 7. REAL DEALS
INSERT INTO deal (id, startup_id, investor_id, project_id, contract_value, success_fee, status, signed_at, updated_at) VALUES
    ('77777777-7777-7777-7777-777777777711', '33333333-3333-3333-3333-333333333311', '44444444-4444-4444-4444-444444444411', '66666666-6666-6666-6666-666666666611', 1500000.0, 150000.0, 'SIGNED', now() - interval '15 days', now()),
    ('77777777-7777-7777-7777-777777777712', '33333333-3333-3333-3333-333333333312', '44444444-4444-4444-4444-444444444412', '66666666-6666-6666-6666-666666666612', 2000000.0, 200000.0, 'NEGOTIATING', now() - interval '5 days', now())
ON CONFLICT (id) DO NOTHING;
