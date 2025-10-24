"""
RAG Service - Retrieval Augmented Generation
Kết hợp vector search, Google search và LLM
"""
from typing import List, Dict, Any, Optional
from openai import OpenAI
import logging
from src.core.config import settings
from .vector_store import vector_store
from .tools import google_search_tool


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RAGService:
    """Service RAG với FAISS, Google Search và OpenAI"""
    
    def __init__(self):
        """Khởi tạo RAG Service"""
        self.client = OpenAI(
            api_key=settings.API_KEY,
            base_url=settings.BASE_URL
        )
        self.model = settings.LLM_MODEL
        self.vector_store = vector_store
        self.google_search = google_search_tool
    
    def _build_context_from_documents(
        self, 
        query: str,
        project_id: Optional[int] = None,
        top_k: int = None
    ) -> str:
        """
        Lấy context từ vector database
        
        Args:
            query: Câu truy vấn
            project_id: Lọc theo project (optional)
            top_k: Số lượng kết quả
            
        Returns:
            Context string
        """
        if top_k is None:
            top_k = settings.TOP_K_RESULTS
        
        # Search trong vector store
        results = self.vector_store.search(
            query=query,
            k=top_k,
            project_id=project_id
        )
        
        if not results:
            return ""
        
        # Build context
        context_parts = []
        for i, (text, metadata, score) in enumerate(results, 1):
            source = metadata.get("source", "Unknown")
            context_parts.append(f"[Tài liệu {i} - {source}]:\n{text}\n")
        
        return "\n".join(context_parts)
    
    def _build_context_from_google(
        self, 
        query: str,
        num_results: int = 3
    ) -> str:
        """
        Lấy context từ Google Search
        
        Args:
            query: Câu truy vấn
            num_results: Số lượng kết quả
            
        Returns:
            Context string
        """
        results = self.google_search.search(query, num_results=num_results)
        
        if not results:
            return ""
        
        # Build context
        context_parts = []
        for i, result in enumerate(results, 1):
            title = result.get('title', 'N/A')
            snippet = result.get('snippet') or result.get('description') or result.get('answer', '')
            link = result.get('link', '')
            
            context_parts.append(f"[Kết quả Google {i} - {title}]:\n{snippet}\nNguồn: {link}\n")
        
        return "\n".join(context_parts)
    
    def chat_with_rag(
        self,
        user_message: str,
        project_id: Optional[int] = None,
        use_google: bool = True,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Chat với RAG - kết hợp documents, Google search và LLM
        
        Args:
            user_message: Tin nhắn từ người dùng
            project_id: ID project để lọc documents (optional)
            use_google: Có sử dụng Google search không
            conversation_history: Lịch sử hội thoại
            system_prompt: Custom system prompt
            
        Returns:
            Dict chứa response và sources
        """
        try:
            # 1. Lấy context từ vector database
            doc_context = self._build_context_from_documents(
                query=user_message,
                project_id=project_id
            )
            
            # 2. Lấy context từ Google (nếu được bật)
            google_context = ""
            if use_google and settings.SERPAPI_API_KEY:
                google_context = self._build_context_from_google(
                    query=user_message,
                    num_results=3
                )
            
            # 3. Build full context
            full_context = ""
            if doc_context:
                full_context += f"**TÀI LIỆU THAM KHẢO:**\n\n{doc_context}\n\n"
            
            if google_context:
                full_context += f"**THÔNG TIN TỪ INTERNET:**\n\n{google_context}\n\n"
            
            # 4. Build system prompt
            if not system_prompt:
                system_prompt = """Bạn là trợ lý AI thông minh hỗ trợ startup và dự án.

Nhiệm vụ của bạn:
1. Trả lời câu hỏi của người dùng dựa trên:
   - Tài liệu tham khảo được cung cấp
   - Thông tin từ internet (nếu có)
   - Kiến thức của bạn
2. Luôn trả lời bằng tiếng Việt
3. Trích dẫn nguồn khi sử dụng thông tin từ tài liệu hoặc internet
4. Nếu không chắc chắn, hãy nói rõ điều đó
5. Đưa ra câu trả lời chi tiết, hữu ích và thực tế

Khi có tài liệu tham khảo hoặc thông tin từ internet, hãy ưu tiên sử dụng chúng.
Nếu không có thông tin liên quan, hãy dựa vào kiến thức của bạn để trả lời."""
            
            # 5. Build messages
            messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            # Thêm conversation history nếu có
            if conversation_history:
                messages.extend(conversation_history)
            
            # Thêm context và user message
            if full_context:
                user_content = f"{full_context}\n**CÂU HỎI:** {user_message}"
            else:
                user_content = user_message
            
            messages.append({"role": "user", "content": user_content})
            
            # 6. Call OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )
            
            answer = response.choices[0].message.content
            
            # 7. Build sources info
            sources = {
                "has_documents": bool(doc_context),
                "has_google_results": bool(google_context),
                "document_count": len(self.vector_store.search(user_message, k=settings.TOP_K_RESULTS, project_id=project_id)),
                "google_results": len(self.google_search.search(user_message, num_results=3)) if use_google and settings.SERPAPI_API_KEY else 0
            }
            
            return {
                "answer": answer,
                "sources": sources,
                "context_used": {
                    "documents": bool(doc_context),
                    "google": bool(google_context)
                }
            }
        
        except Exception as e:
            raise Exception(f"Error in RAG chat: {str(e)}")
    
    def answer_question(
        self,
        question: str,
        project_id: Optional[int] = None,
        use_google: bool = True
    ) -> Dict[str, Any]:
        """
        Trả lời câu hỏi đơn giản (không có conversation history)
        
        Args:
            question: Câu hỏi
            project_id: ID project
            use_google: Sử dụng Google search
            
        Returns:
            Dict chứa answer và sources
        """
        return self.chat_with_rag(
            user_message=question,
            project_id=project_id,
            use_google=use_google
        )
    
    def get_vector_store_stats(self) -> Dict[str, Any]:
        """Lấy thống kê về vector store"""
        return self.vector_store.get_stats()


# Singleton instance
rag_service = RAGService()
