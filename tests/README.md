# Test Documentation

## Cài đặt dependencies cho testing

```bash
pip install pytest pytest-asyncio pytest-cov
```

Hoặc cài đặt từ requirements.txt:

```bash
pip install -r requirements.txt
```

## Chạy tests

### Chạy tất cả tests
```bash
pytest
```

### Chạy tests với output chi tiết
```bash
pytest -v
```

### Chạy tests với coverage report
```bash
pytest --cov=src --cov-report=html
```

### Chạy chỉ tests cho AI module
```bash
pytest tests/test_ai_api.py -v
```

### Chạy một test class cụ thể
```bash
pytest tests/test_ai_api.py::TestGenerateProjectAPI -v
```

### Chạy một test method cụ thể
```bash
pytest tests/test_ai_api.py::TestGenerateProjectAPI::test_generate_project_success -v
```

## Cấu trúc tests

### test_ai_api.py
File này chứa tất cả tests cho các API endpoints của AI module:

#### 1. **Project Generation APIs**
- `TestGenerateProjectAPI`: Test API tạo project từ mô tả
  - Test tạo project thành công
  - Test xử lý lỗi unauthorized
  - Test validation input
  - Test xử lý lỗi từ AI service

#### 2. **Suggestion & Autocomplete APIs**
- `TestSuggestionAPI`: Test API lấy gợi ý cho các trường
  - Test lấy gợi ý thành công
  - Test với project context
  - Test với project_id
  
- `TestAutocompleteAPI`: Test API autocomplete văn bản
  - Test autocomplete thành công
  - Test với context

#### 3. **Business Model Canvas API**
- `TestBMCGenerationAPI`: Test API tạo BMC
  - Test tạo BMC thành công
  - Test với project không tồn tại
  - Test unauthorized

#### 4. **Financial Planning API**
- `TestFinancialPlanAPI`: Test API tạo kế hoạch tài chính
  - Test tạo financial plan thành công
  - Test với project không tồn tại

#### 5. **Market Research API**
- `TestMarketResearchAPI`: Test API nghiên cứu thị trường
  - Test tạo market research thành công
  - Test xử lý lỗi

#### 6. **Go-to-Market Strategy API**
- `TestGTMStrategyAPI`: Test API chiến lược GTM
  - Test tạo GTM strategy thành công
  - Test xử lý các trường hợp lỗi

#### 7. **Text Enhancement API**
- `TestEnhanceTextAPI`: Test API cải thiện văn bản
  - Test enhance text thành công
  - Test với và không có context

#### 8. **RAG Document APIs**
- `TestDocumentUploadAPI`: Test API upload tài liệu
  - Test upload document thành công
  - Test validate file format
  - Test với project không tồn tại
  
- `TestListDocumentsAPI`: Test API liệt kê documents
  - Test lấy danh sách documents
  - Test filter theo project
  
- `TestDeleteDocumentAPI`: Test API xóa document
  - Test xóa document thành công
  - Test với document không tồn tại

#### 9. **RAG Chat & Question APIs**
- `TestRAGChatAPI`: Test API chat với RAG
  - Test chat thành công
  - Test với conversation history
  - Test với project filter
  
- `TestRAGQuestionAPI`: Test API hỏi đáp
  - Test hỏi đáp thành công
  - Test với và không có Google search
  
- `TestVectorStoreStatsAPI`: Test API thống kê vector store
  - Test lấy thống kê thành công

## Fixtures

### conftest.py
File này chứa các fixtures dùng chung cho tất cả tests:

- `db`: In-memory SQLite database cho mỗi test
- `client`: FastAPI TestClient với database override
- `test_user`: User mẫu cho testing
- `test_token`: Access token cho authentication
- `auth_headers`: Headers với Bearer token
- `test_project`: Project mẫu
- `test_document`: Document mẫu

## Mocking

Tests sử dụng `unittest.mock.patch` để mock các AI services:
- `ai_service.generate_project_from_description()`
- `ai_service.generate_suggestions()`
- `ai_service.autocomplete_text()`
- `ai_service.generate_bmc()`
- `ai_service.generate_financial_plan()`
- `ai_service.generate_market_research()`
- `ai_service.generate_gtm_strategy()`
- `ai_service.enhance_text()`
- `rag_service.chat_with_rag()`
- `rag_service.answer_question()`
- `rag_service.get_vector_store_stats()`
- `document_processor` methods
- `vector_store` methods

## Coverage Report

Sau khi chạy với coverage:
```bash
pytest --cov=src --cov-report=html
```

Mở file `htmlcov/index.html` trong browser để xem coverage report chi tiết.

## Best Practices

1. **Isolation**: Mỗi test độc lập, sử dụng in-memory database
2. **Mocking**: Mock external services (AI, file system) để test nhanh và reliable
3. **Fixtures**: Sử dụng fixtures để tái sử dụng setup code
4. **Clear naming**: Tên test mô tả rõ ràng điều đang test
5. **Assertions**: Kiểm tra cả status code và response data

## Troubleshooting

### Lỗi import modules
Nếu gặp lỗi import, đảm bảo PYTHONPATH đúng:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"  # Linux/Mac
$env:PYTHONPATH="$pwd"  # Windows PowerShell
```

### Lỗi database
Tests sử dụng SQLite in-memory nên không cần MySQL/PostgreSQL. Nếu vẫn có lỗi, check:
- SQLAlchemy đã cài đúng version
- Import models thành công

### Lỗi authentication
Nếu tests authentication fail, check:
- JWT secret key configuration
- Token generation logic trong fixtures
