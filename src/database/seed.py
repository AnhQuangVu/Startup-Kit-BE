import logging
import datetime
from sqlalchemy.orm import Session
from src.core.security import get_password_hash
from src.database.core import SessionLocal, Base, engine
from src.database.models import (
    User, UserRole, UserProfile, MentorProfile,
    Project, ProjectStage, Category, ProjectPost, PostComment, PostLike
)

logger = logging.getLogger(__name__)

def seed_database(db: Session):
    logger.info("Starting database seeding...")
    default_password_hash = get_password_hash("StartupKit@2025")

    # 1. Seed Categories
    categories_data = [
        ("AI & Trí tuệ nhân tạo", "technology"),
        ("Công nghệ tài chính (Fintech)", "finance"),
        ("Công nghệ y tế (Healthtech)", "healthcare"),
        ("Công nghệ giáo dục (Edtech)", "education"),
        ("Nông nghiệp thông minh (AgriTech)", "agriculture"),
        ("Thương mại điện tử & Bán lẻ", "commerce"),
        ("Vận tải & Logistics", "logistics"),
        ("Công nghệ xanh & Môi trường", "environment"),
        ("Phần mềm doanh nghiệp (SaaS)", "software"),
        ("An toàn thông tin & An ninh mạng", "security"),
    ]
    created_categories = {}
    for name, cat_type in categories_data:
        cat = db.query(Category).filter(Category.name == name).first()
        if not cat:
            cat = Category(name=name, type=cat_type)
            db.add(cat)
            db.flush()
        created_categories[name] = cat

    # 2. Seed Users
    # Founders
    founders_data = [
        {
            "name": "Nguyễn Văn An",
            "email": "nguyenvanan.founder@startupkit.vn",
            "role": UserRole.FOUNDER,
            "company": "EcoFarm IoT",
            "avatar": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=300",
            "bio": "Kỹ sư Nông nghiệp số, 8 năm nghiên cứu giải pháp IoT và tiết kiệm nguồn nước.",
            "location": "Lâm Đồng, Việt Nam",
            "linkedin": "https://linkedin.com/in/nguyenvanan-ecofarm",
        },
        {
            "name": "TS. Lê Thị Bích",
            "email": "lethibich.founder@startupkit.vn",
            "role": UserRole.FOUNDER,
            "company": "MediAI Vision",
            "avatar": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=300",
            "bio": "Tiến sĩ Khoa học Máy tính, chuyên gia ứng dụng Computer Vision trong y tế dự phòng.",
            "location": "Hà Nội, Việt Nam",
            "linkedin": "https://linkedin.com/in/lethibich-mediai",
        },
        {
            "name": "Trần Minh Đức",
            "email": "tranminhduc.founder@startupkit.vn",
            "role": UserRole.FOUNDER,
            "company": "FinFlow Core",
            "avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300",
            "bio": "Cựu Giám đốc Tài chính Fintech, đam mê xây dựng hạ tầng tài chính tinh gọn cho SMEs.",
            "location": "TP. Hồ Chí Minh, Việt Nam",
            "linkedin": "https://linkedin.com/in/tranminhduc-finflow",
        },
        {
            "name": "Phạm Thu Hương",
            "email": "phamthuhuong.founder@startupkit.vn",
            "role": UserRole.FOUNDER,
            "company": "EduLearn Adaptive",
            "avatar": "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=300",
            "bio": "Thạc sĩ Tâm lý Giáo dục Đại học Melbourne, sáng lập giải pháp học thích ứng bằng AI.",
            "location": "Đà Nẵng, Việt Nam",
            "linkedin": "https://linkedin.com/in/phamthuhuong-edulearn",
        },
        {
            "name": "Hoàng Hoài Nam",
            "email": "hoanghoainam.founder@startupkit.vn",
            "role": UserRole.FOUNDER,
            "company": "LogiSmart Green",
            "avatar": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=300",
            "bio": "Chuyên gia Tối ưu hóa Chuỗi Cung ứng và Giảm phát thải Carbon Logistics.",
            "location": "Bình Dương, Việt Nam",
            "linkedin": "https://linkedin.com/in/hoanghoainam-logismart",
        },
        {
            "name": "Đặng Quang Huy",
            "email": "dangquanghuy.founder@startupkit.vn",
            "role": UserRole.FOUNDER,
            "company": "CyberSafe Shield",
            "avatar": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=300",
            "bio": "Certified Ethical Hacker (CEH), 12 năm dẫn dắt các đội phản ứng nhanh an toàn mạng.",
            "location": "Hà Nội, Việt Nam",
            "linkedin": "https://linkedin.com/in/dangquanghuy-cybersafe",
        },
        {
            "name": "Nguyễn Ngọc Lan",
            "email": "nguyenngoclan.founder@startupkit.vn",
            "role": UserRole.FOUNDER,
            "company": "ReGreen Pack",
            "avatar": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=300",
            "bio": "Kỹ sư Công nghệ Sinh học, biến phụ phẩm nông nghiệp thành bao bì tự hủy sinh học.",
            "location": "Bến Tre, Việt Nam",
            "linkedin": "https://linkedin.com/in/nguyenngoclan-regreen",
        },
        {
            "name": "Vũ Tuấn Anh",
            "email": "vutuananh.founder@startupkit.vn",
            "role": UserRole.FOUNDER,
            "company": "WorkPulse SaaS",
            "avatar": "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=300",
            "bio": "Full-stack Software Architect, tác giả nền tảng vận hành doanh nghiệp không chạm.",
            "location": "TP. Hồ Chí Minh, Việt Nam",
            "linkedin": "https://linkedin.com/in/vutuananh-workpulse",
        },
    ]

    # Investors
    investors_data = [
        {
            "name": "Phạm Thanh Hưng",
            "email": "shark.hung@venture.vn",
            "role": UserRole.INVESTOR,
            "company": "Cen Group & Angel Fund",
            "avatar": "https://images.unsplash.com/photo-1560250097-0b93528c311a?w=300",
            "bio": "Nhà đầu tư thiên thần, Phó Chủ tịch HĐQT Cen Group. Tập trung vào B2B SaaS, Proptech và AI.",
            "location": "Hà Nội, Việt Nam",
            "linkedin": "https://linkedin.com/in/shark-hung-cen",
        },
        {
            "name": "Đỗ Thị Kim Liên",
            "email": "shark.lien@vass.com.vn",
            "role": UserRole.INVESTOR,
            "company": "Green Environment Fund",
            "avatar": "https://images.unsplash.com/photo-1573497019940-1c28c88b4f3e?w=300",
            "bio": "Nhà đầu tư vì cộng đồng, ưu tiên hỗ trợ các dự án Nước sạch, Năng lượng tái tạo và Nữ quyền.",
            "location": "TP. Hồ Chí Minh, Việt Nam",
            "linkedin": "https://linkedin.com/in/shark-lien-green",
        },
        {
            "name": "Nguyễn Hòa Bình",
            "email": "shark.binh@nexttech.asia",
            "role": UserRole.INVESTOR,
            "company": "NextTech Group of Technopreneurs",
            "avatar": "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=300",
            "bio": "Chủ tịch NextTech. Đầu tư và cố vấn thúc đẩy Digital Economy và E-Logistics Đông Nam Á.",
            "location": "Hà Nội, Việt Nam",
            "linkedin": "https://linkedin.com/in/shark-binh-nexttech",
        },
        {
            "name": "Lê Hạnh",
            "email": "lehanh@vinacapital.com",
            "role": UserRole.INVESTOR,
            "company": "VinaCapital Ventures",
            "avatar": "https://images.unsplash.com/photo-1580894732444-8ecded7900cd?w=300",
            "bio": "Giám đốc Quỹ Đầu tư Công nghệ, tìm kiếm các startup đột phá tại vòng Seed & Series A.",
            "location": "TP. Hồ Chí Minh, Việt Nam",
            "linkedin": "https://linkedin.com/in/lehanh-vinacapital",
        },
    ]

    # Mentors
    mentors_data = [
        {
            "name": "TS. Nguyễn Hữu Hải",
            "email": "nguyenhuuhai.mentor@gmail.com",
            "role": UserRole.MENTOR,
            "company": "AI Innovation Lab",
            "avatar": "https://images.unsplash.com/photo-1537368910025-700350fe46c7?w=300",
            "bio": "Cố vấn Công nghệ Trí tuệ Nhân tạo và Machine Learning, cựu chuyên gia nghiên cứu tại Google.",
            "location": "Hà Nội, Việt Nam",
            "linkedin": "https://linkedin.com/in/nguyenhuuhai-ai",
            "title": "Cố vấn Cao cấp Trí tuệ Nhân tạo & Big Data",
            "current_position": "Giám đốc Khoa học tại AI Innovation Lab",
            "expertise_areas": ["Trí tuệ nhân tạo (AI)", "Machine Learning", "Deep Learning", "Kiến trúc Đám mây"],
            "mentoring_experience": "Hơn 12 năm hướng dẫn và ươm tạo kỹ thuật cho hơn 40 startup công nghệ.",
            "achievements": [
                {"title": "Ex-Google AI Resident", "year": "2020"},
                {"title": "Top 10 Nhà khoa học AI trẻ Việt Nam", "year": "2023"}
            ]
        },
        {
            "name": "Luật sư Trần Thị Mai",
            "email": "tranthimai.mentor@gmail.com",
            "role": UserRole.MENTOR,
            "company": "Vietnam TechLaw Partners",
            "avatar": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=300",
            "bio": "Chuyên gia tư vấn pháp lý và tái cấu trúc vốn cho các thương vụ M&A công nghệ hàng đầu.",
            "location": "TP. Hồ Chí Minh, Việt Nam",
            "linkedin": "https://linkedin.com/in/tranthimai-law",
            "title": "Chuyên gia Pháp chế Doanh nghiệp & Gọi vốn Quốc tế",
            "current_position": "Managing Partner tại Vietnam TechLaw",
            "expertise_areas": ["Pháp chế Doanh nghiệp", "Gọi vốn & M&A", "Bảo hộ Sở hữu Trí tuệ", "Tuân thủ GDPR/PDPA"],
            "mentoring_experience": "Đồng hành tư vấn pháp lý cho 25 thương vụ gọi vốn thành công tại thị trường VN & Singapore.",
            "achievements": [
                {"title": "Luật sư Doanh nghiệp Xuất sắc Năm", "year": "2022"},
                {"title": "Thành viên Hội đồng Cố vấn Khởi nghiệp Quốc gia", "year": "2024"}
            ]
        },
        {
            "name": "Ông Vương Quang Khải",
            "email": "vuongquangkhai.mentor@gmail.com",
            "role": UserRole.MENTOR,
            "company": "ScaleUp Growth Hub",
            "avatar": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=300",
            "bio": "Chuyên gia Tăng trưởng Sản phẩm (Product-Led Growth) và Chiến lược Mở rộng Thị trường Quốc tế.",
            "location": "Singapore / TP. Hồ Chí Minh",
            "linkedin": "https://linkedin.com/in/vuongquangkhai-growth",
            "title": "Cố vấn Tăng trưởng & Mở rộng Thị trường Khu vực",
            "current_position": "Chief Growth Officer tại ScaleUp Hub",
            "expertise_areas": ["Tăng trưởng Sản phẩm (PLG)", "Go-To-Market Strategy", "Quản trị Trải nghiệm Người dùng", "B2B Sales Funnel"],
            "mentoring_experience": "Giúp 5 startup tăng trưởng doanh thu x10 trong vòng 18 tháng sau khi đạt PMF.",
            "achievements": [
                {"title": "Cố vấn Vàng Vườn ươm Khởi nghiệp ĐHQG", "year": "2023"},
                {"title": "Diễn giả Hội nghị Khởi nghiệp Đông Nam Á", "year": "2024"}
            ]
        },
    ]

    created_users = {}
    for user_info in founders_data + investors_data + mentors_data:
        existing = db.query(User).filter(User.email == user_info["email"]).first()
        if not existing:
            u = User(
                full_name=user_info["name"],
                email=user_info["email"],
                hashed_password=default_password_hash,
                role=user_info["role"],
                is_active=True,
                cover_url="https://images.unsplash.com/photo-1557804506-669a67965ba0?w=1200",
                pitch_deck_url="https://startupkit.vn/decks/sample-deck.pdf",
                connect_goal="Mở rộng mạng lưới hợp tác, kết nối nhà đầu tư và cố vấn chiến lược."
            )
            prof = UserProfile(
                avatar_url=user_info["avatar"],
                bio=user_info["bio"],
                company=user_info.get("company"),
                location=user_info.get("location"),
                linkedin=user_info.get("linkedin"),
                website_url=f"https://startupkit.vn/{user_info['email'].split('@')[0]}",
                achievements=[{"title": f"Top Innovator 2024 - {user_info['name']}"}],
            )
            u.profile = prof

            if user_info["role"] == UserRole.MENTOR:
                m_prof = MentorProfile(
                    title=user_info.get("title"),
                    current_position=user_info.get("current_position"),
                    expertise_areas=user_info.get("expertise_areas"),
                    community_link=user_info.get("linkedin"),
                    mentoring_experience=user_info.get("mentoring_experience"),
                    achievements=user_info.get("achievements")
                )
                u.mentor_profile = m_prof

            db.add(u)
            db.flush()
            created_users[user_info["email"]] = u
        else:
            created_users[user_info["email"]] = existing

    # 3. Seed Projects
    projects_data = [
        {
            "founder_email": "nguyenvanan.founder@startupkit.vn",
            "name": "EcoFarm IoT",
            "tagline": "Hệ thống giám sát và tưới tiêu nông nghiệp tự động thông minh bằng cảm biến IoT & AI",
            "description": "EcoFarm IoT là giải pháp toàn diện giúp nhà nông và hợp tác xã giám sát độ ẩm, dinh dưỡng đất và thời tiết theo thời gian thực. Bằng việc kết hợp các cảm biến không dây với thuật toán AI dự báo nhu cầu nước, hệ thống giúp tiết kiệm 40% chi phí nước ngọt và tăng 25% năng suất cây trồng.",
            "logo_url": "https://images.unsplash.com/photo-1574943320219-553eb213f72d?w=300",
            "team_image": {"url": "https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=800"},
            "stage": ProjectStage.LAUNCH,
            "industry": "AgriTech & Nông nghiệp thông minh",
            "pain_point": "Chi phí nước ngọt và phân bón ngày càng tăng, hạn hán kéo dài tại Tây Nguyên và Đồng Bằng Sông Cửu Long.",
            "solution": "Mạng lưới cảm biến IoT năng lượng mặt trời kết nối đám mây, tự động điều tiết van tưới chính xác theo mililit.",
            "product": "Bộ thiết bị phần cứng Sensor Hub và ứng dụng di động EcoFarm Dashboard trên iOS/Android.",
            "customer_segment": "Chủ nông trại sầu riêng, cà phê, dưa lưới và các hợp tác xã nông nghiệp công nghệ cao.",
            "market_size": "Hơn 500 triệu USD quy mô thị trường nông nghiệp chính xác tại Đông Nam Á.",
            "market_area": "Lâm Đồng, Đắk Lắk, Tiền Giang, Cần Thơ",
            "business_model": "Bán bộ kit phần cứng + Gói thuê bao phần mềm SaaS quản lý mùa vụ hàng tháng.",
            "capital_source": "500.000 USD",
            "revenue_goal": "1.200.000 USD năm 2026",
            "member_count": 8,
            "deployment_location": "Đà Lạt, Lâm Đồng",
            "website_url": "https://ecofarm-iot.vn",
        },
        {
            "founder_email": "lethibich.founder@startupkit.vn",
            "name": "MediAI Vision",
            "tagline": "Trợ lý AI hỗ trợ bác sĩ chẩn đoán hình ảnh X-quang và CT Scanner với độ chính xác 96.8%",
            "description": "MediAI Vision hỗ trợ các bệnh viện tuyến cơ sở giải quyết tình trạng thiếu hụt chuyên gia chẩn đoán hình ảnh. Nền tảng phân tích hơn 1.000 ca chụp mỗi phút, tự động khoanh vùng các tổn thương phổi, xương và u hạt tiền ung thư.",
            "logo_url": "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=300",
            "team_image": {"url": "https://images.unsplash.com/photo-1576091160550-2173dba999ef?w=800"},
            "stage": ProjectStage.LAUNCH,
            "industry": "Công nghệ y tế (Healthtech)",
            "pain_point": "Bác sĩ chẩn đoán hình ảnh bị quá tải, nguy cơ bỏ sót tổn thương nhỏ ở giai đoạn vàng.",
            "solution": "Mô hình Deep Learning đạt chuẩn y khoa quốc tế, tích hợp mượt mà vào hệ thống PACS bệnh viện.",
            "product": "MediAI Cloud Server & Plugin tích hợp trực tiếp máy quét y tế.",
            "customer_segment": "Bệnh viện đa khoa, phòng khám chẩn đoán hình ảnh tư nhân và trung tâm y tế dự phòng.",
            "market_size": "1.8 tỷ USD tại thị trường Châu Á - Thái Bình Dương.",
            "market_area": "Hà Nội, TP.HCM, Đà Nẵng",
            "business_model": "Thu phí trên từng lượt quét hình ảnh (Pay-per-scan) hoặc gói License hàng năm.",
            "capital_source": "1.200.000 USD",
            "revenue_goal": "3.000.000 USD năm 2026",
            "member_count": 12,
            "deployment_location": "Hà Nội",
            "website_url": "https://mediaivision.health",
        },
        {
            "founder_email": "tranminhduc.founder@startupkit.vn",
            "name": "FinFlow Core",
            "tagline": "Nền tảng tự động hóa quản lý dòng tiền và dự báo tài chính bằng AI cho doanh nghiệp SMEs",
            "description": "FinFlow Core kết nối đa ngân hàng và phần mềm kế toán, tự động đối soát dòng tiền, xuất hóa đơn thông minh và cảnh báo rủi ro thanh khoản trước 60 ngày cho các chủ doanh nghiệp vừa và nhỏ.",
            "logo_url": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=300",
            "team_image": {"url": "https://images.unsplash.com/photo-1556761175-5973dc0f32e7?w=800"},
            "stage": ProjectStage.HOAN_THIEN_SAN_PHAM,
            "industry": "Công nghệ tài chính (Fintech)",
            "pain_point": "82% startup và SMEs thất bại do đứt gãy dòng tiền và không dự báo được lịch thu/chi.",
            "solution": "Đồng bộ Open Banking API, AI phân tích hành vi thanh toán và tự động nhắc nợ đa kênh.",
            "product": "Ứng dụng FinFlow Web & Mobile đồng bộ dữ liệu kế toán tự động.",
            "customer_segment": "Hơn 800.000 doanh nghiệp SMEs và hộ kinh doanh cá thể tại Việt Nam.",
            "market_size": "350 triệu USD thị trường FinTech B2B.",
            "market_area": "Toàn quốc",
            "business_model": "Gói thuê bao định kỳ SaaS từ 499.000 VNĐ - 2.999.000 VNĐ/tháng.",
            "capital_source": "750.000 USD",
            "revenue_goal": "2.000.000 USD",
            "member_count": 10,
            "deployment_location": "TP. Hồ Chí Minh",
            "website_url": "https://finflow.vn",
        },
        {
            "founder_email": "phamthuhuong.founder@startupkit.vn",
            "name": "EduLearn Adaptive",
            "tagline": "Gia sư ảo 1-1 ứng dụng AI cá nhân hóa lộ trình học tập cho học sinh phổ thông",
            "description": "EduLearn Adaptive phân tích điểm mạnh, điểm yếu và phong cách tiếp thu của từng học sinh để tự động tạo ra bài giảng, bài tập trắc nghiệm và lộ trình ôn thi cá nhân hóa, giúp học sinh tiến bộ vượt bậc sau 4 tuần.",
            "logo_url": "https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=300",
            "team_image": {"url": "https://images.unsplash.com/photo-1524178232363-1fb2b075b655?w=800"},
            "stage": ProjectStage.LAUNCH,
            "industry": "Công nghệ giáo dục (Edtech)",
            "pain_point": "Học thêm đại trà không hiệu quả, học phí gia sư chất lượng cao quá đắt đỏ với phụ huynh.",
            "solution": "AI phân tích sai số từng câu hỏi, giải thích cặn kẽ và bổ túc lỗ hổng kiến thức kịp thời.",
            "product": "Nền tảng học trực tuyến đa nền tảng kết hợp phòng luyện thi ảo.",
            "customer_segment": "Học sinh từ lớp 6 đến lớp 12 và phụ huynh học sinh.",
            "market_size": "1.2 tỷ USD thị trường EdTech học thêm và ôn thi.",
            "market_area": "Hà Nội, Đà Nẵng, TP.HCM",
            "business_model": "Đăng ký thành viên học tập hàng tháng/hàng năm (Freemium + Premium).",
            "capital_source": "400.000 USD",
            "revenue_goal": "1.000.000 USD",
            "member_count": 7,
            "deployment_location": "Đà Nẵng",
            "website_url": "https://edulearn.vn",
        },
        {
            "founder_email": "hoanghoainam.founder@startupkit.vn",
            "name": "LogiSmart Green",
            "tagline": "Tối ưu hóa tuyến đường giao hàng chặng cuối và cắt giảm 25% phát thải CO2 trong vận tải",
            "description": "Hệ thống thuật toán điều phối thông minh giúp các đội xe tải và shipper giao hàng nhanh hơn 30%, ghép đơn hàng tối ưu và theo dõi chỉ số carbon xanh đạt chuẩn xuất khẩu ESG.",
            "logo_url": "https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?w=300",
            "team_image": {"url": "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=800"},
            "stage": ProjectStage.NGHIEN_CUU_THI_TRUONG,
            "industry": "Vận tải & Logistics",
            "pain_point": "Xe chạy rỗng chiều về chiếm 40%, tắc đường đô thị làm tăng vọt chi phí nhiên liệu.",
            "solution": "Thuật toán tìm đường đa điểm tối ưu kết hợp dự báo lưu lượng giao thông thời gian thực.",
            "product": "Hệ thống Quản lý Vận tải Vận hành Đám mây (TMS) và Ứng dụng Tài xế.",
            "customer_segment": "Các công ty 3PL, chủ xe tải tư nhân và các chuỗi siêu thị bán lẻ.",
            "market_size": "800 triệu USD thị trường phần mềm Logistics Việt Nam.",
            "market_area": "Bình Dương, Đồng Nai, TP.HCM",
            "business_model": "Thu phí hoa hồng trên mỗi chuyến xe ghép thành công và gói bản quyền phần mềm.",
            "capital_source": "350.000 USD",
            "revenue_goal": "800.000 USD",
            "member_count": 6,
            "deployment_location": "Bình Dương",
            "website_url": "https://logismartgreen.vn",
        },
        {
            "founder_email": "dangquanghuy.founder@startupkit.vn",
            "name": "CyberSafe Shield",
            "tagline": "Bức tường lửa AI ngăn chặn tấn công Ransomware và rò rỉ dữ liệu doanh nghiệp thời gian thực",
            "description": "CyberSafe Shield giám sát liên tục lưu lượng mạng nội bộ, phân tích hành vi đáng ngờ và tự động cô lập máy tính nhiễm mã độc trong vòng 0.3 giây trước khi ransomware kịp mã hóa dữ liệu.",
            "logo_url": "https://images.unsplash.com/photo-1563986768609-322da13575f3?w=300",
            "team_image": {"url": "https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=800"},
            "stage": ProjectStage.HOAN_THIEN_SAN_PHAM,
            "industry": "An toàn thông tin & An ninh mạng",
            "pain_point": "Tấn công mã độc tống tiền tăng 150% mỗi năm, gây thiệt hại hàng triệu đô la cho doanh nghiệp.",
            "solution": "Cơ chế cách ly Zero-Trust tự động và khôi phục snapshot dữ liệu nguyên bản tức thì.",
            "product": "Agent phần mềm cài đặt máy trạm và bảng điều khiển SOC tập trung.",
            "customer_segment": "Ngân hàng, sàn thương mại điện tử, công ty bảo hiểm và doanh nghiệp chuyển đổi số.",
            "market_size": "2.5 tỷ USD thị trường an ninh mạng khu vực ASEAN.",
            "market_area": "Toàn quốc & Khu vực Đông Nam Á",
            "business_model": "Bán license theo số lượng Endpoint thiết bị bảo vệ mỗi tháng.",
            "capital_source": "900.000 USD",
            "revenue_goal": "2.500.000 USD",
            "member_count": 9,
            "deployment_location": "Hà Nội",
            "website_url": "https://cybersafeshield.com",
        },
        {
            "founder_email": "nguyenngoclan.founder@startupkit.vn",
            "name": "ReGreen Pack",
            "tagline": "Bao bì sinh học tự hủy hoàn toàn 100% từ phụ phẩm bã mía và xơ dừa Bến Tre",
            "description": "ReGreen Pack tận dụng hàng ngàn tấn bã mía và vỏ dừa bị đốt bỏ để sản xuất hộp cơm, ly nước và màng bọc thực phẩm tự phân hủy sinh học trong đất chỉ sau 90 ngày.",
            "logo_url": "https://images.unsplash.com/photo-1532996122724-e3c354a0b15b?w=300",
            "team_image": {"url": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=800"},
            "stage": ProjectStage.LAUNCH,
            "industry": "Công nghệ xanh & Môi trường",
            "pain_point": "Rác thải nhựa một lần hủy hoại môi trường, các thị trường phát triển siết chặt rào cản thuế nhựa.",
            "solution": "Công nghệ ép nhiệt xơ thực vật không chứa hóa chất độc hại, chống thấm dầu mỡ tự nhiên.",
            "product": "Dòng sản phẩm hộp thực phẩm ReGreen EcoBox và túi màng sinh học ReBio.",
            "customer_segment": "Chuỗi nhà hàng F&B, chuỗi cà phê, khách sạn và các đơn vị xuất khẩu nông sản.",
            "market_size": "600 triệu USD thị trường bao bì sinh học thay thế nhựa.",
            "market_area": "Bến Tre, TP.HCM, xuất khẩu sang Nhật Bản & EU",
            "business_model": "Sản xuất và phân phối trực tiếp B2B theo đơn đặt hàng lớn.",
            "capital_source": "600.000 USD",
            "revenue_goal": "1.800.000 USD",
            "member_count": 11,
            "deployment_location": "Bến Tre",
            "website_url": "https://regreenpack.vn",
        },
        {
            "founder_email": "vutuananh.founder@startupkit.vn",
            "name": "WorkPulse SaaS",
            "tagline": "Nền tảng số hóa quy trình phê duyệt nội bộ và đo lường hiệu suất nhân sự linh hoạt",
            "description": "WorkPulse thay thế toàn bộ giấy tờ, hóa đơn thủ công và bảng chấm công truyền thống bằng quy trình No-Code kéo thả trực quan, tích hợp chấm công bằng định vị GPS và nhận diện khuôn mặt bảo mật.",
            "logo_url": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=300",
            "team_image": {"url": "https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=800"},
            "stage": ProjectStage.Y_TUONG,
            "industry": "Phần mềm doanh nghiệp (SaaS)",
            "pain_point": "Nhân sự làm việc hybrid khó quản lý tiến độ, phê duyệt hợp đồng mất nhiều ngày qua giấy tờ.",
            "solution": "Trợ lý số phê duyệt tức thì qua ứng dụng và tích hợp kết nối Telegram/Slack/Zalo.",
            "product": "Ứng dụng WorkPulse All-In-One Workspace.",
            "customer_segment": "Các công ty công nghệ, đơn vị agency tiếp thị và chuỗi bán lẻ đa chi nhánh.",
            "market_size": "400 triệu USD thị trường phần mềm quản trị doanh nghiệp.",
            "market_area": "Toàn quốc",
            "business_model": "Thu phí từ 30.000 VNĐ/nhân sự/tháng.",
            "capital_source": "200.000 USD",
            "revenue_goal": "500.000 USD",
            "member_count": 5,
            "deployment_location": "TP. Hồ Chí Minh",
            "website_url": "https://workpulse.app",
        },
    ]

    created_projects = []
    now = datetime.datetime.utcnow()

    for p_info in projects_data:
        existing_p = db.query(Project).filter(Project.name == p_info["name"]).first()
        founder = created_users.get(p_info["founder_email"])
        if not founder:
            continue

        if not existing_p:
            p = Project(
                founder_id=founder.id,
                name=p_info["name"],
                tagline=p_info["tagline"],
                description=p_info["description"],
                logo_url=p_info["logo_url"],
                team_image=p_info["team_image"],
                stage=p_info["stage"],
                industry=p_info["industry"],
                pain_point=p_info["pain_point"],
                solution=p_info["solution"],
                product=p_info["product"],
                customer_segment=p_info["customer_segment"],
                market_size=p_info["market_size"],
                market_area=p_info["market_area"],
                business_model=p_info["business_model"],
                capital_source=p_info["capital_source"],
                revenue_goal=p_info["revenue_goal"],
                member_count=p_info["member_count"],
                deployment_location=p_info["deployment_location"],
                website_url=p_info["website_url"],
                profile_url=f"/projects/{p_info['name'].lower().replace(' ', '-')}",
                status="published",
                published_at=now,
                published_by=founder.id,
                current_stage=p_info["stage"].value if hasattr(p_info["stage"], "value") else str(p_info["stage"]),
                current_stage_label="Đang hoạt động sôi nổi",
                stages=[
                    {"key": "y-tuong", "title": "Hình thành ý tưởng", "status": "completed"},
                    {"key": "prototype", "title": "Phát triển MVP", "status": "completed"},
                    {"key": "beta", "title": "Thử nghiệm khách hàng", "status": "completed"},
                    {"key": "launch", "title": "Mở rộng thị trường", "status": "in_progress"},
                ]
            )
            db.add(p)
            db.flush()
            created_projects.append(p)
        else:
            created_projects.append(existing_p)

    # 4. Seed Project Posts (Diễn đàn & Cập nhật dự án)
    posts_data = [
        {
            "project_name": "EcoFarm IoT",
            "author_email": "nguyenvanan.founder@startupkit.vn",
            "title": "EcoFarm chính thức hoàn thành triển khai cho 120 nông trại sầu riêng tại Lâm Đồng!",
            "body": "Tin vui đầu năm từ đội ngũ EcoFarm IoT! Sau 6 tháng thử nghiệm thực địa, hệ thống cảm biến thông minh của chúng tôi đã chứng minh khả năng tiết kiệm trung bình 42% lượng nước ngọt tưới tiêu và giảm thiểu 15% sâu bệnh hại rễ. Xin gửi lời cảm ơn chân thành đến các mentor và bà con nông dân đã tin tưởng đồng hành cùng EcoFarm!",
            "comments": [
                {
                    "author_email": "shark.hung@venture.vn",
                    "content": "Chúc mừng An và đội ngũ EcoFarm! Một giải pháp thực tế giải quyết bài toán cốt lõi của nông nghiệp xuất khẩu. Cen Group rất quan tâm và sẵn sàng kết nối mô hình này vào chuỗi trang trại sinh thái đối tác."
                },
                {
                    "author_email": "nguyenhuuhai.mentor@gmail.com",
                    "content": "Kết quả ấn tượng! Nhớ chú ý chuẩn hóa các sensor thu thập dữ liệu độ ẩm đất để sau này huấn luyện mô hình dự báo sâu bệnh chính xác hơn nhé."
                }
            ]
        },
        {
            "project_name": "MediAI Vision",
            "author_email": "lethibich.founder@startupkit.vn",
            "title": "MediAI đạt chứng nhận thử nghiệm lâm sàng tại Bệnh viện Đa khoa và chuẩn bị gọi vốn Series A",
            "body": "Đội ngũ nghiên cứu MediAI Vision tự hào chia sẻ kết quả thử nghiệm mù kép trên 5.000 ca phim X-quang ngực: độ nhạy phát hiện u phổi giai đoạn sớm đạt 96.8%. Chúng tôi đang mở vòng đàm phán Series A (1.5M USD) để mở rộng sang các nước trong khu vực Đông Nam Á.",
            "comments": [
                {
                    "author_email": "lehanh@vinacapital.com",
                    "content": "Số liệu lâm sàng rất hứa hẹn! Đội ngũ VinaCapital Ventures muốn sắp xếp một buổi thảo luận chi tiết với Bích trong tuần này nhé."
                }
            ]
        },
        {
            "project_name": "FinFlow Core",
            "author_email": "tranminhduc.founder@startupkit.vn",
            "title": "[Góc tuyển dụng] FinFlow Core tìm kiếm Lead React Frontend & Senior AI Engineer",
            "body": "Để đáp ứng tốc độ tăng trưởng 2.500 doanh nghiệp SMEs sử dụng trong Q1/2026, FinFlow đang mở rộng đội ngũ kỹ thuật tại TP.HCM. Chế độ đãi ngộ cạnh tranh, ESOP hấp dẫn và văn hóa làm việc linh hoạt, tôn trọng sáng tạo.",
            "comments": [
                {
                    "author_email": "vuongquangkhai.mentor@gmail.com",
                    "content": "Startup FinFlow đang scale rất tốt. Bạn nào làm Frontend hoặc AI muốn thử thách môi trường fintech thực chiến thì nên ứng tuyển nhé!"
                }
            ]
        },
        {
            "project_name": "ReGreen Pack",
            "author_email": "nguyenngoclan.founder@startupkit.vn",
            "title": "Hành trình đưa bã mía xơ dừa Bến Tre trở thành hộp thực phẩm xuất khẩu sang thị trường Nhật Bản",
            "body": "Từ đống phế phẩm nông nghiệp bị đốt bỏ gây ô nhiễm khói bụi, ReGreen Pack đã hoàn thiện quy trình ép nhiệt không keo dán độc hại. Đến nay chúng tôi đã xuất khẩu lô hàng container đầu tiên sang thị trường khó tính Nhật Bản, mở ra cơ hội lớn cho kinh tế tuần hoàn tại ĐBSCL.",
            "comments": [
                {
                    "author_email": "shark.lien@vass.com.vn",
                    "content": "Rất tự hào về các bạn trẻ dám dấn thân làm nông nghiệp sạch và kinh tế xanh! Quỹ Môi trường Xanh sẵn sàng tài trợ một phần chi phí R&D máy ép thế hệ mới cho ReGreen."
                }
            ]
        },
    ]

    for post_info in posts_data:
        p = db.query(Project).filter(Project.name == post_info["project_name"]).first()
        author = created_users.get(post_info["author_email"])
        if not p or not author:
            continue

        existing_post = db.query(ProjectPost).filter(
            ProjectPost.project_id == p.id,
            ProjectPost.title == post_info["title"]
        ).first()

        if not existing_post:
            post = ProjectPost(
                project_id=p.id,
                author_id=author.id,
                title=post_info["title"],
                body=post_info["body"],
                visibility="public",
                created_at=now,
                updated_at=now
            )
            db.add(post)
            db.flush()

            # Add Likes
            for voter in list(created_users.values())[:3]:
                db.add(PostLike(post_id=post.id, user_id=voter.id))

            # Add Comments
            for c_info in post_info.get("comments", []):
                c_author = created_users.get(c_info["author_email"])
                if c_author:
                    comment = PostComment(
                        post_id=post.id,
                        author_id=c_author.id,
                        body=c_info["content"],
                        created_at=now
                    )
                    db.add(comment)

    db.commit()
    logger.info("Database seeded successfully with rich Vietnam startup ecosystem data!")

def seed_database_if_empty():
    db = SessionLocal()
    try:
        project_count = db.query(Project).count()
        if project_count == 0:
            logger.info("Database is empty. Populating initial seed data...")
            seed_database(db)
        else:
            logger.info("Database already contains %d projects. Skipping seed.", project_count)
    except Exception as e:
        logger.warning("Error during seed_database_if_empty: %s", e)
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
        print("Manual seed executed successfully!")
    finally:
        db.close()
