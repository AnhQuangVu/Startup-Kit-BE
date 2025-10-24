"""
Test các API endpoints của AI module
"""
import pytest
from unittest.mock import patch, MagicMock
from src.ai import schemas


class TestGenerateProjectAPI:
    """Test API generate project từ mô tả"""
    
    def test_generate_project_success(self, client, auth_headers):
        """Test generate project thành công"""
        mock_response = {
            "name": "AI Startup",
            "tagline": "Revolutionary AI Solution",
            "industry": "Technology",
            "pain_point": "Lack of automation",
            "solution": "AI-powered automation",
            "product": "SaaS platform",
            "customer_segment": "SMEs",
            "market_size": "1000000",
            "business_model": "B2B",
            "revenue_method": "Subscription"
        }
        
        with patch('src.ai.ai_service.ai_service.generate_project_from_description') as mock_gen:
            mock_gen.return_value = schemas.AIGeneratedProject(**mock_response)
            
            response = client.post(
                "/ai/generate-project",
                json={"description": "Một nền tảng AI giúp doanh nghiệp tự động hóa quy trình"},
                headers=auth_headers
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "AI Startup"
        assert data["industry"] == "Technology"
        assert "AI" in data["tagline"] or "AI" in data["name"]
    
    def test_generate_project_unauthorized(self, client):
        """Test generate project không có token"""
        response = client.post(
            "/ai/generate-project",
            json={"description": "Test description"}
        )
        assert response.status_code == 401
    
    def test_generate_project_short_description(self, client, auth_headers):
        """Test generate project với mô tả quá ngắn"""
        response = client.post(
            "/ai/generate-project",
            json={"description": "Short"},
            headers=auth_headers
        )
        # Pydantic validation sẽ fail
        assert response.status_code == 422
    
    def test_generate_project_service_error(self, client, auth_headers):
        """Test xử lý lỗi từ AI service"""
        with patch('src.ai.ai_service.ai_service.generate_project_from_description') as mock_gen:
            mock_gen.side_effect = Exception("AI service error")
            
            response = client.post(
                "/ai/generate-project",
                json={"description": "A valid project description for testing"},
                headers=auth_headers
            )
        
        assert response.status_code == 500
        assert "Lỗi khi tạo dự án" in response.json()["detail"]


class TestSuggestionAPI:
    """Test API lấy gợi ý cho các trường"""
    
    def test_get_suggestions_success(self, client, auth_headers):
        """Test lấy gợi ý thành công"""
        mock_suggestions = [
            schemas.AISuggestion(suggestion="Suggestion 1", confidence=0.9),
            schemas.AISuggestion(suggestion="Suggestion 2", confidence=0.8),
            schemas.AISuggestion(suggestion="Suggestion 3", confidence=0.7)
        ]
        
        with patch('src.ai.ai_service.ai_service.generate_suggestions') as mock_sug:
            mock_sug.return_value = mock_suggestions
            
            response = client.post(
                "/ai/suggest",
                json={
                    "field_name": "pain_point",
                    "current_text": "Khách hàng gặp khó khăn trong",
                    "project_context": {"industry": "Technology"}
                },
                headers=auth_headers
            )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["suggestions"]) == 3
        assert data["suggestions"][0]["confidence"] == 0.9
    
    def test_get_suggestions_with_project_id(self, client, auth_headers, test_project):
        """Test lấy gợi ý với project_id"""
        mock_suggestions = [
            schemas.AISuggestion(suggestion="Based on project context", confidence=0.85)
        ]
        
        with patch('src.ai.ai_service.ai_service.generate_suggestions') as mock_sug:
            mock_sug.return_value = mock_suggestions
            
            response = client.post(
                "/ai/suggest",
                json={
                    "field_name": "solution",
                    "current_text": "We will solve this by",
                    "project_id": test_project.id
                },
                headers=auth_headers
            )
        
        assert response.status_code == 200
        # Verify rằng service được gọi với project context
        mock_sug.assert_called_once()
    
    def test_get_suggestions_unauthorized(self, client):
        """Test lấy gợi ý không có token"""
        response = client.post(
            "/ai/suggest",
            json={
                "field_name": "pain_point",
                "current_text": "Some text"
            }
        )
        assert response.status_code == 401


