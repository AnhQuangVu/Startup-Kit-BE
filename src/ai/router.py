from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import Dict, Any, List
import os
import shutil

from src.database.core import get_db
from src.database.models import User, Project, Document
from src.auth.service import get_current_user
from src.auth.service import get_optional_current_user
from typing import Optional
from src.core.config import settings
from . import schemas
from .ai_service import ai_service
from .rag_service import rag_service
from .document_processor import document_processor
from .vector_store import vector_store

router = APIRouter(
    prefix="/ai",
    tags=["AI Assistant"]
)

def get_project_context(project: Project) -> Dict[str, Any]:
    """Chuyển đổi project thành dict để làm context"""
    return {
        "name": project.name,
        "tagline": project.tagline,
        "description": project.description,
        "industry": project.industry,
        "pain_point": project.pain_point,
        "solution": project.solution,
        "product": project.product,
        "customer_segment": project.customer_segment,
        "market_size": project.market_size,
        "business_model": project.business_model,
        "revenue_method": project.revenue_method,
        "partners": project.partners,
        "cost_estimate": project.cost_estimate,
    }

@router.post("/generate-project", response_model=schemas.AIGeneratedProject)
def generate_project_from_description(
    request: schemas.AIGenerateProjectRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Tạo toàn bộ thông tin dự án từ mô tả ngắn
    
    Endpoint này nhận vào một đoạn mô tả dự án và AI sẽ tạo ra
    toàn bộ các trường thông tin cần thiết cho dự án.
    """
    try:
        generated_project = ai_service.generate_project_from_description(
            description=request.description
        )
        return generated_project
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi tạo dự án: {str(e)}"
        )


@router.post("/generate-description", response_model=schemas.AIGenerateDescriptionResponse)
def generate_startup_description(
    request: schemas.AIGenerateDescriptionRequest,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """
    Sinh mô tả hồ sơ startup tự động bằng AI (LLM)
    
    Có thể truyền trực tiếp:
    - name: Tên startup
    - industry: Lĩnh vực
    - target_audience: Khách hàng mục tiêu
    - key_features: Giải pháp / điểm nổi bật
    - tone: Phong cách văn phong
    - current_description: Mô tả nháp / hiện tại để cải thiện
    - project_id (tùy chọn): Tự động lấy thông tin từ database nếu có
    """
    try:
        name = request.name
        industry = request.industry
        target_audience = request.target_audience
        key_features = request.key_features
        current_description = request.current_description

        # Nếu có project_id, kiểm tra quyền truy cập chống IDOR và trích xuất ngữ cảnh dự án
        if request.project_id:
            query = db.query(Project).filter(Project.id == request.project_id)
            if current_user:
                # Cho phép lấy nếu là chủ sở hữu hoặc dự án đã publish
                project = query.filter((Project.founder_id == current_user.id) | (getattr(Project, "is_published", False) == True)).first()
            else:
                # Nếu khách vãng lai, chỉ cho phép nếu dự án đã publish công khai
                project = query.filter(getattr(Project, "is_published", False) == True).first()

            if project:
                if not name:
                    name = project.name
                if not industry:
                    industry = project.industry
                if not target_audience:
                    target_audience = project.customer_segment
                if not key_features:
                    key_features = project.solution or project.product
                if not current_description:
                    current_description = project.description

        result = ai_service.generate_startup_description(
            name=name,
            industry=industry,
            target_audience=target_audience,
            key_features=key_features,
            tone=request.tone,
            current_description=current_description
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi sinh mô tả startup bằng AI: {str(e)}"
        )

@router.post("/suggest", response_model=schemas.AISuggestionResponse)
def get_field_suggestions(
    request: schemas.AISuggestionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lấy gợi ý cho một trường cụ thể
    
    Khi người dùng đang nhập vào một trường (VD: pain_point, solution),
    endpoint này sẽ trả về các gợi ý dựa trên ngữ cảnh dự án.
    """
    try:
        # Nếu có project_id, lấy thông tin dự án
        project_context = request.project_context
        if request.project_id and not project_context:
            project = db.query(Project).filter(
                Project.id == request.project_id,
                Project.founder_id == current_user.id
            ).first()
            
            if project:
                project_context = get_project_context(project)
        
        suggestions = ai_service.generate_suggestions(
            field_name=request.field_name,
            current_text=request.current_text,
            project_context=project_context
        )
        
        return schemas.AISuggestionResponse(suggestions=suggestions)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi tạo gợi ý: {str(e)}"
        )

