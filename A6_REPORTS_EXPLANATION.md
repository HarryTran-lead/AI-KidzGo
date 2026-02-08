# Giải thích API A6 Reports - Cách hoạt động

## 📋 Tổng quan

API A6 Reports (`POST /a6/generate-monthly-report`) là một **stateless API service** - tức là:
- ✅ **Nhận data từ request body** (không đọc từ database)
- ✅ **Generate report bằng AI (Gemini) hoặc rule-based**
- ✅ **Trả về kết quả trong response** (không lưu vào database)
- ❌ **KHÔNG tự động lưu vào database**

---

## 🔄 Luồng hoạt động hiện tại

### 1. **Backend .NET gọi API A6**

Khi backend .NET cần generate monthly report:

```
Backend .NET
    ↓
1. Aggregate data từ database (attendance, homework, test, mission, session reports)
    ↓
2. Tạo request body với:
   - Student info
   - Session feedbacks (từ SessionReports)
   - Recent reports (3 tháng gần nhất)
   - Teacher notes
    ↓
3. Gọi POST /a6/generate-monthly-report
    ↓
4. Nhận response với draft_text và sections
    ↓
5. Lưu vào database (StudentMonthlyReport.DraftContent)
```

### 2. **API A6 xử lý**

```python
# app/agents/a6_reports/service.py

1. Nhận request body:
   - student: {student_id, name, age, program}
   - range: {from_date, to_date}
   - session_feedbacks: [{date, text}, ...]
   - recent_reports: [{month, overview, strengths, ...}, ...]
   - teacher_notes: string

2. Xử lý:
   - Nếu có Gemini API key → Dùng AI để generate
   - Nếu không có hoặc AI fail → Dùng rule-based (keyword matching)

3. Trả về response:
   {
     "ai_used": true/false,
     "draft_text": "string (formatted text)",
     "sections": {
       "overview": "...",
       "strengths": ["...", "...", "..."],
       "improvements": ["...", "...", "..."],
       "highlights": ["...", "..."],
       "goals_next_month": ["...", "...", "..."],
       "source_summary": {"total_feedbacks": 10, "days_covered": 10}
     }
   }
```

---

## 📊 Data flow

### **Input Data (từ Backend .NET):**

```json
{
  "student": {
    "student_id": "uuid",
    "name": "Nguyễn Văn A",
    "age": 8,
    "program": "KidzGo 1"
  },
  "range": {
    "from_date": "2024-01-01",
    "to_date": "2024-01-31"
  },
  "session_feedbacks": [
    {
      "date": "2024-01-15",
      "text": "Học viên tiến bộ tốt, phát âm rõ ràng hơn."
    },
    {
      "date": "2024-01-22",
      "text": "Cần luyện tập thêm phần nghe hiểu."
    }
  ],
  "recent_reports": [
    {
      "month": "2023-12",
      "overview": "...",
      "strengths": ["...", "..."],
      "improvements": ["...", "..."]
    }
  ],
  "teacher_notes": "Ghi chú bổ sung từ giáo viên",
  "language": "vi"
}
```

### **Output (trả về cho Backend .NET):**

```json
{
  "ai_used": true,
  "draft_text": "1) Tổng quan:\n...\n\n2) Điểm mạnh:\n- ...\n- ...",
  "sections": {
    "overview": "Trong tháng 1/2024, Nguyễn Văn A...",
    "strengths": [
      "Phát âm rõ ràng và tự tin hơn",
      "Tham gia tích cực trong lớp",
      "Hoàn thành bài tập đúng hạn"
    ],
    "improvements": [
      "Cần luyện tập thêm phần nghe hiểu",
      "Tăng tốc độ phản xạ khi giao tiếp",
      "Củng cố từ vựng theo chủ đề"
    ],
    "highlights": [
      "Học viên tiến bộ tốt, phát âm rõ ràng hơn.",
      "Có thái độ học tập tích cực."
    ],
    "goals_next_month": [
      "Duy trì thói quen luyện tập ngắn mỗi ngày (5–10 phút)",
      "Tập trung 1–2 mục tiêu cụ thể",
      "Hoàn thành bài tập đúng hạn"
    ],
    "source_summary": {
      "total_feedbacks": 10,
      "days_covered": 10
    }
  }
}
```

---

## 💾 Lưu trữ dữ liệu

### **API A6 KHÔNG lưu vào database**

