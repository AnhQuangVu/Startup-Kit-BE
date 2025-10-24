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
        """Khởi tạo OpenAI client"""
        if not settings.API_KEY:
            raise ValueError("API_KEY not configured in settings")
        
        self.client = OpenAI(
            api_key=settings.API_KEY,
            base_url=settings.BASE_URL
        )
        self.model = settings.LLM_MODEL
    
    def _call_openai(self, prompt: str, temperature: float = 0.7) -> str:
        """
        Gọi OpenAI API với prompt
        
        Args:
            prompt: Prompt text
            temperature: Độ sáng tạo (0-1)
            
        Returns:
            Response text từ model
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant for startup project creation. Always respond in Vietnamese. Return valid JSON when requested."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                response_format={"type": "json_object"}
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Error calling OpenAI API: {str(e)}")
    
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


# Singleton instance
ai_service = AIService()
