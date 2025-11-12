from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# Request schemas
class AIGenerateProjectRequest(BaseModel):
    """Request để generate toàn bộ project từ mô tả"""
    description: str = Field(..., min_length=10, description="Mô tả dự án từ người dùng")

class AISuggestionRequest(BaseModel):
    """Request để lấy gợi ý cho một trường cụ thể"""
    field_name: str = Field(..., description="Tên trường đang nhập (VD: 'pain_point', 'solution')")
    current_text: str = Field(..., description="Văn bản hiện tại người dùng đã nhập")
    project_id: Optional[int] = Field(None, description="ID dự án (nếu đang edit)")
    project_context: Optional[Dict[str, Any]] = Field(None, description="Thông tin dự án hiện tại")

class AIAutocompleteRequest(BaseModel):
    """Request để autocomplete văn bản"""
    field_name: str = Field(..., description="Tên trường đang nhập")
    current_text: str = Field(..., description="Văn bản hiện tại")
    project_context: Optional[Dict[str, Any]] = Field(None, description="Thông tin dự án")

class AIGenerateSectionRequest(BaseModel):
    """Request để generate một section cụ thể (BMC, Financial, etc.)"""
    section_type: str = Field(..., description="Loại section: BMC, FINANCIAL, MARKET_RESEARCH, GTM_STRATEGY")
    project_id: int = Field(..., description="ID của dự án")

class AIEnhanceTextRequest(BaseModel):
    """Request để cải thiện văn bản"""
    text: str = Field(..., description="Văn bản cần cải thiện")
    context: Optional[str] = Field(None, description="Ngữ cảnh")

# Response schemas
class AISuggestion(BaseModel):
    """Một gợi ý từ AI"""
    suggestion: str
    confidence: float = Field(..., ge=0, le=1, description="Độ tin cậy của gợi ý (0-1)")

class AISuggestionResponse(BaseModel):
    """Response chứa danh sách gợi ý"""
    suggestions: List[AISuggestion]

class AIAutocompleteResponse(BaseModel):
    """Response cho autocomplete"""
    completion: str = Field(..., description="Phần văn bản được bổ sung")
    full_text: str = Field(..., description="Toàn bộ văn bản sau khi hoàn thiện")

class AIGeneratedProject(BaseModel):
    """Dữ liệu dự án được AI generate"""
    name: Optional[str] = None
    tagline: Optional[str] = None
    industry: Optional[str] = None
    pain_point: Optional[str] = None
    solution: Optional[str] = None
    product: Optional[str] = None
    customer_segment: Optional[str] = None
    customer_features: Optional[str] = None
    market_size: Optional[str] = None
    market_area: Optional[str] = None
    business_model: Optional[str] = None
    revenue_method: Optional[str] = None
    distribution_channel: Optional[str] = None
    partners: Optional[str] = None
    cost_estimate: Optional[str] = None
    capital_source: Optional[str] = None
    revenue_goal: Optional[str] = None
    member_count: Optional[int] = None
    member_skills: Optional[str] = None
    resources: Optional[str] = None
    deployment_location: Optional[str] = None

class AIBMCBlock(BaseModel):
    """Một block trong Business Model Canvas"""
    block: str
    value: str

class AIBMCResponse(BaseModel):
    """Response cho BMC generation"""
    bmc: List[AIBMCBlock]

class AIFinancialBreakdown(BaseModel):
    """Chi tiết một khoản chi phí hoặc doanh thu"""
    item: str
    amount: str

class AIFinancialStartupCosts(BaseModel):
    """Chi phí khởi nghiệp"""
    initial_investment: str
    breakdown: List[AIFinancialBreakdown]

class AIFinancialOperatingCosts(BaseModel):
    """Chi phí vận hành"""
    monthly: str
    breakdown: List[AIFinancialBreakdown]

class AIFinancialRevenueProjection(BaseModel):
    """Dự báo doanh thu"""
    year1: str
    year2: str
    year3: str
    assumptions: str

class AIFundingSource(BaseModel):
    """Nguồn vốn"""
    source: str
    amount: str
    percentage: str

class AIFundingNeeds(BaseModel):
    """Nhu cầu vốn"""
    total: str
    sources: List[AIFundingSource]

class AIFinancialPlanResponse(BaseModel):
    """Response cho financial plan generation"""
    startup_costs: AIFinancialStartupCosts
    operating_costs: AIFinancialOperatingCosts
    revenue_projection: AIFinancialRevenueProjection
    funding_needs: AIFundingNeeds
    breakeven_analysis: str

class AICompetitor(BaseModel):
    """Thông tin đối thủ cạnh tranh"""
    name: str
    strengths: str
    weaknesses: str