class TestAutocompleteAPI:
    """Test API autocomplete văn bản"""
    
    def test_autocomplete_success(self, client, auth_headers):
        """Test autocomplete thành công"""
        mock_result = schemas.AIAutocompleteResponse(
            completion=" the automation process",
            full_text="We will improve the automation process"
        )
        
        with patch('src.ai.ai_service.ai_service.autocomplete_text') as mock_auto:
            mock_auto.return_value = mock_result
            
            response = client.post(
                "/ai/autocomplete",
                json={
                    "field_name": "solution",
                    "current_text": "We will improve"
                },
                headers=auth_headers
            )
        
        assert response.status_code == 200
        data = response.json()
        assert "completion" in data
        assert "full_text" in data
        assert data["full_text"].startswith("We will improve")
    
    def test_autocomplete_with_context(self, client, auth_headers):
        """Test autocomplete với project context"""
        mock_result = schemas.AIAutocompleteResponse(
            completion=" using AI technology",
            full_text="Our product will use AI technology"
        )
        
        with patch('src.ai.ai_service.ai_service.autocomplete_text') as mock_auto:
            mock_auto.return_value = mock_result
            
            response = client.post(
                "/ai/autocomplete",
                json={
                    "field_name": "product",
                    "current_text": "Our product will",
                    "project_context": {"industry": "Technology"}
                },
                headers=auth_headers
            )
        
        assert response.status_code == 200


class TestBMCGenerationAPI:
    """Test API tạo Business Model Canvas"""
    
    def test_generate_bmc_success(self, client, auth_headers, test_project):
        """Test tạo BMC thành công"""
        mock_bmc = [
            schemas.AIBMCBlock(block="Key Partners", value="Tech companies"),
            schemas.AIBMCBlock(block="Key Activities", value="Software development"),
            schemas.AIBMCBlock(block="Value Propositions", value="Automation solution")
        ]
        
        with patch('src.ai.ai_service.ai_service.generate_bmc') as mock_gen:
            mock_gen.return_value = mock_bmc
            
            response = client.post(
                f"/ai/generate-bmc/{test_project.id}",
                headers=auth_headers
            )
        
        assert response.status_code == 200
        data = response.json()
        assert "bmc" in data
        assert len(data["bmc"]) == 3
        assert data["bmc"][0]["block"] == "Key Partners"
    
    def test_generate_bmc_project_not_found(self, client, auth_headers):
        """Test tạo BMC với project không tồn tại"""
        response = client.post(
            "/ai/generate-bmc/99999",
            headers=auth_headers
        )
        assert response.status_code == 404
        assert "Không tìm thấy dự án" in response.json()["detail"]
    
    def test_generate_bmc_unauthorized(self, client, test_project):
        """Test tạo BMC không có token"""
        response = client.post(f"/ai/generate-bmc/{test_project.id}")
        assert response.status_code == 401


class TestFinancialPlanAPI:
    """Test API tạo kế hoạch tài chính"""
    
    def test_generate_financial_plan_success(self, client, auth_headers, test_project):
        """Test tạo kế hoạch tài chính thành công"""
        mock_plan = schemas.AIFinancialPlanResponse(
            startup_costs=schemas.AIFinancialStartupCosts(
                initial_investment="500,000,000 VND",
                breakdown=[
                    schemas.AIFinancialBreakdown(item="Development", amount="300,000,000 VND")
                ]
            ),
            operating_costs=schemas.AIFinancialOperatingCosts(
                monthly="50,000,000 VND",
                breakdown=[
                    schemas.AIFinancialBreakdown(item="Salaries", amount="30,000,000 VND")
                ]
            ),
            revenue_projection=schemas.AIFinancialRevenueProjection(
                year1="200,000,000 VND",
                year2="500,000,000 VND",
                year3="1,000,000,000 VND",
                assumptions="Based on market analysis"
            ),
            funding_needs=schemas.AIFundingNeeds(
                total="500,000,000 VND",
                sources=[
                    schemas.AIFundingSource(
                        source="Angel Investors",
                        amount="500,000,000 VND",
                        percentage="100%"
                    )
                ]
            ),
            breakeven_analysis="Expected to break even in 18 months"
        )
        
        with patch('src.ai.ai_service.ai_service.generate_financial_plan') as mock_gen:
            mock_gen.return_value = mock_plan
            
            response = client.post(
                f"/ai/generate-financial/{test_project.id}",
                headers=auth_headers
            )
        
        assert response.status_code == 200
        data = response.json()
        assert "startup_costs" in data
        assert "operating_costs" in data
        assert "revenue_projection" in data
        assert data["startup_costs"]["initial_investment"] == "500,000,000 VND"
    
    def test_generate_financial_plan_project_not_found(self, client, auth_headers):
        """Test tạo kế hoạch tài chính với project không tồn tại"""
        response = client.post(
            "/ai/generate-financial/99999",
            headers=auth_headers
        )
        assert response.status_code == 404


