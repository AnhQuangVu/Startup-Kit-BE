"""
AI Service để tương tác với OpenAI API
"""
import json
from typing import Dict, Any, Optional, List
from openai import OpenAI
from src.core.config import settings
from . import prompts
from . import schemas

class AIService:
    """Service xử lý các tác vụ AI"""
    
    def __init__(self):
        """Khởi tạo OpenAI client an toàn, không crash app nếu API_KEY chưa được cấu hình lúc startup"""
        self.client = None
        if settings.API_KEY and settings.API_KEY != "your_openai_api_key_here":
            try:
                self.client = OpenAI(
                    api_key=settings.API_KEY,
                    base_url=settings.BASE_URL
                )
            except Exception as e:
                print(f"[Warning] Khởi tạo OpenAI client thất bại: {e}")
        self.model = settings.LLM_MODEL or "gpt-4o-mini"
    
    def _call_openai(self, prompt: str, temperature: float = 0.7) -> str:
        """
        Gọi OpenAI API với prompt an toàn
        """
        try:
            if not self.client:
                if settings.API_KEY and settings.API_KEY != "your_openai_api_key_here":
                    self.client = OpenAI(api_key=settings.API_KEY, base_url=settings.BASE_URL)
                else:
                    raise ValueError("Chưa cấu hình API_KEY hợp lệ trong file .env cho dịch vụ AI")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant for startup project creation. Always respond in Vietnamese. Return valid JSON when requested."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                response_format={"type": "json_object"},
                timeout=30.0
            )
            return response.choices[0].message.content
        except Exception as e:
            err_msg = str(e)
            if "quota" in err_msg.lower() or "429" in err_msg:
                raise Exception("Tài khoản OpenAI đã hết hạn mức (quota) hoặc bị giới hạn tần suất. Vui lòng kiểm tra lại gói API.")
            elif "authentication" in err_msg.lower() or "401" in err_msg:
                raise Exception("Khóa API_KEY không hợp lệ hoặc đã hết hạn.")
            raise Exception(f"Lỗi khi gọi AI API: {err_msg}")
    
    def generate_project_from_description(self, description: str) -> schemas.AIGeneratedProject:
        """
        Tạo toàn bộ thông tin dự án từ mô tả
        
        Args:
            description: Mô tả dự án từ người dùng
            
        Returns:
            AIGeneratedProject với đầy đủ thông tin
        """
        prompt = prompts.DESCRIPTION_TO_FULL_PROJECT_PROMPT.format(
            description=description
        )
        
        response_text = self._call_openai(prompt, temperature=0.8)
        
        try:
            response_data = json.loads(response_text)
            return schemas.AIGeneratedProject(**response_data)
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse AI response: {str(e)}")
    
    def generate_suggestions(
        self, 
        field_name: str, 
        current_text: str, 
        project_context: Optional[Dict[str, Any]] = None
    ) -> List[schemas.AISuggestion]:
        """
        Tạo gợi ý cho một trường cụ thể
        
        Args:
            field_name: Tên trường đang nhập
            current_text: Văn bản hiện tại
            project_context: Thông tin dự án đã có
            
        Returns:
            List của AISuggestion
        """
        context_str = json.dumps(project_context or {}, ensure_ascii=False, indent=2)
        
        prompt = prompts.SUGGESTION_PROMPT.format(
            field_name=field_name,
            current_text=current_text,
            project_context=context_str
        )
        
        response_text = self._call_openai(prompt, temperature=0.85)
        
        try:
            response_data = json.loads(response_text)
            # Response có thể là array trực tiếp hoặc wrapped trong object
            suggestions_data = response_data if isinstance(response_data, list) else response_data.get("suggestions", [])
            return [schemas.AISuggestion(**item) for item in suggestions_data]
        except (json.JSONDecodeError, KeyError) as e:
            raise Exception(f"Failed to parse suggestions: {str(e)}")
    
    def autocomplete_text(
        self,
        field_name: str,
        current_text: str,
        project_context: Optional[Dict[str, Any]] = None
    ) -> schemas.AIAutocompleteResponse:
        """
        Autocomplete văn bản cho trường
        
        Args:
            field_name: Tên trường
            current_text: Văn bản hiện tại
            project_context: Ngữ cảnh dự án
            
        Returns:
            AIAutocompleteResponse
        """
        context_str = json.dumps(project_context or {}, ensure_ascii=False, indent=2)
        
        prompt = prompts.AUTOCOMPLETE_PROMPT.format(
            field_name=field_name,
            current_text=current_text,
            project_context=context_str
        )
        
        response_text = self._call_openai(prompt, temperature=0.7)
        
        try:
            response_data = json.loads(response_text)
            return schemas.AIAutocompleteResponse(**response_data)
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse autocomplete response: {str(e)}")
    
    def generate_bmc(self, project_info: Dict[str, Any]) -> List[schemas.AIBMCBlock]:
        """
        Tạo Business Model Canvas
        
        Args:
            project_info: Thông tin dự án
            
        Returns:
            List của AIBMCBlock (9 blocks)
        """
        project_str = json.dumps(project_info, ensure_ascii=False, indent=2)
        
        prompt = prompts.BMC_GENERATION_PROMPT.format(
            project_info=project_str
        )
        
        response_text = self._call_openai(prompt, temperature=0.7)
        
        try:
            response_data = json.loads(response_text)
            bmc_data = response_data if isinstance(response_data, list) else response_data.get("bmc", [])
            return [schemas.AIBMCBlock(**item) for item in bmc_data]
        except (json.JSONDecodeError, KeyError) as e:
            raise Exception(f"Failed to parse BMC: {str(e)}")
    
    def generate_financial_plan(self, project_info: Dict[str, Any]) -> schemas.AIFinancialPlanResponse:
        """
        Tạo kế hoạch tài chính
        
        Args:
            project_info: Thông tin dự án
            
        Returns:
            AIFinancialPlanResponse
        """
        project_str = json.dumps(project_info, ensure_ascii=False, indent=2)
        
        prompt = prompts.FINANCIAL_PLAN_PROMPT.format(
            project_info=project_str
        )
        
        response_text = self._call_openai(prompt, temperature=0.6)
        
        try:
            response_data = json.loads(response_text)
            return schemas.AIFinancialPlanResponse(**response_data)
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse financial plan: {str(e)}")
    
    def generate_market_research(self, project_info: Dict[str, Any]) -> schemas.AIMarketResearchResponse:
        """
        Tạo nghiên cứu thị trường
        
        Args:
            project_info: Thông tin dự án
            
        Returns:
            AIMarketResearchResponse
        """
        project_str = json.dumps(project_info, ensure_ascii=False, indent=2)
        
        prompt = prompts.MARKET_RESEARCH_PROMPT.format(
            project_info=project_str
        )
        
        response_text = self._call_openai(prompt, temperature=0.7)
        
        try:
            response_data = json.loads(response_text)
            return schemas.AIMarketResearchResponse(**response_data)
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse market research: {str(e)}")
    
    def generate_gtm_strategy(self, project_info: Dict[str, Any]) -> schemas.AIGTMStrategyResponse:
        """
        Tạo chiến lược Go-to-Market
        
        Args:
            project_info: Thông tin dự án
            
        Returns:
            AIGTMStrategyResponse
        """
        project_str = json.dumps(project_info, ensure_ascii=False, indent=2)
        
        prompt = prompts.GTM_STRATEGY_PROMPT.format(
            project_info=project_str
        )
        
        response_text = self._call_openai(prompt, temperature=0.7)
        
        try:
            response_data = json.loads(response_text)
            return schemas.AIGTMStrategyResponse(**response_data)
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse GTM strategy: {str(e)}")
    
    def enhance_text(self, text: str, context: Optional[str] = None) -> schemas.AIEnhanceTextResponse:
        """
        Cải thiện văn bản
        
        Args:
            text: Văn bản cần cải thiện
            context: Ngữ cảnh (optional)
            
        Returns:
            AIEnhanceTextResponse
        """
        context_str = f"\nNgữ cảnh: {context}" if context else ""
        
        prompt = f"""
Hãy cải thiện văn bản sau để nó chuyên nghiệp và rõ ràng hơn:{context_str}

Văn bản gốc:
{text}

Trả về JSON:
{{
    "original": "Văn bản gốc",
    "enhanced": "Văn bản sau khi cải thiện",
    "improvements": ["Cải tiến 1", "Cải tiến 2"]
}}
"""
        
        response_text = self._call_openai(prompt, temperature=0.6)
        
        try:
            response_data = json.loads(response_text)
            return schemas.AIEnhanceTextResponse(**response_data)
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse enhancement response: {str(e)}")


    def generate_startup_description(
        self,
        name: Optional[str] = None,
        industry: Optional[str] = None,
        target_audience: Optional[str] = None,
        key_features: Optional[str] = None,
        tone: Optional[str] = None,
        current_description: Optional[str] = None,
    ) -> schemas.AIGenerateDescriptionResponse:
        """
        Sinh mô tả startup profile từ các thông tin cơ bản
        Tự động fallback sinh mô tả thông minh nếu chưa có API Key
        """
        # Nếu chưa cấu hình API_KEY, kích hoạt Smart Fallback Generator để hệ thống vẫn hoạt động mượt mà
        has_key = bool(settings.API_KEY and settings.API_KEY != "your_openai_api_key_here")
        if not has_key:
            clean_name = name or "Dự án Khởi nghiệp"
            clean_ind = industry or "Công nghệ & Đổi mới sáng tạo"
            clean_aud = target_audience or "người dùng và doanh nghiệp tại Việt Nam"
            clean_feat = key_features or "ứng dụng giải pháp số hóa để tối ưu hóa hiệu quả và trải nghiệm"

            fallback_desc = (
                f"{clean_name} là giải pháp tiên phong trong lĩnh vực {clean_ind}, "
                f"được xây dựng nhằm giải quyết các thách thức then chốt của {clean_aud}.\n\n"
                f"Với trọng tâm lấy người dùng làm trung tâm, dự án mang đến {clean_feat}. "
                f"Sản phẩm tạo nên giá trị vượt trội thông qua việc tiết kiệm thời gian, tối ưu hóa chi phí vận hành "
                f"và kiến tạo quy trình làm việc thông minh, hiện đại.\n\n"
                f"Tầm nhìn của {clean_name} là tiếp tục đổi mới sáng tạo, mở rộng quy mô thị trường "
                f"và trở thành nền tảng đáng tin cậy hàng đầu trong hệ sinh thái khởi nghiệp số."
            )
            fallback_pitch = f"{clean_name} - Giải pháp đột phá trong ngành {clean_ind} dành cho {clean_aud}."
            fallback_tagline = f"Đột phá tương lai cùng {clean_name}"
            fallback_tags = [clean_ind, "Khởi nghiệp", "Công nghệ", "Innovation"]

            return schemas.AIGenerateDescriptionResponse(
                description=fallback_desc,
                short_pitch=fallback_pitch,
                tagline=fallback_tagline,
                suggested_tags=fallback_tags
            )
        prompt = prompts.GENERATE_STARTUP_DESCRIPTION_PROMPT.format(
            name=name or "Chưa đặt tên",
            industry=industry or "Đa ngành",
            target_audience=target_audience or "Chưa xác định",
            key_features=key_features or "Giải pháp ứng dụng công nghệ đột phá",
            tone=tone or "chuyên nghiệp, thu hút nhà đầu tư",
            current_description=current_description or "Chưa có",
        )
        
        response_text = self._call_openai(prompt, temperature=0.75)
        
        try:
            clean_text = (response_text or "").strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            elif clean_text.startswith("```"):
                clean_text = clean_text[3:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]
            clean_text = clean_text.strip()

            response_data = json.loads(clean_text)
            
            # Đảm bảo tags luôn là list
            raw_tags = response_data.get("suggested_tags", [])
            if isinstance(raw_tags, str):
                suggested_tags = [t.strip() for t in raw_tags.split(",") if t.strip()]
            elif isinstance(raw_tags, list):
                suggested_tags = [str(t) for t in raw_tags]
            else:
                suggested_tags = []

            return schemas.AIGenerateDescriptionResponse(
                description=response_data.get("description", ""),
                short_pitch=response_data.get("short_pitch"),
                tagline=response_data.get("tagline"),
                suggested_tags=suggested_tags,
            )
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse AI description response: {str(e)}")


# Singleton instance
ai_service = AIService()