@router.post("/autocomplete", response_model=schemas.AIAutocompleteResponse)
def autocomplete_field(
    request: schemas.AIAutocompleteRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Autocomplete văn bản cho một trường
    
    Giống như autocomplete trong IDE, endpoint này sẽ hoàn thiện
    câu/đoạn văn mà người dùng đang nhập.
    """
    try:
        result = ai_service.autocomplete_text(
            field_name=request.field_name,
            current_text=request.current_text,
            project_context=request.project_context
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi autocomplete: {str(e)}"
        )

@router.post("/generate-bmc/{project_id}", response_model=schemas.AIBMCResponse)
def generate_business_model_canvas(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Tạo Business Model Canvas cho dự án
    
    Dựa trên thông tin dự án hiện có, AI sẽ tạo ra BMC với 9 blocks.
    """
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.founder_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy dự án"
        )
    
    try:
        project_info = get_project_context(project)
        bmc_blocks = ai_service.generate_bmc(project_info)
        
        return schemas.AIBMCResponse(bmc=bmc_blocks)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi tạo BMC: {str(e)}"
        )

@router.post("/generate-financial/{project_id}", response_model=schemas.AIFinancialPlanResponse)
def generate_financial_plan(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Tạo kế hoạch tài chính cho dự án
    
    AI sẽ tạo ước lượng chi phí, doanh thu, và nhu cầu vốn.
    """
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.founder_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy dự án"
        )
    
    try:
        project_info = get_project_context(project)
        financial_plan = ai_service.generate_financial_plan(project_info)
        
        return financial_plan
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi tạo kế hoạch tài chính: {str(e)}"
        )

@router.post("/generate-market-research/{project_id}", response_model=schemas.AIMarketResearchResponse)
def generate_market_research(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Tạo nghiên cứu thị trường cho dự án
    
    AI sẽ phân tích thị trường, đối thủ, cơ hội và thách thức.
    """
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.founder_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy dự án"
        )
    
    try:
        project_info = get_project_context(project)
        market_research = ai_service.generate_market_research(project_info)
        
        return market_research
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi tạo nghiên cứu thị trường: {str(e)}"
        )

