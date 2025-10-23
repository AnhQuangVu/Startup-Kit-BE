"""
AI Prompts cho việc tạo và gợi ý nội dung dự án
"""

DESCRIPTION_TO_FULL_PROJECT_PROMPT = """
Bạn là một chuyên gia tư vấn khởi nghiệp và đầu tư. Nhiệm vụ của bạn là giúp người dùng phát triển ý tưởng dự án thành một hồ sơ đầy đủ.

Dựa trên mô tả dự án sau đây, hãy tạo ra một hồ sơ dự án hoàn chỉnh bao gồm:

Mô tả dự án từ người dùng:
{description}

Hãy tạo ra JSON response với các trường sau (tất cả đều là string hoặc int, trả về null nếu không có thông tin):
{{
    "name": "Tên dự án gợi ý",
    "tagline": "Slogan/câu giới thiệu ngắn gọn",
    "industry": "Ngành/lĩnh vực (VD: Fintech, EdTech, HealthTech)",
    "pain_point": "Vấn đề/nỗi đau mà dự án giải quyết",
    "solution": "Giải pháp đề xuất",
    "product": "Sản phẩm/dịch vụ cụ thể",
    "customer_segment": "Phân khúc khách hàng mục tiêu",
    "customer_features": "Đặc điểm khách hàng",
    "market_size": "Quy mô thị trường (ước lượng)",
    "market_area": "Khu vực thị trường",
    "business_model": "Mô hình kinh doanh",
    "revenue_method": "Phương thức tạo doanh thu",
    "distribution_channel": "Kênh phân phối",
    "partners": "Đối tác tiềm năng",
    "cost_estimate": "Ước lượng chi phí (VD: 100M - 500M VND)",
    "capital_source": "Nguồn vốn đề xuất",
    "revenue_goal": "Mục tiêu doanh thu (năm 1-3)",
    "member_count": 5,
    "member_skills": "Kỹ năng cần thiết cho team",
    "resources": "Nguồn lực cần thiết",
    "deployment_location": "Địa điểm triển khai"
}}

Hãy đưa ra các gợi ý cụ thể, thực tế và khả thi cho thị trường Việt Nam.
"""

BMC_GENERATION_PROMPT = """
Dựa trên thông tin dự án sau, hãy tạo Business Model Canvas (BMC) chi tiết:

Thông tin dự án:
{project_info}

Hãy tạo JSON array với 9 blocks của BMC:
[
    {{"block": "Key Partners", "value": "Mô tả đối tác chính"}},
    {{"block": "Key Activities", "value": "Hoạt động chính"}},
    {{"block": "Key Resources", "value": "Nguồn lực chính"}},
    {{"block": "Value Propositions", "value": "Giá trị cốt lõi"}},
    {{"block": "Customer Relationships", "value": "Quan hệ khách hàng"}},
    {{"block": "Channels", "value": "Kênh tiếp cận"}},
    {{"block": "Customer Segments", "value": "Phân khúc khách hàng"}},
    {{"block": "Cost Structure", "value": "Cơ cấu chi phí"}},
    {{"block": "Revenue Streams", "value": "Nguồn thu"}}
]
"""

FINANCIAL_PLAN_PROMPT = """
Tạo kế hoạch tài chính chi tiết cho dự án sau:

Thông tin dự án:
{project_info}

Hãy tạo JSON object với cấu trúc:
{{
    "startup_costs": {{
        "initial_investment": "Vốn đầu tư ban đầu",
        "breakdown": [
            {{"item": "Tên khoản chi", "amount": "Số tiền"}},
        ]
    }},
    "operating_costs": {{
        "monthly": "Chi phí vận hành hàng tháng",
        "breakdown": [
            {{"item": "Tên khoản chi", "amount": "Số tiền"}},
        ]
    }},
    "revenue_projection": {{
        "year1": "Doanh thu năm 1",
        "year2": "Doanh thu năm 2",
        "year3": "Doanh thu năm 3",
        "assumptions": "Các giả định"
    }},
    "funding_needs": {{
        "total": "Tổng vốn cần thiết",
        "sources": [
            {{"source": "Nguồn vốn", "amount": "Số tiền", "percentage": "Tỷ lệ"}},
        ]
    }},
    "breakeven_analysis": "Phân tích hòa vốn"
}}
"""

