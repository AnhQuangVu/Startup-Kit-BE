# Notification API Documentation

## Tổng quan

Module Notification cung cấp đầy đủ các API để quản lý hệ thống thông báo cho người dùng trong platform.

## Các tính năng chính

✅ **Lấy danh sách thông báo** với pagination  
✅ **Lọc thông báo chưa đọc**  
✅ **Đếm số lượng thông báo** (tổng + chưa đọc)  
✅ **Đánh dấu đã đọc** (từng cái hoặc tất cả)  
✅ **Xóa thông báo** (từng cái hoặc tất cả)  
✅ **Helper functions** để tạo thông báo cho các sự kiện khác nhau  

---

## API Endpoints

### 1. **GET /api/notifications/**
Lấy danh sách thông báo của user hiện tại

**Query Parameters:**
- `page` (int, default=1): Số trang
- `page_size` (int, default=20, max=100): Số items mỗi trang
- `unread_only` (bool, default=false): Chỉ lấy thông báo chưa đọc

**Response:**
```json
{
  "notifications": [
    {
      "id": 1,
      "recipient_id": 5,
      "content": "John Doe đã gửi yêu cầu kết nối đến dự án 'AI Platform' của bạn",
      "type": "new_connection_request",
      "related_entity_id": 10,
      "is_read": false,
      "created_at": "2025-11-03T10:30:00Z"
    }
  ],
  "total": 50,
  "page": 1,
  "page_size": 20,
  "unread_count": 15
}
```

---

### 2. **GET /api/notifications/count**
Đếm số lượng thông báo

**Response:**
```json
{
  "total": 50,
  "unread": 15
}
```

---

### 3. **GET /api/notifications/{notification_id}**
Lấy chi tiết một thông báo

**Response:**
```json
{
  "id": 1,
  "recipient_id": 5,
  "content": "John Doe đã gửi yêu cầu kết nối...",
  "type": "new_connection_request",
  "related_entity_id": 10,
  "is_read": false,
  "created_at": "2025-11-03T10:30:00Z"
}
```

---

### 4. **PATCH /api/notifications/{notification_id}/read**
Đánh dấu thông báo là đã đọc

**Response:**
```json
{
  "id": 1,
  "recipient_id": 5,
  "content": "...",
  "type": "new_connection_request",
  "related_entity_id": 10,
  "is_read": true,
  "created_at": "2025-11-03T10:30:00Z"
}
```

---

### 5. **POST /api/notifications/mark-all-read**
Đánh dấu tất cả thông báo là đã đọc

**Response:**
```json
{
  "message": "Đã đánh dấu tất cả thông báo là đã đọc",
  "updated_count": 15
}
```

---

### 6. **DELETE /api/notifications/{notification_id}**
Xóa một thông báo

**Response:**
```json
{
  "message": "Đã xóa thông báo thành công"
}
```

---

### 7. **DELETE /api/notifications/**
Xóa tất cả thông báo của user

**Response:**
```json
{
  "message": "Đã xóa tất cả thông báo",
  "deleted_count": 50
}
```

---

## Loại thông báo (NotificationType)

Hệ thống hỗ trợ 4 loại thông báo:

1. **`new_connection_request`** - Yêu cầu kết nối mới
2. **`connection_accepted`** - Kết nối được chấp nhận
3. **`project_update`** - Cập nhật dự án
4. **`new_message`** - Tin nhắn mới

---

## Helper Functions trong Service

Service layer cung cấp các helper functions để tạo thông báo dễ dàng:

### 1. Thông báo yêu cầu kết nối
```python
from src.notifications.service import NotificationService

NotificationService.create_connection_request_notification(
    db=db,
    recipient_id=founder_id,
    sender_name="John Investor",
    project_name="AI Platform",
    connection_id=connection.id
)
```

### 2. Thông báo kết nối được chấp nhận
```python
NotificationService.create_connection_accepted_notification(
    db=db,
    recipient_id=investor_id,
    founder_name="Jane Founder",
    project_name="AI Platform",
    connection_id=connection.id
)
```

### 3. Thông báo cập nhật dự án
```python
NotificationService.create_project_update_notification(
    db=db,
    recipient_id=follower_id,
    project_name="AI Platform",
    project_id=project.id
)
```

### 4. Thông báo tin nhắn mới
```python
NotificationService.create_new_message_notification(
    db=db,
    recipient_id=recipient_id,
    sender_name="John Doe",
    conversation_id=conversation.id
)
```

---

## Tích hợp với các module khác

### Ví dụ: Tạo thông báo khi có connection request

Trong `src/projects/service.py` hoặc connection service:

```python
from src.notifications.service import NotificationService

# Khi tạo connection request
def create_connection_request(db, investor_id, project_id, message):
    # ... tạo connection ...
    
    # Tạo thông báo cho founder
    project = db.query(Project).filter(Project.id == project_id).first()
    investor = db.query(User).filter(User.id == investor_id).first()
    
    NotificationService.create_connection_request_notification(
        db=db,
        recipient_id=project.founder_id,
        sender_name=investor.full_name,
        project_name=project.name,
        connection_id=connection.id
    )
    
    return connection
```

---

## Authentication

Tất cả các endpoints đều yêu cầu authentication. Token phải được gửi trong header:

```
Authorization: Bearer <your_access_token>
```

User chỉ có thể truy cập và quản lý thông báo của chính mình.

---

## Testing

### Test API với curl:

```bash
# Lấy danh sách thông báo
curl -X GET "http://localhost:8000/api/notifications/?page=1&page_size=20" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Đếm số thông báo
curl -X GET "http://localhost:8000/api/notifications/count" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Đánh dấu đã đọc
curl -X PATCH "http://localhost:8000/api/notifications/1/read" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Đánh dấu tất cả đã đọc
curl -X POST "http://localhost:8000/api/notifications/mark-all-read" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Xóa thông báo
curl -X DELETE "http://localhost:8000/api/notifications/1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Database Schema

Bảng `notifications` có cấu trúc:

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| recipient_id | Integer | FK to users.id |
| content | Text | Nội dung thông báo |
| type | Enum | Loại thông báo |
| related_entity_id | Integer | ID entity liên quan (optional) |
| is_read | Boolean | Đã đọc chưa (default: False, indexed) |
| created_at | DateTime | Thời gian tạo |

---

## Tính năng mở rộng (có thể thêm sau)

- 🔔 **WebSocket real-time notifications**
- 📱 **Push notifications** (Firebase, OneSignal)
- ⚙️ **Notification preferences** (cho phép user tắt/bật loại thông báo)
- 📊 **Admin dashboard** để quản lý thông báo hệ thống
- 🎨 **Rich notifications** với images, actions, deep links
- ⏰ **Scheduled notifications**
- 📧 **Email notifications** (gửi email khi có thông báo quan trọng)

---

## Notes

- Thông báo được sắp xếp theo thời gian mới nhất trước
- `is_read` field có index để query nhanh
- `related_entity_id` giúp link đến entity gốc (project, connection, conversation)
- Cascade delete: khi xóa user, tất cả notifications của user đó cũng bị xóa