API A6 chỉ là một **stateless service** - nó:
- Nhận request → Xử lý → Trả về response
- **KHÔNG** có kết nối database
- **KHÔNG** lưu kết quả vào file hay database

### **Backend .NET lưu kết quả**

Sau khi nhận response từ A6, backend .NET sẽ:
1. Lưu `draft_text` vào `StudentMonthlyReport.DraftContent` (jsonb)
2. Lưu `sections` vào `StudentMonthlyReport.DraftContent` (jsonb)
3. Có thể lưu thêm metadata vào các bảng khác

---

## 🔗 Tích hợp với Backend .NET

### **Hiện tại:**

Interface `IAiReportGenerator` đã được định nghĩa trong:
- `Kidzgo.Application/Abstraction/Reports/IAiReportGenerator.cs`

**Nhưng chưa có implementation thực tế!**

### **Cần implement:**

1. **Tạo class `HttpAiReportGenerator`** (hoặc `PythonAiReportGenerator`):
   ```csharp
   public class HttpAiReportGenerator : IAiReportGenerator
   {
       private readonly HttpClient _httpClient;
       
       public async Task<string> GenerateDraftAsync(
           string dataJson,
           string studentName,
           int month,
           int year,
           CancellationToken cancellationToken)
       {
           // 1. Parse dataJson để lấy session_feedbacks, recent_reports, etc.
           // 2. Tạo request body theo schema của A6
           // 3. Gọi POST /a6/generate-monthly-report
           // 4. Parse response và trả về draft_text hoặc sections JSON
       }
   }
   ```

2. **Register trong DependencyInjection:**
   ```csharp
   services.AddHttpClient<IAiReportGenerator, HttpAiReportGenerator>(client =>
   {
       client.BaseAddress = new Uri(configuration["AiService:BaseUrl"]!);
       client.Timeout = TimeSpan.FromMinutes(5);
   });
   ```

3. **Sử dụng trong command handler:**
   - Khi cần generate draft cho monthly report
   - Gọi `_aiReportGenerator.GenerateDraftAsync(...)`
   - Lưu kết quả vào `StudentMonthlyReport.DraftContent`

---

## 🧪 Test API A6

### **Cách test trực tiếp:**

1. **Mở Swagger:** http://localhost:8000/docs
2. **Chọn endpoint:** `POST /a6/generate-monthly-report`
3. **Click "Try it out"**
4. **Điền request body:**
   ```json
   {
     "student": {
       "student_id": "test-123",
       "name": "Nguyễn Văn A",
       "age": 8,
       "program": "KidzGo 1"
     },
     "range": {
       "from_date": "2024-01-01",
       "to_date": "2024-01-31"
     },
     "session_feedbacks": [
       {
         "date": "2024-01-15",
         "text": "Học viên tiến bộ tốt, phát âm rõ ràng hơn."
       }
     ],
     "recent_reports": [],
     "teacher_notes": null,
     "language": "vi"
   }
   ```
5. **Click "Execute"**
6. **Xem response** với `draft_text` và `sections`

---

## ⚙️ Cấu hình

### **Gemini API Key:**

Để dùng AI (thay vì rule-based), cần set environment variable:
```bash
GEMINI_API_KEY=your_api_key_here
```

Hoặc trong file `.env`:
```
GEMINI_API_KEY=your_api_key_here
```

### **Fallback behavior:**

- Nếu **không có Gemini API key** → Dùng rule-based (keyword matching)
- Nếu **AI call fail** → Fallback về rule-based
- Nếu **không có session_feedbacks** → Vẫn generate với default messages

---

## 📝 Tóm tắt

| Câu hỏi | Trả lời |
|---------|---------|
| **Data từ đâu?** | Từ request body (backend .NET gửi lên) |
| **Có data sẵn không?** | Không, phải gửi từ backend .NET |
| **Có lưu vào database không?** | ❌ Không, API này stateless |
| **Ai lưu kết quả?** | Backend .NET sau khi nhận response |
| **Có thể test trực tiếp không?** | ✅ Có, qua Swagger với mock data |

---

## 🚀 Next Steps

1. ✅ API A6 đã sẵn sàng và chạy được
2. ⏳ Cần implement `HttpAiReportGenerator` trong backend .NET
3. ⏳ Tích hợp vào `UpdateMonthlyReportDraft` hoặc tạo command mới để generate draft
4. ⏳ Test end-to-end flow: Backend → A6 API → Backend lưu kết quả

