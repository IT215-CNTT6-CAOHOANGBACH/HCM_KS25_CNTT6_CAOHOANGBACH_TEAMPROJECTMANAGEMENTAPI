# TEST API - TEAM PROJECT MANAGEMENT API

## 1. Thông tin kiểm thử

- Ngày kiểm thử: 2026-08-26
- Môi trường: FastAPI chạy bằng `.venv`
- Database: MySQL `project_management`
- Công cụ: FastAPI `TestClient`, compile Python, kiểm tra source và OpenAPI
- Automated test: Chưa có test file trong thư mục `tests/`
- Kết quả chạy pytest: `no tests ran`

## 2. Quy ước trạng thái

- **PASS**: Đã chạy và kết quả đúng kỳ vọng.
- **FAIL**: Đã chạy và phát hiện kết quả không đúng hoặc có lỗi bảo mật/nghiệp vụ.
- **SOURCE**: Source có triển khai, nhưng chưa chạy bằng test case độc lập.
- **NOT RUN**: Chưa kiểm thử được.

## 3. Các test case đã thực hiện

| Test ID | API / Nội dung | Expected | Actual | Status |
|---|---|---:|---:|---|
| TC-AUTH-001 | `POST /auth/register` với dữ liệu hợp lệ | 201 | 201, tạo user thành công | PASS |
| TC-AUTH-002 | Register email đã tồn tại | 400/409 | 409, `Email đã tồn tại` | PASS |
| TC-AUTH-003 | `POST /auth/login` đúng email/password | 200 + JWT | 200, trả access token | PASS |
| TC-AUTH-005 | Gọi `/users/me` không có token | 401 | 401 | PASS |
| TC-AUTH-006 | Gọi `/users/me` với token sai | 401 | 401, `Token không hợp lệ` | PASS |
| TC-USER-001 | `GET /users/me` | Trả thông tin user | 200, không có `password_hash` | PASS |
| TC-PROJECT-001 | `POST /projects` với tên hợp lệ | 201 | 201, user trở thành OWNER | PASS |
| TC-PROJECT-003 | Tạo project với tên rỗng | 400/422 | 400 | PASS |
| TC-TASK-003 | Tạo task thiếu `title` | 422 | 422, lỗi field bắt buộc | PASS |
| TC-CODE-001 | Compile toàn bộ source | Không có lỗi cú pháp | `compileall` thành công | PASS |
| TC-CODE-002 | Kiểm tra diagnostics file chính | Không có lỗi | Không có lỗi diagnostics | PASS |

## 4. Checklist theo chức năng

### Authentication

| Nội dung | Status | Ghi chú |
|---|---|---|
| Register email hợp lệ | PASS | Đã chạy |
| Register email trùng | PASS | Trả 409 |
| Register dữ liệu không hợp lệ | SOURCE | Có validation Pydantic, chưa chạy đầy đủ |
| Login đúng | PASS | Đã chạy |
| Login sai password | NOT RUN | |
| Login user không tồn tại | NOT RUN | |
| JWT access token | PASS | Đã nhận token và gọi `/users/me` |
| Gọi API không token | PASS | Đã chạy |
| Token sai | PASS | Đã chạy |
| Token hết hạn | NOT RUN | |

### User

| Nội dung | Status | Ghi chú |
|---|---|---|
| Lấy `/users/me` | PASS | Đã chạy |
| Không lộ `password_hash` | PASS | Đã kiểm tra response |
| Admin lấy danh sách user | SOURCE | Endpoint yêu cầu role ADMIN |
| User thường lấy danh sách user | SOURCE | Dự kiến 403, chưa chạy |
| Search theo tên/email | SOURCE | Có trong service |
| Filter theo trạng thái | SOURCE | Có `is_active` |
| Pagination user | SOURCE | Có `page` và `limit` |

### Project

| Nội dung | Status | Ghi chú |
|---|---|---|
| Tạo project hợp lệ | PASS | Đã chạy |
| Tên rỗng | PASS | Đã chạy, trả 400 |
| Tên vượt giới hạn | NOT RUN | Giới hạn service đang là 10 ký tự, message ghi 20 |
| User tạo project thành OWNER | PASS | Đã xác nhận từ response và source |
| Danh sách project của user | SOURCE | Có lọc member và soft delete |
| Search project | SOURCE | Có query `search` |
| Xem chi tiết project | SOURCE | Có kiểm tra membership |
| User ngoài project truy cập | SOURCE | Dự kiến 403, chưa chạy |
| OWNER cập nhật project | SOURCE | API hiện là `PUT` |
| MEMBER cập nhật project | SOURCE | Có kiểm tra OWNER, dự kiến 403 |
| OWNER xóa project | SOURCE | Soft delete |
| MEMBER xóa project | SOURCE | Có kiểm tra OWNER, dự kiến 403 |
| Kiểm tra soft delete | FAIL | Task route chưa kiểm tra project đã bị xóa mềm |
| `PATCH /projects/{id}` theo test mẫu | FAIL | Chưa có endpoint PATCH, chỉ có PUT |

### Project Member

| Nội dung | Status | Ghi chú |
|---|---|---|
| OWNER thêm member | SOURCE | Có endpoint |
| Thêm member hợp lệ | NOT RUN | |
| User không tồn tại | SOURCE | Có trả 404 trong service |
| Member đã tồn tại | SOURCE | Có trả 400 |
| MEMBER thêm member | SOURCE | Có kiểm tra OWNER |
| OWNER xóa member | NOT RUN | |
| MEMBER xóa member | SOURCE | Có kiểm tra OWNER |
| Không xóa OWNER | SOURCE | Có trả 400 |
| Lấy danh sách member | SOURCE | Có endpoint |
| Kiểm tra role member | SOURCE | Response có field `role` |