MARKET_RESEARCH_PROMPT = """
Tạo báo cáo nghiên cứu thị trường cho dự án:

Thông tin dự án:
{project_info}

Hãy tạo JSON object:
{{
    "market_overview": "Tổng quan thị trường",
    "market_size": "Quy mô thị trường",
    "market_trends": ["Xu hướng 1", "Xu hướng 2"],
    "target_audience": {{
        "demographics": "Đặc điểm nhân khẩu học",
        "behaviors": "Hành vi tiêu dùng",
        "pain_points": "Nỗi đau của khách hàng"
    }},
    "competitors": [
        {{"name": "Đối thủ", "strengths": "Điểm mạnh", "weaknesses": "Điểm yếu"}},
    ],
    "opportunities": ["Cơ hội 1", "Cơ hội 2"],
    "threats": ["Thách thức 1", "Thách thức 2"],
    "competitive_advantage": "Lợi thế cạnh tranh của dự án"
}}
"""

GTM_STRATEGY_PROMPT = """
Tạo chiến lược Go-to-Market cho dự án:

Thông tin dự án:
{project_info}

Hãy tạo JSON object:
{{
    "target_market": "Thị trường mục tiêu",
    "positioning": "Định vị sản phẩm",
    "launch_phases": [
        {{
            "phase": "Giai đoạn",
            "timeline": "Thời gian",
            "objectives": ["Mục tiêu 1", "Mục tiêu 2"],
            "activities": ["Hoạt động 1", "Hoạt động 2"]
        }},
    ],
    "marketing_channels": [
        {{"channel": "Kênh marketing", "budget": "Ngân sách", "expected_roi": "ROI dự kiến"}},
    ],
    "sales_strategy": "Chiến lược bán hàng",
    "customer_acquisition": {{
        "strategy": "Chiến lược thu hút khách hàng",
        "cost_per_acquisition": "Chi phí/khách hàng",
        "conversion_rate": "Tỷ lệ chuyển đổi"
    }},
    "milestones": [
        {{"milestone": "Mốc quan trọng", "target_date": "Thời gian dự kiến"}},
    ]
}}
"""

SUGGESTION_PROMPT = """
Bạn là một trợ lý AI thông minh giúp hoàn thiện nội dung dự án.

Người dùng đang nhập nội dung cho trường: {field_name}
Nội dung hiện tại: {current_text}

Thông tin dự án đã có:
{project_context}

Hãy đưa ra 3 gợi ý hoàn thiện cho nội dung này. Mỗi gợi ý nên:
- Phù hợp với ngữ cảnh dự án
- Cụ thể và thực tế
- Dài khoảng 1-3 câu

Trả về JSON array:
[
    {{"suggestion": "Gợi ý 1", "confidence": 0.9}},
    {{"suggestion": "Gợi ý 2", "confidence": 0.85}},
    {{"suggestion": "Gợi ý 3", "confidence": 0.8}}
]
"""

AUTOCOMPLETE_PROMPT = """
Bạn là một trợ lý AI autocomplete cho việc tạo hồ sơ dự án.

Người dùng đang nhập vào trường: {field_name}
Văn bản hiện tại: "{current_text}"

Ngữ cảnh dự án:
{project_context}

Hãy hoàn thiện câu/đoạn văn này một cách tự nhiên và phù hợp. Chỉ trả về phần văn bản cần bổ sung (không lặp lại phần đã có).

Trả về JSON:
{{
    "completion": "Phần văn bản hoàn thiện",
    "full_text": "Toàn bộ văn bản sau khi hoàn thiện"
}}
"""