class TestMarketResearchAPI:
    """Test API nghiên cứu thị trường"""
    
    def test_generate_market_research_success(self, client, auth_headers, test_project):
        """Test tạo nghiên cứu thị trường thành công"""
        mock_research = schemas.AIMarketResearchResponse(
            market_overview="Growing tech market",
            market_size="1 billion USD",
            market_trends=["AI adoption", "Cloud migration"],
            target_audience=schemas.AITargetAudience(
                demographics="25-45 years old",
                behaviors="Tech-savvy",
                pain_points="Manual processes"
            ),
            competitors=[
                schemas.AICompetitor(
                    name="Competitor A",
                    strengths="Established brand",
                    weaknesses="High price"
                )
            ],
            opportunities=["Market gap", "New technology"],
            threats=["Competition", "Regulation"],
            competitive_advantage="AI-powered automation"
        )
        
        with patch('src.ai.ai_service.ai_service.generate_market_research') as mock_gen:
            mock_gen.return_value = mock_research
            
            response = client.post(
                f"/ai/generate-market-research/{test_project.id}",
                headers=auth_headers
            )
        
        assert response.status_code == 200
        data = response.json()
        assert "market_overview" in data
        assert "competitors" in data
        assert len(data["market_trends"]) == 2
        assert len(data["competitors"]) == 1


class TestGTMStrategyAPI:
    """Test API chiến lược Go-to-Market"""
    
    def test_generate_gtm_strategy_success(self, client, auth_headers, test_project):
        """Test tạo chiến lược GTM thành công"""
        mock_gtm = schemas.AIGTMStrategyResponse(
            target_market="SME technology sector",
            positioning="AI automation leader",
            launch_phases=[
                schemas.AILaunchPhase(
                    phase="Beta Launch",
                    timeline="Q1 2025",
                    objectives=["Get 100 users"],
                    activities=["Marketing campaign"]
                )
            ],
            marketing_channels=[
                schemas.AIMarketingChannel(
                    channel="LinkedIn",
                    budget="10,000,000 VND",
                    expected_roi="300%"
                )
            ],
            sales_strategy="Direct B2B sales",
            customer_acquisition=schemas.AICustomerAcquisition(
                strategy="Content marketing + demos",
                cost_per_acquisition="500,000 VND",
                conversion_rate="5%"
            ),
            milestones=[
                schemas.AIMilestone(
                    milestone="First 100 customers",
                    target_date="Q2 2025"
                )
            ]
        )
        
        with patch('src.ai.ai_service.ai_service.generate_gtm_strategy') as mock_gen:
            mock_gen.return_value = mock_gtm
            
            response = client.post(
                f"/ai/generate-gtm/{test_project.id}",
                headers=auth_headers
            )
        
        assert response.status_code == 200
        data = response.json()
        assert "target_market" in data
        assert "launch_phases" in data
        assert len(data["marketing_channels"]) == 1


class TestEnhanceTextAPI:
    """Test API cải thiện văn bản"""
    
    def test_enhance_text_success(self, client, auth_headers):
        """Test cải thiện văn bản thành công"""
        mock_result = schemas.AIEnhanceTextResponse(
            original="We make software",
            enhanced="We develop cutting-edge software solutions",
            improvements=["More professional", "Added specificity"]
        )
        
        with patch('src.ai.ai_service.ai_service.enhance_text') as mock_enhance:
            mock_enhance.return_value = mock_result
            
            response = client.post(
                "/ai/enhance-text",
                json={
                    "text": "We make software",
                    "context": "Product description"
                },
                headers=auth_headers
            )
        
        assert response.status_code == 200
        data = response.json()
        assert "original" in data
        assert "enhanced" in data
        assert "improvements" in data
        assert len(data["improvements"]) == 2
    
    def test_enhance_text_without_context(self, client, auth_headers):
        """Test cải thiện văn bản không có context"""
        mock_result = schemas.AIEnhanceTextResponse(
            original="Good product",
            enhanced="Excellent product",
            improvements=["Enhanced quality descriptor"]
        )
        
        with patch('src.ai.ai_service.ai_service.enhance_text') as mock_enhance:
            mock_enhance.return_value = mock_result
            
            response = client.post(
                "/ai/enhance-text",
                json={"text": "Good product"},
                headers=auth_headers
            )
        
        assert response.status_code == 200


