from src.projects.schemas import ProjectCreate, ProjectRead, ProjectSectionRead
from src.projects.pdf_utils import create_project_pdf
from src.database.models import ProjectStage
from datetime import datetime
import os

# Tạo dữ liệu project mẫu
project_data = ProjectCreate(
    name="Dự án Khởi nghiệp A ",

    tagline="Giải pháp đổi mới cho thị trường Việt Nam",
    stage=ProjectStage.Y_TUONG,
    description="Đây là mô tả chi tiết về dự án khởi nghiệp A.",
    industry="Công nghệ",
    pain_point="Thiếu giải pháp quản lý hiệu quả.",
    solution="Ứng dụng AI để tối ưu hóa quy trình.",
    product="Phần mềm quản lý doanh nghiệp",
    customer_segment="Doanh nghiệp vừa và nhỏ",
    customer_features="Dễ sử dụng, chi phí thấp",
    market_size="100,000 doanh nghiệp",
    market_area="Toàn quốc",
    business_model="B2B",
    revenue_method="Thu phí theo tháng",
    distribution_channel="Online",
    partners="Công ty phần mềm B",
    cost_estimate="500 triệu VNĐ",
    capital_source="Nhà đầu tư thiên thần",
    revenue_goal="1 tỷ VNĐ/năm",
    member_count=5,
    member_skills="Lập trình, kinh doanh, marketing",
    resources="Máy chủ, phần mềm",
    deployment_location="Hà Nội",
    website_url="https://duanA.vn",
    use_ai=True
)

# Tạo section BMC dạng bảng
bmc_table = [
    {"block": "Problem", "value": "1) Doanh nghiệp vừa và nhỏ thiếu công cụ quản lý quy trình; 2) Chi phí hiện tại cao; 3) Thiếu tự động hoá báo cáo"},
    {"block": "Solution", "value": "Ứng dụng SaaS quản lý công việc + AI tự động hoá báo cáo và tối ưu hoá quy trình"},
    {"block": "Unique Value Proposition", "value": "Tiết kiệm 30% thời gian quản lý nhờ tự động hoá và gợi ý AI, phù hợp cho SME tại Việt Nam"},
    {"block": "Unfair Advantage", "value": "Mạng lưới đối tác triển khai, dữ liệu ngành riêng và mô hình AI được tinh chỉnh cho thị trường VN"},
    {"block": "Customer Segments", "value": "Doanh nghiệp vừa và nhỏ (nhóm B2B), đặc biệt: bán lẻ, dịch vụ, sản xuất quy mô nhỏ"},

    {"block": "Existing Alternatives", "value": "Excel + email, phần mềm CRM/ERP cồng kềnh, thuê tư vấn bên ngoài"},
    {"block": "Key Metrics", "value": "Tỷ lệ chuyển đổi dùng thử -> trả phí, thời gian triển khai trung bình, NPS"},
    {"block": "High-Level Concept", "value": "'Asana cho SME' với AI hỗ trợ tự động hoá quy trình"},
    {"block": "Channels", "value": "Bán hàng trực tiếp B2B, Mạng đối tác triển khai, Marketing nội dung và webinar"},
    {"block": "Early Adopters", "value": "Các doanh nghiệp bán lẻ chuỗi nhỏ, startups có 10-50 nhân sự"},

    {"block": "Cost Structure", "value": "Chi phí phát triển, máy chủ, marketing, sale, hỗ trợ khách hàng"},
    {"block": "Revenue Streams", "value": "Thu phí đăng ký theo người dùng / tháng, gói triển khai tích hợp một lần"},
]

bmc_section = ProjectSectionRead(
    id=1,
    type="BUSINESS_MODEL_CANVAS",
    title="Business Model Canvas (BMC)",
    content={"table": bmc_table},
    file_url=None,
    updated_at=datetime.now()
)

# Tạo project kiểu ProjectRead để truyền vào hàm PDF
project = ProjectRead(
    id=1,
    founder_id=1,
    name=project_data.name,
    tagline=project_data.tagline,
    stage=project_data.stage,
    description=project_data.description,
    logo_url=None,
    website_url=project_data.website_url,
    industry=project_data.industry,
    pain_point=project_data.pain_point,
    solution=project_data.solution,
    product=project_data.product,
    customer_segment=project_data.customer_segment,
    customer_features=project_data.customer_features,
    market_size=project_data.market_size,
    market_area=project_data.market_area,
    business_model=project_data.business_model,
    revenue_method=project_data.revenue_method,
    distribution_channel=project_data.distribution_channel,
    partners=project_data.partners,
    cost_estimate=project_data.cost_estimate,
    capital_source=project_data.capital_source,
    revenue_goal=project_data.revenue_goal,
    member_count=project_data.member_count,
    member_skills=project_data.member_skills,
    resources=project_data.resources,
    team_image_url=None,
    product_image_url=None,
    use_ai=project_data.use_ai,
    created_at=datetime.now(),
    updated_at=datetime.now(),
    sections=[bmc_section],
    is_deleted=False,
    deployment_location=project_data.deployment_location
)

# Tạo file PDF
output_path = os.path.abspath("project_demo.pdf")
watermark_path = os.path.abspath("static/logo.png")
create_project_pdf(project, output_path, watermark_path)
print(f"Đã tạo file PDF: {output_path}")
