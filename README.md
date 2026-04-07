# ✈️ TravelBuddy AI Agent

Trợ lý du lịch thông minh cho Việt Nam, xây dựng bằng LangGraph + Streamlit.

---

## Yêu cầu

- Python 3.10+
- OpenAI API key **hoặc** Google Gemini API key

---

## Cài đặt

**1. Clone repo**
```bash
git clone <repo-url>
cd 2A202600324_Day04
```

**2. Tạo virtual environment (khuyến nghị)**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

**3. Cài dependencies**
```bash
pip install -r requirements.txt
```

**4. Cấu hình API key**

Tạo file `.env` trong thư mục `lab4_agent/`:
```bash
cp lab4_agent/.env.example lab4_agent/.env
```

Mở `lab4_agent/.env` và điền key:
```env
# Chọn provider: "openai" hoặc "gemini"
LLM_PROVIDER=openai

OPENAI_API_KEY=sk-...
GEMINI_API_KEY=your_gemini_key_here
```

---

## Chạy ứng dụng

**Web UI (Streamlit) — khuyến nghị:**
```bash
streamlit run lab4_agent/app.py
```
Mở trình duyệt tại `http://localhost:8501`

**CLI mode:**
```bash
python lab4_agent/agent.py
```

---

## Chạy tests

```bash
pytest lab4_agent/test_agent.py -v -p no:asyncio
```

---

## Cấu trúc project

```
lab4_agent/
├── .env                # API keys (không commit)
├── app.py              # Streamlit web UI
├── agent.py            # LangGraph agent + logging
├── tools.py            # Tools: search_flights, search_hotels, calculate_budget
├── prompts.py          # System prompt
├── test_agent.py       # 28 test cases
├── logs/               # Session logs (tự động tạo)
└── system_prompt.txt   # (legacy, không dùng)
```

---

## Tính năng

| Tính năng | Mô tả |
|-----------|-------|
| 🔍 Tìm chuyến bay | Hà Nội, Đà Nẵng, Phú Quốc, Hồ Chí Minh |
| 🏨 Tìm khách sạn | Lọc theo thành phố và ngân sách |
| 💰 Tính ngân sách | Tổng hợp chi phí chuyến đi |
| 🔗 Tool chaining | Tự động chain nhiều tool cho trọn gói |
| 🛡️ Guardrail | Từ chối yêu cầu ngoài du lịch |
| 📋 Session logs | Ghi log mỗi session vào `logs/` |
| ⚙️ Multi-provider | Đổi OpenAI ↔ Gemini ngay trên UI |

---

## Test cases

| # | Input | Kỳ vọng |
|---|-------|---------|
| TC1 | "Chào bạn!" | Chào lại, không gọi tool |
| TC2 | "Vé máy bay Hà Nội đi Đà Nẵng" | Gọi `search_flights` |
| TC3 | "Đi Phú Quốc 2 đêm, budget 5tr" | Chain: flights → hotels → budget |
| TC4 | "Tôi muốn đặt khách sạn" | Hỏi lại thành phố/đêm/ngân sách |
| TC5 | "Viết code Python giúp tôi" | Từ chối, redirect về du lịch |
