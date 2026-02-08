# Quick Start - Chạy AI-KidzGo

## 🐍 PyCharm (Khuyến nghị - Dễ nhất) ✅

PyCharm là IDE chuyên dụng cho Python, rất dễ chạy FastAPI project.

### Bước 1: Mở Project
1. **Mở PyCharm**
2. **File > Open** (hoặc `Ctrl + O`)
3. Chọn folder: `D:\KLTN\AI-KidzGo`
4. PyCharm sẽ tự động detect Python project

### Bước 2: Cấu hình Python Interpreter
1. **File > Settings** (hoặc `Ctrl + Alt + S`)
2. **Project: AI-KidzGo > Python Interpreter**
3. Nếu chưa có interpreter:
   - Click dropdown > `Add Interpreter`
   - Chọn `System Interpreter`
   - Chọn Python 3.14.0 (hoặc version bạn đã cài)
   - Click `OK`

### Bước 3: Cài đặt Dependencies
1. **Mở Terminal trong PyCharm:**
   - `Alt + F12` hoặc `View > Tool Windows > Terminal`
2. **Chạy lệnh:**
   ```bash
   pip install -r requirements.txt
   ```

### Bước 4: Chạy Project

**Cách A: Chạy trực tiếp từ file (Đơn giản nhất)**
1. Mở file `app/main.py`
2. Click chuột phải vào file > `Run 'main'`
   - Hoặc click vào icon ▶️ bên cạnh dòng `if __name__ == "__main__":` (nếu có)
   - Hoặc nhấn `Shift + F10`

**Cách B: Tạo Run Configuration (Chuyên nghiệp hơn)**
1. **Run > Edit Configurations...**
2. Click `+` > `Python`
3. Điền thông tin:
   ```
   Name: AI-KidzGo FastAPI
   Script path: D:\KLTN\AI-KidzGo\app\main.py
   Working directory: D:\KLTN\AI-KidzGo
   Python interpreter: (chọn Python 3.14.0)
   ```
4. **HOẶC dùng uvicorn module (Khuyến nghị):**
   - Click `+` > `Python`
   - Chọn tab `Module name` thay vì `Script path`
   - Điền:
     ```
     Name: AI-KidzGo FastAPI
     Module name: uvicorn
     Parameters: app.main:app --reload --host 0.0.0.0 --port 8000
     Working directory: D:\KLTN\AI-KidzGo
     ```
5. Click `OK`
6. Chạy: Click `Run` hoặc nhấn `Shift + F10`

### Bước 5: Kiểm tra
- ✅ Server chạy tại: http://localhost:8000
- ✅ Swagger UI: http://localhost:8000/docs
- ✅ Health check: http://localhost:8000/health

---

## 🚀 Rider (IDE cho .NET)

### Cách 1: Chạy từ Terminal (Đơn giản nhất) ✅

1. **Mở Terminal trong Rider:**
   - Nhấn `Alt + F12` 
   - Hoặc `View > Tool Windows > Terminal`

2. **Chạy lệnh:**
   ```powershell
   cd D:\KLTN\AI-KidzGo
   pip install -r requirements.txt
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Mở Swagger:**
   - Mở trình duyệt: http://localhost:8000/docs

---

## Cách 2: Tạo Run Configuration

1. **Mở Run Configurations:**
   - Click vào dropdown "Run" ở toolbar (góc trên bên phải)
   - Chọn `Edit Configurations...`
   - Hoặc `Run > Edit Configurations...`

2. **Tạo Python Configuration:**
   - Click `+` (Add New Configuration)
   - Chọn `Python`
   - Điền thông tin:
     ```
     Name: AI-KidzGo FastAPI
     Script path: D:\KLTN\AI-KidzGo\app\main.py
     Working directory: D:\KLTN\AI-KidzGo
     Python interpreter: (chọn Python 3.14.0)
     ```

3. **HOẶC dùng uvicorn module:**
   - Click `+` > `Python`
   - Chọn tab `Module name` thay vì `Script path`
   - Điền:
     ```
     Name: AI-KidzGo FastAPI
     Module name: uvicorn
     Parameters: app.main:app --reload --host 0.0.0.0 --port 8000
     Working directory: D:\KLTN\AI-KidzGo
     ```

4. **Chạy:**
   - Click `Run` hoặc nhấn `Shift + F10`

---

## Cách 3: Chạy script .bat

1. **Trong File Explorer:**
   - Double-click `run.bat` trong folder `D:\KLTN\AI-KidzGo`

2. **Hoặc từ Terminal:**
   ```powershell
   cd D:\KLTN\AI-KidzGo
   .\run.bat
   ```

---

## Kiểm tra Python Interpreter trong Rider

Nếu cần cấu hình Python:

1. **Mở Settings:**
   - `File > Settings` (hoặc `Ctrl + Alt + S`)

2. **Tìm Python:**
   - Trong search box, gõ: `python`
   - Hoặc vào: `Build, Execution, Deployment > Python`

3. **Chọn Interpreter:**
   - Nếu chưa có, click `Add Interpreter`
   - Chọn `System Interpreter`
   - Chọn Python 3.14.0

---

## Lưu ý

- **PyCharm**: IDE chuyên dụng cho Python, rất dễ dùng ✅ (Khuyến nghị)
- **Rider**: IDE cho .NET, nhưng vẫn hỗ trợ Python (cần cài Python plugin)
- **Cách đơn giản nhất với PyCharm**: Mở file `app/main.py` > Click Run ▶️
- **Cách đơn giản nhất với Rider**: Dùng Terminal (Alt+F12)

---

## Sau khi chạy thành công

- ✅ Server chạy tại: http://localhost:8000
- ✅ Swagger UI: http://localhost:8000/docs
- ✅ Health check: http://localhost:8000/health

