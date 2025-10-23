"""
Tools cho AI Agent - Google Search
"""
from typing import List, Dict, Any, Optional
import requests
import logging
from src.core.config import settings

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GoogleSearchTool:
    """Tool để search Google thông qua SerpAPI"""
    
    def __init__(self):
        """Khởi tạo Google Search Tool"""
        self.api_key = settings.SERPAPI_API_KEY
        self.base_url = "https://serpapi.com/search"
    
    def search(
        self, 
        query: str, 
        num_results: int = 5,
        location: str = "Vietnam"
    ) -> List[Dict[str, Any]]:
        """
        Tìm kiếm trên Google
        
        Args:
            query: Câu truy vấn
            num_results: Số kết quả trả về
            location: Vị trí tìm kiếm
            
        Returns:
            List of search results
        """
        if not self.api_key:
            logger.warning("SERPAPI_API_KEY not configured")
            return []
        
        try:
            params = {
                "q": query,
                "api_key": self.api_key,
                "engine": "google",
                "num": num_results,
                "location": location,
                "gl": "vn",  # Google country
                "hl": "vi"   # Language
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Parse kết quả
            results = []
            
            # Organic results
            if "organic_results" in data:
                for result in data["organic_results"][:num_results]:
                    results.append({
                        "title": result.get("title", ""),
                        "link": result.get("link", ""),
                        "snippet": result.get("snippet", ""),
                        "source": "google_organic"
                    })
            
            # Knowledge graph
            if "knowledge_graph" in data and len(results) < num_results:
                kg = data["knowledge_graph"]
                results.append({
                    "title": kg.get("title", ""),
                    "description": kg.get("description", ""),
                    "source": "knowledge_graph",
                    "type": kg.get("type", "")
                })
            
            # Answer box
            if "answer_box" in data and len(results) < num_results:
                ab = data["answer_box"]
                results.append({
                    "title": ab.get("title", ""),
                    "answer": ab.get("answer", ""),
                    "snippet": ab.get("snippet", ""),
                    "source": "answer_box"
                })
            
            return results
        
        except requests.exceptions.RequestException as e:
            logger.error(f"✗ Error searching Google: {e}")
            return []
        except Exception as e:
            logger.error(f"✗ Unexpected error: {e}")
            return []
    
    def format_results(self, results: List[Dict[str, Any]]) -> str:
        """
        Format search results thành text
        
        Args:
            results: Search results
            
        Returns:
            Formatted text
        """
        if not results:
            return "Không tìm thấy kết quả."
        
        formatted = "**Kết quả tìm kiếm từ Google:**\n\n"
        
        for i, result in enumerate(results, 1):
            formatted += f"{i}. **{result.get('title', 'N/A')}**\n"
            
            if result.get('snippet'):
                formatted += f"   {result['snippet']}\n"
            elif result.get('description'):
                formatted += f"   {result['description']}\n"
            elif result.get('answer'):
                formatted += f"   {result['answer']}\n"
            
            if result.get('link'):
                formatted += f"   🔗 {result['link']}\n"
            
            formatted += f"   _Nguồn: {result.get('source', 'unknown')}_\n\n"
        
        return formatted


# Singleton instance
google_search_tool = GoogleSearchTool()
