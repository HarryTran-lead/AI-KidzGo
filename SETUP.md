# Hướng dẫn chạy AI-KidzGo trên Rider

## Yêu cầu
- Python 3.8+ (đã có: Python 3.14.0)
- Rider IDE
- pip (package manager của Python)

## Các bước setup

### 1. Cài đặt dependencies
Mở terminal trong Rider hoặc PowerShell và chạy:
```bash
cd D:\KLTN\AI-KidzGo
pip install -r requirements.txt
```

### 2. Cấu hình Python Interpreter trong Rider
1. Mở **File > Settings** (hoặc `Ctrl+Alt+S`)
2. Vào **Project > Python Interpreter**
3. Chọn Python interpreter (Python 3.14.0)
4. Nếu chưa có, click **Add Interpreter** và chọn Python đã cài

### 3. Chạy project

#### Cách 1: Chạy từ terminal (Khuyến nghị)
```bash
cd D:\KLTN\AI-KidzGo
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Cách 2: Tạo Run Configuration trong Rider
1. Click **Run > Edit Configurations...**
2. Click **+** > **Python**
3. Điền thông tin:
   - **Name**: `AI-KidzGo FastAPI`
   - **Script path**: `D:\KLTN\AI-KidzGo\app\main.py`
   - **Parameters**: (để trống)
   - **Working directory**: `D:\KLTN\AI-KidzGo`
   - **Python interpreter**: Chọn Python 3.14.0
4. Hoặc dùng uvicorn:
   - **Module name**: `uvicorn`
   - **Parameters**: `app.main:app --reload --host 0.0.0.0 --port 8000`
   - **Working directory**: `D:\KLTN\AI-KidzGo`

### 4. Truy cập Swagger UI
Sau khi chạy, mở trình duyệt:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health check**: http://localhost:8000/health

## API Endpoints

- `POST /a6/generate-monthly-report` - Generate monthly report
- `POST /a7/...` - Receipts endpoints
- `POST /a3/...` - Homework endpoints
- `POST /a8/...` - Speaking/Phonics endpoints

## Lưu ý
- Project này là **FastAPI service** (không phải .NET)
- Swagger UI tự động có sẵn tại `/docs`
- Cần có **Google Gemini API key** trong environment variables nếu dùng AI features