### Task

| Nội dung | Status | Ghi chú |
|---|---|---|
| MEMBER tạo task | SOURCE | `get_member_role` cho phép member |
| Tạo task hợp lệ | NOT RUN | |
| Thiếu title | PASS | Đã chạy, trả 422 |
| Priority không hợp lệ | SOURCE | Enum validation |
| Status không hợp lệ | SOURCE | Enum validation |
| Due date không hợp lệ | SOURCE | Pydantic validation |
| Tạo task ở project không thuộc user | SOURCE | Dự kiến 403 |
| Danh sách task | SOURCE | Có endpoint |
| Không lộ task giữa project | SOURCE | Có kiểm tra membership khi xem list/detail |
| Xem chi tiết task | SOURCE | Có endpoint |
| User ngoài project truy cập | SOURCE | Dự kiến 403 |
| OWNER/ASSIGNEE cập nhật task | SOURCE | Có kiểm tra permission |
| PATCH partial update | SOURCE | Có `exclude_unset=True` |
| Field không gửi không bị ghi đè | SOURCE | Chưa chạy thực tế |
| Xóa task | SOURCE | Chỉ OWNER được xóa |
| User không có quyền xóa | SOURCE | Dự kiến 403 |
| Gán task cho member | SOURCE | Có kiểm tra assignee |
| Gán cho user ngoài project | SOURCE | Dự kiến 400 |
| Status TODO / IN_PROGRESS / DONE | SOURCE | Có enum |
| Priority LOW / MEDIUM / HIGH | SOURCE | Có enum |
| Search theo title | SOURCE | Có `ilike` |
| Filter status / priority / assignee | SOURCE | Có query filter |
| Kết hợp nhiều filter | SOURCE | Có thể kết hợp query |
| Pagination task | FAIL | Chưa có `page`, `limit` |
| Sort `created_at` / `due_date` | FAIL | Chưa có tham số sort |

## 5. Lỗi và rủi ro phát hiện

### BUG-001 - Task vẫn truy cập được sau khi project bị soft-delete

- Mức độ: Cao
- Nguyên nhân: `get_member_role()` trong `app/routers/tasks.py` chỉ kiểm tra bản ghi `ProjectMember`, không kiểm tra `Project.is_deleted`.
- Ảnh hưởng: Member của project đã xóa mềm vẫn có thể xem hoặc tạo task.
- Đề xuất: Kiểm tra project active trước mọi thao tác task, hoặc dùng helper kiểm tra project active kết hợp membership.

### BUG-002 - Sai method cập nhật project so với test case

- Mức độ: Trung bình
- Test mẫu yêu cầu `PATCH /projects/{id}` nhưng source chỉ đăng ký `PUT /projects/{project_id}`.
- Đề xuất: Thống nhất đặc tả và source; nếu cần partial update thì thêm PATCH.

### BUG-003 - Thiếu pagination và sort cho task

- Mức độ: Trung bình
- Endpoint `GET /projects/{project_id}/tasks` hiện chỉ hỗ trợ filter/search.
- Đề xuất: Bổ sung `page`, `limit`, `sort_by`, `sort_order`.

### BUG-004 - Validation độ dài title không thống nhất

- Mức độ: Nhỏ
- `TaskCreate.title` cho phép tối đa 255 ký tự nhưng `TaskUpdate.title` chỉ cho phép tối đa 20 ký tự.
- Đề xuất: Dùng cùng một giới hạn, phù hợp với model database.

### BUG-005 - Validation tên project chưa thống nhất

- Mức độ: Nhỏ
- Schema chưa khai báo `min_length`/`max_length`; service kiểm tra tối đa 10 ký tự nhưng message ghi tối đa 20 ký tự.
- Đề xuất: Đưa validation vào schema và thống nhất giới hạn.

## 6. Route thực tế

- `POST /auth/register`
- `POST /auth/login`
- `GET /users/me`
- `GET /users`
- `POST /projects`
- `GET /projects`
- `GET /projects/{project_id}`
- `PUT /projects/{project_id}`
- `DELETE /projects/{project_id}`
- `GET /projects/{project_id}/members`
- `POST /projects/{project_id}/members`
- `DELETE /projects/{project_id}/members/{user_id}`
- `POST /projects/{project_id}/tasks`
- `GET /projects/{project_id}/tasks`
- `GET /tasks/{task_id}`
- `PATCH /tasks/{task_id}`
- `DELETE /tasks/{task_id}`
- `POST /tasks/{task_id}/comments`
- `POST /tasks/{task_id}/attachments`

## 7. Tổng kết

- Tổng số case đã ghi trong checklist: 76
- Đã PASS trực tiếp: 11
- Đã xác định FAIL: 5 vấn đề/rủi ro
- SOURCE, chưa chạy độc lập: nhiều case
- NOT RUN: các case cần nhiều user/member/assignee hoặc token hết hạn
- Automated test: chưa có

**Kết luận:** API hoạt động tốt ở luồng authentication cơ bản, user profile và một phần project validation. Chưa thể kết luận đạt toàn bộ yêu cầu vì còn lỗi soft-delete task, thiếu PATCH project, thiếu pagination/sort và chưa có bộ test tự động cho permission/cross-project.
