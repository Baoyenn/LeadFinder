# 🔍 LeadFinder — Full Stack Setup

## Cấu trúc dự án

```
leadfinder/
├── backend/          ← Flask API (Python)
│   ├── app.py
│   ├── requirements.txt
│   └── leads.json    ← tự tạo khi chạy
│
├── web-app/          ← Dashboard (HTML thuần, không cần build)
│   └── index.html
│
└── extension/        ← Chrome Extension
    ├── manifest.json
    ├── content.js    ← inject vào LinkedIn
    ├── popup.html
    ├── popup.js
    └── background.js
```

---

## Bước 1 — Chạy Backend (Flask)

```bash
cd backend

# Tạo virtual env (khuyến nghị)
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows

# Cài packages
pip install -r requirements.txt

# Chạy server
python app.py
```

Server sẽ chạy tại: **http://localhost:5000**

---

## Bước 2 — Mở Web App (Dashboard)

Cách 1 — Double click `web-app/index.html` để mở trong browser.

Cách 2 — Dùng Live Server (VS Code extension) để tự reload.

Cách 3 — Python simple server:
```bash
cd web-app
python -m http.server 3000
# Mở http://localhost:3000
```

---

## 🐳 Bước X — Chạy Bằng Docker (Dành Cho Team/Server)

Nếu bạn muốn treo hệ thống chạy 24/7 trên Server hoặc máy tính công ty mà không cần cài Python thủ công, bạn có thể dùng Docker:

```bash
# Đảm bảo bạn đã cài Docker và Docker Compose trên máy
# Chỉ cần đứng ở thư mục gốc của dự án (chứa file docker-compose.yml) và chạy:
docker-compose up -d --build
```

Lệnh trên sẽ:
1. Chạy Backend (Gunicorn + Flask) ở cổng `5000`. Dữ liệu `leads.json` được cấu hình lưu vào Volume nên sẽ **không bị mất** kể cả khi bạn tắt Docker.
2. Chạy Dashboard (Nginx) ở cổng `3000`.

Truy cập Dashboard: **http://localhost:3000**
Truy cập Backend API: **http://localhost:5000**

---

## Bước 3 — Cài Chrome Extension

1. Mở Chrome → địa chỉ: `chrome://extensions/`
2. Bật **Developer mode** (góc trên phải)
3. Nhấn **Load unpacked**
4. Chọn thư mục `extension/`
5. Extension **LeadFinder** xuất hiện trên toolbar

---

## Cách dùng Extension

### Crawl 1 profile:
1. Vào trang LinkedIn của ai đó: `linkedin.com/in/username`
2. Nhấn icon LeadFinder → **"Crawl this page"**
3. Hoặc nhấn nút nổi **"Crawl this page"** ở góc phải màn hình

### Crawl danh sách (Search results):
1. Vào `linkedin.com/search/results/people/...`
2. Nhấn icon LeadFinder → **"Crawl this page"**
3. Tool sẽ lấy tất cả profiles hiển thị trên trang

### Xem data:
- Mở Dashboard → data tự cập nhật mỗi 5 giây
- Nhấn **Export CSV** để tải file

---

## API Endpoints

| Method | URL | Mô tả |
|--------|-----|-------|
| GET | `/api/leads` | Lấy tất cả leads |
| POST | `/api/leads` | Thêm lead(s) mới |
| DELETE | `/api/leads/:id` | Xóa lead |
| POST | `/api/leads/:id/verify` | Verify lead |
| POST | `/api/leads/clear` | Xóa tất cả |
| GET | `/api/export/csv` | Download CSV |
| GET | `/api/stats` | Thống kê |

---

## Lưu ý quan trọng

- **CORS**: Backend đã bật CORS cho tất cả origins (dev mode)
- **LinkedIn rate limit**: Không crawl quá nhanh, tránh bị block
- **Data**: Lưu trong `backend/leads.json`, backup thường xuyên
- **Duplicate detection**: Dựa vào email + LinkedIn URL

---

## Troubleshooting

**Extension không gửi được data:**
- Kiểm tra Flask đang chạy: `http://localhost:5000/api/stats`
- Kiểm tra Console của Extension (F12 trên popup)

**LinkedIn không cho crawl:**
- LinkedIn thay đổi HTML selectors thường xuyên
- Cập nhật selectors trong `content.js` nếu cần

**CORS error:**
- Đảm bảo `flask-cors` đã cài: `pip install flask-cors`
