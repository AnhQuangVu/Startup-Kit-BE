"""
Document Processor để xử lý và chunk các loại tài liệu khác nhau
"""
import os
from typing import List, Optional
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document as LangchainDocument
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    Docx2txtLoader
)
from src.core.config import settings


class DocumentProcessor:
    """Xử lý và chunk documents"""
    
    def __init__(self):
        """Khởi tạo Document Processor"""
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def load_document(self, file_path: str, file_type: str) -> List[LangchainDocument]:
        """
        Load document từ file path
        
        Args:
            file_path: Đường dẫn đến file
            file_type: Loại file (pdf, txt, docx, etc.)
            
        Returns:
            List of Langchain Documents
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            if file_type.lower() == 'pdf':
                loader = PyPDFLoader(file_path)
            elif file_type.lower() == 'txt':
                loader = TextLoader(file_path, encoding='utf-8')
            elif file_type.lower() in ['docx', 'doc']:
                loader = Docx2txtLoader(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
            
            documents = loader.load()
            return documents
        
        except Exception as e:
            print(f"✗ Error loading document: {e}")
            raise
    
    def process_document(
        self, 
        file_path: str, 
        file_type: str,
        metadata: Optional[dict] = None
    ) -> List[LangchainDocument]:
        """
        Process document: load và chunk
        
        Args:
            file_path: Đường dẫn đến file
            file_type: Loại file
            metadata: Metadata bổ sung
            
        Returns:
            List of chunked Langchain Documents
        """
        try:
            # Load document
            documents = self.load_document(file_path, file_type)
            
            # Thêm metadata nếu có
            if metadata:
                for doc in documents:
                    doc.metadata.update(metadata)
            
            # Chunk documents
            chunks = self.text_splitter.split_documents(documents)
            
            print(f"[OK] Processed document into {len(chunks)} chunks")
            return chunks
        
        except Exception as e:
            print(f"✗ Error processing document: {e}")
            raise
    
    def process_text(
        self, 
        text: str, 
        metadata: Optional[dict] = None
    ) -> List[LangchainDocument]:
        """
        Process raw text: chunk
        
        Args:
            text: Văn bản cần xử lý
            metadata: Metadata bổ sung
            
        Returns:
            List of chunked Langchain Documents
        """
        try:
            # Tạo document
            doc = LangchainDocument(
                page_content=text,
                metadata=metadata or {}
            )
            
            # Chunk
            chunks = self.text_splitter.split_documents([doc])
            
            print(f"[OK] Processed text into {len(chunks)} chunks")
            return chunks
        
        except Exception as e:
            print(f"✗ Error processing text: {e}")
            raise
    
    def extract_preview(self, file_path: str, file_type: str, max_chars: int = 500) -> str:
        """
        Extract preview text từ document
        
        Args:
            file_path: Đường dẫn đến file
            file_type: Loại file
            max_chars: Số ký tự tối đa
            
        Returns:
            Preview text
        """
        try:
            documents = self.load_document(file_path, file_type)
            
            if not documents:
                return ""
            
            # Lấy text từ page đầu tiên
            preview = documents[0].page_content[:max_chars]
            
            if len(documents[0].page_content) > max_chars:
                preview += "..."
            
            return preview
        
        except Exception as e:
            print(f"✗ Error extracting preview: {e}")
            return ""


# Singleton instance
document_processor = DocumentProcessor()