@router.post("/generate-gtm/{project_id}", response_model=schemas.AIGTMStrategyResponse)
def generate_gtm_strategy(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Tạo chiến lược Go-to-Market cho dự án
    
    AI sẽ tạo chiến lược triển khai sản phẩm ra thị trường.
    """
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.founder_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy dự án"
        )
    
    try:
        project_info = get_project_context(project)
        gtm_strategy = ai_service.generate_gtm_strategy(project_info)
        
        return gtm_strategy
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi tạo chiến lược GTM: {str(e)}"
        )

@router.post("/enhance-text", response_model=schemas.AIEnhanceTextResponse)
def enhance_text(
    request: schemas.AIEnhanceTextRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Cải thiện văn bản
    
    AI sẽ cải thiện văn bản để chuyên nghiệp và rõ ràng hơn.
    """
    try:
        result = ai_service.enhance_text(
            text=request.text,
            context=request.context
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi cải thiện văn bản: {str(e)}"
        )


# ===== RAG ENDPOINTS =====

@router.post("/documents/upload", response_model=schemas.DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    project_id: int = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload tài liệu để thêm vào vector database
    
    Hỗ trợ: PDF, TXT, DOCX
    """
    # Validate file type
    allowed_extensions = ['pdf', 'txt', 'docx', 'doc']
    file_ext = file.filename.split('.')[-1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Định dạng file không hỗ trợ. Chỉ chấp nhận: {', '.join(allowed_extensions)}"
        )
    
    # Validate project ownership nếu có project_id
    if project_id:
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.founder_id == current_user.id
        ).first()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy dự án hoặc bạn không có quyền"
            )
    
    try:
        # Tạo thư mục lưu file
        documents_path = settings.DOCUMENTS_PATH
        os.makedirs(documents_path, exist_ok=True)
        
        # Lưu file
        file_path = os.path.join(documents_path, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        file_size = os.path.getsize(file_path)
        
        # Tạo record trong database
        doc = Document(
            filename=file.filename,
            file_path=file_path,
            file_type=file_ext,
            file_size=file_size,
            uploaded_by=current_user.id,
            project_id=project_id,
            is_processed=False
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        
        # Process document và thêm vào vector store
        try:
            # Extract preview
            preview = document_processor.extract_preview(file_path, file_ext)
            doc.content_preview = preview
            
            # Process và chunk document
            chunks = document_processor.process_document(
                file_path=file_path,
                file_type=file_ext,
                metadata={
                    "filename": file.filename,
                    "source": file.filename,
                    "document_id": doc.id,
                    "project_id": project_id,
                    "uploaded_by": current_user.id
                }
            )
            
            # Thêm vào vector store
            chunks_created = vector_store.add_documents(
                documents=chunks,
                document_id=doc.id,
                project_id=project_id
            )
            
            # Update processed status
            doc.is_processed = True
            doc.doc_metadata = {
                "chunks_count": chunks_created,
                "processed": True
            }
            db.commit()
            
            return schemas.DocumentUploadResponse(
                id=doc.id,
                filename=doc.filename,
                file_type=doc.file_type,
                file_size=doc.file_size,
                is_processed=True,
                chunks_created=chunks_created,
                message=f"Upload và xử lý thành công! Tạo {chunks_created} chunks."
            )
        
        except Exception as process_error:
            # Rollback nếu xử lý thất bại
            doc.is_processed = False
            doc.doc_metadata = {"error": str(process_error)}
            db.commit()
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Lỗi xử lý tài liệu: {str(process_error)}"
            )
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi upload: {str(e)}"
        )


@router.get("/documents", response_model=List[schemas.DocumentRead])
def list_documents(
    project_id: int = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lấy danh sách documents của user
    
    Có thể lọc theo project_id
    """
    query = db.query(Document).filter(Document.uploaded_by == current_user.id)
    
    if project_id:
        query = query.filter(Document.project_id == project_id)
    
    documents = query.order_by(Document.created_at.desc()).all()
    return documents


@router.delete("/documents/{document_id}")
def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Xóa document và các embeddings liên quan
    """
    doc = db.query(Document).filter(
        Document.id == document_id,
        Document.uploaded_by == current_user.id
    ).first()
    
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy document"
        )
    
    try:
        # Xóa file
        if os.path.exists(doc.file_path):
            os.remove(doc.file_path)
        
        # Xóa khỏi vector store
        vector_store.delete_document(document_id)
        
        # Xóa record trong DB
        db.delete(doc)
        db.commit()
        
        return {"message": "Xóa document thành công"}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi xóa document: {str(e)}"
        )


@router.post("/chat", response_model=schemas.RAGChatResponse)
def chat_with_rag(
    request: schemas.RAGChatRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Chat với AI sử dụng RAG
    
    AI sẽ sử dụng:
    - Tài liệu đã upload (từ vector database)
    - Google Search (nếu bật)
    - Kiến thức của model
    
    để trả lời câu hỏi.
    """
    try:
        result = rag_service.chat_with_rag(
            user_message=request.message,
            project_id=request.project_id,
            use_google=request.use_google,
            conversation_history=request.conversation_history
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi chat: {str(e)}"
        )


@router.post("/chat/public", response_model=schemas.RAGChatResponse)
def chat_public(
    request: schemas.RAGChatRequest,
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """Public chat endpoint: allows anonymous users.

    Restrictions for anonymous requests:
    - `project_id` is not allowed (project context requires authentication)
    - message length limited
    """
    # Reject project context for anonymous users
    if current_user is None and request.project_id is not None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Project context requires authentication")

    # Simple input guard for anonymous users
    if current_user is None and request.message and len(request.message) > 1000:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Message too long for anonymous requests")

    try:
        result = rag_service.chat_with_rag(
            user_message=request.message,
            project_id=(request.project_id if current_user else None),
            use_google=request.use_google,
            conversation_history=request.conversation_history
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi chat: {str(e)}"
        )


@router.post("/ask", response_model=schemas.RAGChatResponse)
def ask_question(
    request: schemas.RAGQuestionRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Hỏi đáp đơn giản với RAG (không có conversation history)
    
    Endpoint này phù hợp cho các câu hỏi độc lập.
    """
    try:
        result = rag_service.answer_question(
            question=request.question,
            project_id=request.project_id,
            use_google=request.use_google
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi trả lời câu hỏi: {str(e)}"
        )


@router.get("/vector-store/stats", response_model=schemas.VectorStoreStatsResponse)
def get_vector_store_stats(
    current_user: User = Depends(get_current_user)
):
    """
    Lấy thống kê về vector store
    """
    try:
        stats = rag_service.get_vector_store_stats()
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi lấy thống kê: {str(e)}"
        )
