# PyPAKMA — Physics Simulation & Data Acquisition Studio

PyPAKMA là phiên bản chuyển đổi sang **Python** từ phần mềm mô phỏng vật lý **JPAKMA** (Đại học Würzburg, Đức).

---

## ⚡ Yêu cầu hệ thống (Prerequisites)
- **Python**: Phiên bản `3.10` trở lên (Khuyến nghị Python 3.12).
- **Hệ điều hành**: Windows 10/11, Linux hoặc macOS.

---

## 🚀 Cách 1: Chạy nhanh bằng 1-Click (Windows)
Chỉ cần nhấp đúp (Double-click) vào file:
```
run.bat
```
File này sẽ tự động kiểm tra, cài đặt toàn bộ thư viện trong `requirements.txt` và khởi chạy giao diện ứng dụng.

---

## 🛠️ Cách 2: Cài đặt và Chạy thủ công qua Terminal

### Bước 1: Mở Terminal tại thư mục `PyPAKMA`
```powershell
cd PyPAKMA
```

### Bước 2: Cài đặt các thư viện phụ thuộc
```powershell
pip install -r requirements.txt
```

### Bước 3: Khởi chạy ứng dụng
```powershell
python main.py
```

---

## 🧪 Chạy Kiểm thử (Unit Tests & Logging)

- Chạy bộ kiểm thử tự động:
  ```powershell
  python -m unittest tests/test_phase1.py -v
  ```
- Chạy và tự động xuất log báo cáo có timestamp:
  ```powershell
  python logs/testcase_runner.py
  ```

---

## 📦 Danh sách thư viện chính (`requirements.txt`)
- **PyQt6**: Khung giao diện đồ họa Desktop (GUI).
- **pyqtgraph**: Vẽ đồ thị khoa học thời gian thực tốc độ cao (60+ FPS).
- **numpy**: Bộ xử lý ma trận và giải phương trình vi phân số học (ODE RK4/Euler).
- **pyserial**: Giao tiếp cổng nối tiếp COM / Cảm biến phòng thí nghiệm.