# ===== RAG API TESTS =====

class TestDocumentUploadAPI:
    """Test API upload tài liệu"""
    
    def test_upload_document_success(self, client, auth_headers, test_project):
        """Test upload document thành công"""
        # Mock file upload
        from io import BytesIO
        
        mock_file_content = b"This is a test PDF content"
        files = {
            "file": ("test.pdf", BytesIO(mock_file_content), "application/pdf")
        }
        
        with patch('src.ai.document_processor.document_processor.extract_preview') as mock_preview, \
             patch('src.ai.document_processor.document_processor.process_document') as mock_process, \
             patch('src.ai.vector_store.vector_store.add_documents') as mock_add:
            
            mock_preview.return_value = "Test preview"
            mock_process.return_value = ["chunk1", "chunk2"]
            mock_add.return_value = 2
            
            response = client.post(
                f"/ai/documents/upload?project_id={test_project.id}",
                files=files,
                headers=auth_headers
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["filename"] == "test.pdf"
        assert data["is_processed"] == True
        assert data["chunks_created"] == 2
    
    def test_upload_document_invalid_format(self, client, auth_headers):
        """Test upload file không hợp lệ"""
        from io import BytesIO
        
        files = {
            "file": ("test.exe", BytesIO(b"content"), "application/octet-stream")
        }
        
        response = client.post(
            "/ai/documents/upload",
            files=files,
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert "Định dạng file không hỗ trợ" in response.json()["detail"]
    
    def test_upload_document_project_not_found(self, client, auth_headers):
        """Test upload document với project không tồn tại"""
        from io import BytesIO
        
        files = {
            "file": ("test.pdf", BytesIO(b"content"), "application/pdf")
        }
        
        response = client.post(
            "/ai/documents/upload?project_id=99999",
            files=files,
            headers=auth_headers
        )
        
        assert response.status_code == 404


class TestListDocumentsAPI:
    """Test API liệt kê documents"""
    
    def test_list_documents_success(self, client, auth_headers, test_document):
        """Test lấy danh sách documents thành công"""
        response = client.get(
            "/ai/documents",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["filename"] == "test_doc.pdf"
    
    def test_list_documents_filter_by_project(self, client, auth_headers, test_document, test_project):
        """Test lọc documents theo project"""
        response = client.get(
            f"/ai/documents?project_id={test_project.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert all(doc["project_id"] == test_project.id for doc in data if doc["project_id"])
    
    def test_list_documents_unauthorized(self, client):
        """Test lấy danh sách documents không có token"""
        response = client.get("/ai/documents")
        assert response.status_code == 401


class TestDeleteDocumentAPI:
    """Test API xóa document"""
    
    def test_delete_document_success(self, client, auth_headers, test_document):
        """Test xóa document thành công"""
        with patch('src.ai.vector_store.vector_store.delete_document') as mock_delete, \
             patch('os.path.exists') as mock_exists, \
             patch('os.remove') as mock_remove:
            
            mock_exists.return_value = True
            mock_delete.return_value = True
            
            response = client.delete(
                f"/ai/documents/{test_document.id}",
                headers=auth_headers
            )
        
        assert response.status_code == 200
        assert "Xóa document thành công" in response.json()["message"]
    
    def test_delete_document_not_found(self, client, auth_headers):
        """Test xóa document không tồn tại"""
        response = client.delete(
            "/ai/documents/99999",
            headers=auth_headers
        )
        assert response.status_code == 404


class TestRAGChatAPI:
    """Test API chat với RAG"""
    
    def test_chat_with_rag_success(self, client, auth_headers):
        """Test chat thành công"""
        mock_response = schemas.RAGChatResponse(
            answer="This is the AI answer based on documents",
            sources={
                "documents": ["doc1.pdf", "doc2.pdf"],
                "google_results": []
            },
            context_used={
                "vector_db": True,
                "google_search": False
            }
        )
        
        with patch('src.ai.rag_service.rag_service.chat_with_rag') as mock_chat:
            mock_chat.return_value = mock_response
            
            response = client.post(
                "/ai/chat",
                json={
                    "message": "What is the market size?",
                    "use_google": False
                },
                headers=auth_headers
            )
        
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "sources" in data
        assert data["context_used"]["vector_db"] == True
    
    def test_chat_with_conversation_history(self, client, auth_headers):
        """Test chat với lịch sử hội thoại"""
        mock_response = schemas.RAGChatResponse(
            answer="Based on previous context...",
            sources={"documents": []},
            context_used={"vector_db": False, "google_search": False}
        )
        
        with patch('src.ai.rag_service.rag_service.chat_with_rag') as mock_chat:
            mock_chat.return_value = mock_response
            
            response = client.post(
                "/ai/chat",
                json={
                    "message": "Tell me more",
                    "conversation_history": [
                        {"role": "user", "content": "What is AI?"},
                        {"role": "assistant", "content": "AI is..."}
                    ],
                    "use_google": True
                },
                headers=auth_headers
            )
        
        assert response.status_code == 200
    
    def test_chat_with_project_filter(self, client, auth_headers, test_project):
        """Test chat với lọc theo project"""
        mock_response = schemas.RAGChatResponse(
            answer="Project-specific answer",
            sources={"documents": ["project_doc.pdf"]},
            context_used={"vector_db": True, "google_search": False}
        )
        
        with patch('src.ai.rag_service.rag_service.chat_with_rag') as mock_chat:
            mock_chat.return_value = mock_response
            
            response = client.post(
                "/ai/chat",
                json={
                    "message": "What are the project details?",
                    "project_id": test_project.id,
                    "use_google": False
                },
                headers=auth_headers
            )
        
        assert response.status_code == 200


class TestRAGQuestionAPI:
    """Test API hỏi đáp với RAG"""
    
    def test_ask_question_success(self, client, auth_headers):
        """Test hỏi đáp thành công"""
        mock_response = schemas.RAGChatResponse(
            answer="The answer to your question is...",
            sources={"documents": ["doc.pdf"]},
            context_used={"vector_db": True, "google_search": True}
        )
        
        with patch('src.ai.rag_service.rag_service.answer_question') as mock_answer:
            mock_answer.return_value = mock_response
            
            response = client.post(
                "/ai/ask",
                json={
                    "question": "How to start a business?",
                    "use_google": True
                },
                headers=auth_headers
            )
        
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "sources" in data
    
    def test_ask_question_without_google(self, client, auth_headers):
        """Test hỏi đáp không dùng Google"""
        mock_response = schemas.RAGChatResponse(
            answer="Answer from documents only",
            sources={"documents": ["doc.pdf"]},
            context_used={"vector_db": True, "google_search": False}
        )
        
        with patch('src.ai.rag_service.rag_service.answer_question') as mock_answer:
            mock_answer.return_value = mock_response
            
            response = client.post(
                "/ai/ask",
                json={
                    "question": "What is the solution?",
                    "use_google": False
                },
                headers=auth_headers
            )
        
        assert response.status_code == 200
        assert response.json()["context_used"]["google_search"] == False


class TestVectorStoreStatsAPI:
    """Test API thống kê vector store"""
    
    def test_get_vector_store_stats_success(self, client, auth_headers):
        """Test lấy thống kê thành công"""
        mock_stats = schemas.VectorStoreStatsResponse(
            total_vectors=1000,
            dimension=384,
            unique_documents=50,
            unique_projects=10
        )
        
        with patch('src.ai.rag_service.rag_service.get_vector_store_stats') as mock_stats_func:
            mock_stats_func.return_value = mock_stats
            
            response = client.get(
                "/ai/vector-store/stats",
                headers=auth_headers
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_vectors"] == 1000
        assert data["dimension"] == 384
        assert data["unique_documents"] == 50
    
    def test_get_vector_store_stats_unauthorized(self, client):
        """Test lấy thống kê không có token"""
        response = client.get("/ai/vector-store/stats")
        assert response.status_code == 401