class AITargetAudience(BaseModel):
    """Đối tượng mục tiêu"""
    demographics: str
    behaviors: str
    pain_points: str

class AIMarketResearchResponse(BaseModel):
    """Response cho market research generation"""
    market_overview: str
    market_size: str
    market_trends: List[str]
    target_audience: AITargetAudience
    competitors: List[AICompetitor]
    opportunities: List[str]
    threats: List[str]
    competitive_advantage: str

class AILaunchPhase(BaseModel):
    """Giai đoạn launch"""
    phase: str
    timeline: str
    objectives: List[str]
    activities: List[str]

class AIMarketingChannel(BaseModel):
    """Kênh marketing"""
    channel: str
    budget: str
    expected_roi: str

class AICustomerAcquisition(BaseModel):
    """Chiến lược thu hút khách hàng"""
    strategy: str
    cost_per_acquisition: str
    conversion_rate: str

class AIMilestone(BaseModel):
    """Mốc quan trọng"""
    milestone: str
    target_date: str

class AIGTMStrategyResponse(BaseModel):
    """Response cho GTM strategy generation"""
    target_market: str
    positioning: str
    launch_phases: List[AILaunchPhase]
    marketing_channels: List[AIMarketingChannel]
    sales_strategy: str
    customer_acquisition: AICustomerAcquisition
    milestones: List[AIMilestone]

class AIEnhanceTextResponse(BaseModel):
    """Response cho text enhancement"""
    original: str
    enhanced: str
    improvements: List[str]


# --- RAG Schemas ---
class DocumentUploadResponse(BaseModel):
    """Response khi upload document"""
    id: int
    filename: str
    file_type: str
    file_size: int
    is_processed: bool
    chunks_created: int
    message: str


class DocumentRead(BaseModel):
    """Schema để đọc document"""
    id: int
    filename: str
    file_type: str
    file_size: int
    uploaded_by: int
    project_id: Optional[int]
    content_preview: Optional[str]
    is_processed: bool
    created_at: Any
    
    class Config:
        from_attributes = True


class RAGChatRequest(BaseModel):
    """Request cho RAG chat"""
    message: str = Field(..., min_length=1, description="Tin nhắn từ người dùng")
    project_id: Optional[int] = Field(None, description="ID project để lọc documents")
    use_google: bool = Field(True, description="Có sử dụng Google search không")
    conversation_history: Optional[List[Dict[str, str]]] = Field(
        None, 
        description="Lịch sử hội thoại [{'role': 'user/assistant', 'content': '...'}]"
    )


class RAGChatResponse(BaseModel):
    """Response từ RAG chat"""
    answer: str = Field(..., description="Câu trả lời từ AI")
    sources: Dict[str, Any] = Field(..., description="Thông tin về nguồn dữ liệu")
    context_used: Dict[str, bool] = Field(..., description="Context nào đã được sử dụng")


class RAGQuestionRequest(BaseModel):
    """Request để hỏi đáp đơn giản"""
    question: str = Field(..., min_length=1, description="Câu hỏi")
    project_id: Optional[int] = Field(None, description="ID project")
    use_google: bool = Field(True, description="Sử dụng Google search")


class VectorStoreStatsResponse(BaseModel):
    """Response thống kê vector store"""
    total_vectors: int
    dimension: int
    unique_documents: int
    unique_projects: int


class AIGenerateDescriptionRequest(BaseModel):
    """Request để AI sinh mô tả startup profile với validation bảo mật"""
    name: Optional[str] = Field(None, max_length=200, description="Tên startup hoặc dự án")
    industry: Optional[str] = Field(None, max_length=150, description="Ngành nghề / lĩnh vực")
    target_audience: Optional[str] = Field(None, max_length=300, description="Khách hàng mục tiêu")
    key_features: Optional[str] = Field(None, max_length=1500, description="Điểm nổi bật / giải pháp chính")
    tone: Optional[str] = Field("chuyên nghiệp, thu hút nhà đầu tư", max_length=100, description="Văn phong / phong cách")
    current_description: Optional[str] = Field(None, max_length=3000, description="Mô tả hiện tại nếu muốn cải thiện")
    project_id: Optional[int] = Field(None, description="ID dự án nếu muốn lấy ngữ cảnh tự động")


class AIGenerateDescriptionResponse(BaseModel):
    """Response chứa mô tả startup do AI sinh ra"""
    description: str = Field(..., description="Mô tả chi tiết startup profile")
    short_pitch: Optional[str] = Field(None, description="Elevator pitch ngắn gọn 1-2 câu")
    tagline: Optional[str] = Field(None, description="Slogan / Tagline bắt tai")
    suggested_tags: Optional[List[str]] = Field(default_factory=list, description="Từ khóa / tags gợi ý")
