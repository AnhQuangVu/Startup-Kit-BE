"""
Vector Store sử dụng FAISS để lưu trữ và tìm kiếm embeddings
"""
import os
import pickle
from typing import List, Dict, Any, Optional, Tuple
import faiss
import numpy as np
from langchain_text_splitters  import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document as LangchainDocument
from src.core.config import settings


class VectorStore:
    """Quản lý FAISS vector database"""
    
    def __init__(self):
        """Khởi tạo Vector Store"""
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=settings.API_KEY,
            openai_api_base=settings.BASE_URL,
            model=settings.EMBEDDING_MODEL
        )
        
        self.vector_db_path = settings.VECTOR_DB_PATH
        self.index_file = os.path.join(self.vector_db_path, "faiss.index")
        self.metadata_file = os.path.join(self.vector_db_path, "metadata.pkl")
        
        # Tạo thư mục nếu chưa tồn tại
        os.makedirs(self.vector_db_path, exist_ok=True)
        
        # Load hoặc tạo mới index
        self.index = None
        self.metadata = []
        self.dimension = 1536  # text-embedding-3-small dimension
        
        self._load_or_create_index()
    
    def _load_or_create_index(self):
        """Load index từ disk hoặc tạo mới"""
        if os.path.exists(self.index_file) and os.path.exists(self.metadata_file):
            try:
                # Load FAISS index
                self.index = faiss.read_index(self.index_file)
                
                # Load metadata
                with open(self.metadata_file, 'rb') as f:
                    self.metadata = pickle.load(f)
                
                print(f"✓ Loaded vector store with {self.index.ntotal} vectors")
            except Exception as e:
                print(f"⚠ Error loading index: {e}. Creating new index...")
                self._create_new_index()
        else:
            self._create_new_index()
    
    def _create_new_index(self):
        """Tạo FAISS index mới"""
        # Sử dụng IndexFlatL2 cho độ chính xác cao
        self.index = faiss.IndexFlatL2(self.dimension)
        self.metadata = []
        print("✓ Created new FAISS index")
    
    def _save_index(self):
        """Lưu index và metadata xuống disk"""
        try:
            # Save FAISS index
            faiss.write_index(self.index, self.index_file)
            
            # Save metadata
            with open(self.metadata_file, 'wb') as f:
                pickle.dump(self.metadata, f)
            
            print(f"✓ Saved vector store with {self.index.ntotal} vectors")
        except Exception as e:
            print(f"✗ Error saving index: {e}")
            raise
    
    def add_documents(
        self, 
        documents: List[LangchainDocument],
        document_id: Optional[int] = None,
        project_id: Optional[int] = None
    ) -> int:
        """
        Thêm documents vào vector store
        
        Args:
            documents: List các Langchain Documents
            document_id: ID của document trong database
            project_id: ID của project liên quan
            
        Returns:
            Số lượng chunks đã thêm
        """
        if not documents:
            return 0
        
        try:
            # Tạo embeddings cho tất cả documents
            texts = [doc.page_content for doc in documents]
            embeddings = self.embeddings.embed_documents(texts)
            
            # Convert to numpy array
            embeddings_np = np.array(embeddings, dtype=np.float32)
            
            # Thêm vào FAISS index
            self.index.add(embeddings_np)
            
            # Lưu metadata
            for i, doc in enumerate(documents):
                metadata = {
                    "text": doc.page_content,
                    "metadata": doc.metadata,
                    "document_id": document_id,
                    "project_id": project_id,
                    "vector_id": self.index.ntotal - len(documents) + i
                }
                self.metadata.append(metadata)
            
            # Lưu xuống disk
            self._save_index()
            
            return len(documents)
        
        except Exception as e:
            print(f"✗ Error adding documents: {e}")
            raise
    
    def search(
        self, 
        query: str, 
        k: int = None,
        project_id: Optional[int] = None
    ) -> List[Tuple[str, Dict[str, Any], float]]:
        """
        Tìm kiếm documents tương tự với query
        
        Args:
            query: Câu truy vấn
            k: Số lượng kết quả trả về (default: TOP_K_RESULTS từ settings)
            project_id: Lọc theo project_id (optional)
            
        Returns:
            List of (text, metadata, score)
        """
        if k is None:
            k = settings.TOP_K_RESULTS
        
        if self.index.ntotal == 0:
            return []
        
        try:
            # Tạo embedding cho query
            query_embedding = self.embeddings.embed_query(query)
            query_embedding_np = np.array([query_embedding], dtype=np.float32)
            
            # Tìm kiếm trong FAISS
            # Lấy nhiều hơn k nếu cần filter theo project_id
            search_k = k * 3 if project_id else k
            distances, indices = self.index.search(query_embedding_np, search_k)
            
            # Lấy kết quả
            results = []
            for i, idx in enumerate(indices[0]):
                if idx < len(self.metadata):
                    meta = self.metadata[idx]
                    
                    # Filter theo project_id nếu có
                    if project_id and meta.get("project_id") != project_id:
                        continue
                    
                    results.append((
                        meta["text"],
                        meta["metadata"],
                        float(distances[0][i])
                    ))
                    
                    if len(results) >= k:
                        break
            
            return results
        
        except Exception as e:
            print(f"✗ Error searching: {e}")
            return []
    
    def delete_document(self, document_id: int):
        """
        Xóa tất cả chunks của một document
        
        Args:
            document_id: ID của document cần xóa
        """
        # FAISS không hỗ trợ xóa trực tiếp
        # Cần rebuild index mà không có document này
        try:
            # Lọc metadata
            new_metadata = [m for m in self.metadata if m.get("document_id") != document_id]
            
            if len(new_metadata) == len(self.metadata):
                # Không có gì để xóa
                return
            
            # Tạo index mới
            self._create_new_index()
            
            # Thêm lại các documents còn lại
            if new_metadata:
                texts = [m["text"] for m in new_metadata]
                embeddings = self.embeddings.embed_documents(texts)
                embeddings_np = np.array(embeddings, dtype=np.float32)
                self.index.add(embeddings_np)
                self.metadata = new_metadata
            
            # Lưu lại
            self._save_index()
            
            print(f"✓ Deleted document {document_id}")
        
        except Exception as e:
            print(f"✗ Error deleting document: {e}")
            raise
    
    def delete_project(self, project_id: int):
        """
        Xóa tất cả documents của một project
        
        Args:
            project_id: ID của project cần xóa
        """
        try:
            # Lọc metadata
            new_metadata = [m for m in self.metadata if m.get("project_id") != project_id]
            
            if len(new_metadata) == len(self.metadata):
                return
            
            # Rebuild index
            self._create_new_index()
            
            if new_metadata:
                texts = [m["text"] for m in new_metadata]
                embeddings = self.embeddings.embed_documents(texts)
                embeddings_np = np.array(embeddings, dtype=np.float32)
                self.index.add(embeddings_np)
                self.metadata = new_metadata
            
            self._save_index()
            
            print(f"✓ Deleted all documents from project {project_id}")
        
        except Exception as e:
            print(f"✗ Error deleting project documents: {e}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """Lấy thống kê về vector store"""
        return {
            "total_vectors": self.index.ntotal if self.index else 0,
            "dimension": self.dimension,
            "unique_documents": len(set(m.get("document_id") for m in self.metadata if m.get("document_id"))),
            "unique_projects": len(set(m.get("project_id") for m in self.metadata if m.get("project_id")))
        }


# Singleton instance
vector_store = VectorStore()
