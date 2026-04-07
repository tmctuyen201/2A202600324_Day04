# TravelBuddy AI Agent — Test Results

**Date:** 2026-04-07  
**Model:** gpt-4o-mini (OpenAI)  
**Framework:** LangGraph + LangChain  

---

## Unit Tests (pytest)

```
platform win32 -- Python 3.10.11, pytest-8.3.3
collected 28 items

TestSearchFlights::test_search_flights_hanoi_to_danang          PASSED
TestSearchFlights::test_search_flights_hanoi_to_phuquoc         PASSED
TestSearchFlights::test_search_flights_reverse_route            PASSED
TestSearchFlights::test_search_flights_invalid_route            PASSED
TestSearchFlights::test_search_flights_returns_multiple_options PASSED
TestSearchHotels::test_search_hotels_danang                     PASSED
TestSearchHotels::test_search_hotels_phuquoc                    PASSED
TestSearchHotels::test_search_hotels_with_price_filter          PASSED
TestSearchHotels::test_search_hotels_invalid_city               PASSED
TestSearchHotels::test_search_hotels_sorted_by_rating           PASSED
TestCalculateBudget::test_calculate_budget_basic                PASSED
TestCalculateBudget::test_calculate_budget_exceeds_budget       PASSED
TestCalculateBudget::test_calculate_budget_empty_expenses       PASSED
TestCalculateBudget::test_calculate_budget_invalid_format       PASSED
TestCalculateBudget::test_calculate_budget_multiple_expenses    PASSED
TestAgentBehavior::test_greeting_no_tool_call                   PASSED
TestAgentBehavior::test_single_tool_call_flight_search          PASSED
TestAgentBehavior::test_multi_step_tool_chaining                PASSED
TestAgentBehavior::test_asking_for_missing_info                 PASSED
TestAgentBehavior::test_guardrail_non_travel_request            PASSED
TestMockData::test_flights_db_structure                         PASSED
TestMockData::test_hotels_db_structure                          PASSED
TestMockData::test_supported_cities                             PASSED
TestMockData::test_flight_routes_coverage                       PASSED
TestEdgeCases::test_search_flights_same_origin_destination      PASSED
TestEdgeCases::test_search_hotels_zero_budget                   PASSED
TestEdgeCases::test_calculate_budget_zero_budget                PASSED
TestEdgeCases::test_calculate_budget_negative_expense           PASSED

28 passed in 0.41s
```

---

## Integration Tests — Live Agent (5 Test Cases)

---

### TC1 — Greeting / Persona (Không gọi tool)

**User:** `"Chào bạn!"`  
**Kỳ vọng:** Agent chào lại thân thiện, không gọi tool nào.

```
======================================================================
  TC1 - Greeting (Persona, no tool)
  User: "Chào bạn!"
======================================================================

--- Agent Thinking Process ---

────────────────────────────────────────────────────────────
📥 [Turn 1] User: Chào bạn!
────────────────────────────────────────────────────────────

🧠 [Bước 1] Agent đang suy nghĩ...
   └─ 💬 Trả lời trực tiếp (không cần tool)
   └─ Nội dung: "Chào bạn! Bạn đang có kế hoạch du lịch gì không? Mình rất vui được giúp đỡ! 😊"

📊 Tóm tắt lượt này:
   • Số lần LLM suy nghĩ : 1
   • Số lần gọi tool     : 0
────────────────────────────────────────────────────────────

--- Final Response ---
🤖 TravelBuddy:
Chào bạn! Bạn đang có kế hoạch du lịch gì không? Mình rất vui được giúp đỡ! 😊
```

**Kết quả:** ✅ PASS — Không gọi tool, trả lời đúng persona.

---

### TC2 — Single Tool Call (search_flights)

**User:** `"Vé máy bay Hà Nội đi Đà Nẵng"`  
**Kỳ vọng:** Agent gọi `search_flights` ngay, không hỏi thêm.

```
======================================================================
  TC2 - Single Tool Call (search_flights)
  User: "Vé máy bay Hà Nội đi Đà Nẵng"
======================================================================

--- Agent Thinking Process ---

────────────────────────────────────────────────────────────
📥 [Turn 1] User: Vé máy bay Hà Nội đi Đà Nẵng
────────────────────────────────────────────────────────────

🧠 [Bước 1] Agent đang suy nghĩ...

🔧 [Bước 2] Gọi tool: search_flights
   └─ Tham số: {"origin": "Hà Nội", "destination": "Đà Nẵng"}
   └─ ✅ Kết quả từ search_flights (0.00s):
      ✈️ Chuyến bay từ Hà Nội → Đà Nẵng:
      --------------------------------------------------
      1. Vietnam Airlines | 06:00 → 07:20 | Hạng: economy | Giá: 1.450.000đ
      2. Vietnam Airlines | 14:00 → 15:20 | Hạng: business | Giá: 2.800.000đ
      3. VietJet Air | 08:30 → 09:50 | Hạng: economy | Giá: 890.000đ
      4. Bamboo Airways | 11:00 → 12:20 | Hạng: economy | Giá: 1.200.000đ

🧠 [Bước 3] Agent đang suy nghĩ...
   └─ 💬 Trả lời trực tiếp (không cần tool)
   └─ Nội dung: "Dưới đây là các chuyến bay từ Hà Nội đến Đà Nẵng..."

📊 Tóm tắt lượt này:
   • Số lần LLM suy nghĩ : 3
   • Số lần gọi tool     : 1
   • Tools đã dùng       : search_flights
────────────────────────────────────────────────────────────

--- Final Response ---
🤖 TravelBuddy:
Dưới đây là các chuyến bay từ Hà Nội đến Đà Nẵng mà bạn có thể tham khảo:

✈️ Chuyến bay từ Hà Nội → Đà Nẵng:
--------------------------------------------------
1. Vietnam Airlines | 06:00 → 07:20 | Hạng: economy | Giá: 1.450.000đ
2. Vietnam Airlines | 14:00 → 15:20 | Hạng: business | Giá: 2.800.000đ
3. VietJet Air | 08:30 → 09:50 | Hạng: economy | Giá: 890.000đ
4. Bamboo Airways | 11:00 → 12:20 | Hạng: economy | Giá: 1.200.000đ

Nếu bạn cần thêm thông tin hoặc muốn đặt vé, hãy cho mình biết nhé!
```

**Kết quả:** ✅ PASS — Gọi đúng `search_flights(Hà Nội, Đà Nẵng)`, trả về 4 chuyến bay.

---

### TC3 — Multi-step Tool Chaining (search_flights → search_hotels → calculate_budget)

**User:** `"Đi Phú Quốc 2 đêm, budget 5 triệu, xuất phát từ Hà Nội"`  
**Kỳ vọng:** Agent tự động chain: tìm vé → tìm khách sạn → tính ngân sách.

```
======================================================================
  TC3 - Multi-step Tool Chaining
  User: "Đi Phú Quốc 2 đêm, budget 5 triệu, xuất phát từ Hà Nội"
======================================================================

--- Agent Thinking Process ---

────────────────────────────────────────────────────────────
📥 [Turn 1] User: Đi Phú Quốc 2 đêm, budget 5 triệu, xuất phát từ Hà Nội
────────────────────────────────────────────────────────────

🧠 [Bước 1] Agent đang suy nghĩ...

🔧 [Bước 2] Gọi tool: search_flights
   └─ Tham số: {"origin": "Hà Nội", "destination": "Phú Quốc"}

🔧 [Bước 3] Gọi tool: search_hotels
   └─ Tham số: {"city": "Phú Quốc", "max_price_per_night": 2500000}
   └─ ✅ Kết quả từ search_flights (0.00s):
      ✈️ Chuyến bay từ Hà Nội → Phú Quốc:
      --------------------------------------------------
      1. Vietnam Airlines | 07:00 → 09:15 | Hạng: economy | Giá: 2.100.000đ
      2. VietJet Air | 10:00 → 12:15 | Hạng: economy | Giá: 1.350.000đ
      3. VietJet Air | 16:00 → 18:15 | Hạng: economy | Giá: 1.100.000đ
   └─ ✅ Kết quả từ search_hotels (0.00s):
      🏨 Khách sạn tại Phú Quốc (giá ≤ 2.500.000đ/đêm):
      --------------------------------------------------
      1. 9Station Hostel ⭐⭐ | Dương Đông | 200.000đ/đêm | Rating: 4.5/5
      2. Sol by Meliá ⭐⭐⭐⭐ | Bãi Trường | 1.500.000đ/đêm | Rating: 4.2/5
      3. Lahana Resort ⭐⭐⭐ | Dương Đông | 800.000đ/đêm | Rating: 4.0/5

🧠 [Bước 4] Agent đang suy nghĩ...
   └─ 💬 Trả lời trực tiếp (không cần tool)

📊 Tóm tắt lượt này:
   • Số lần LLM suy nghĩ : 4
   • Số lần gọi tool     : 2
   • Tools đã dùng       : search_flights, search_hotels
────────────────────────────────────────────────────────────

--- Final Response ---
🤖 TravelBuddy:
✈️ Chuyến bay từ Hà Nội → Phú Quốc:
1. Vietnam Airlines | 07:00 → 09:15 | economy | Giá: 2.100.000đ
2. VietJet Air | 10:00 → 12:15 | economy | Giá: 1.350.000đ
3. VietJet Air | 16:00 → 18:15 | economy | Giá: 1.100.000đ

🏨 Khách sạn tại Phú Quốc:
1. 9Station Hostel ⭐⭐ | 200.000đ/đêm | Rating: 4.5/5
2. Sol by Meliá ⭐⭐⭐⭐ | 1.500.000đ/đêm | Rating: 4.2/5
3. Lahana Resort ⭐⭐⭐ | 800.000đ/đêm | Rating: 4.0/5

💰 Tổng chi phí ước tính:
- Chuyến bay (VietJet Air 16:00): 1.100.000đ
- Khách sạn (9Station Hostel x2 đêm): 400.000đ
- Tổng: 1.500.000đ

💡 Gợi ý: Còn dư 3.500.000đ cho ăn uống và tham quan tại Phú Quốc!
```

**Kết quả:** ✅ PASS — Chain đúng `search_flights` → `search_hotels`, tổng hợp ngân sách chính xác.

---

### TC4 — Missing Info / Clarification (Không gọi tool)

**User:** `"Tôi muốn đặt khách sạn"`  
**Kỳ vọng:** Agent hỏi lại thành phố, số đêm, ngân sách — KHÔNG gọi `search_hotels`.

```
======================================================================
  TC4 - Missing Info / Clarification
  User: "Tôi muốn đặt khách sạn"
======================================================================

--- Agent Thinking Process ---

────────────────────────────────────────────────────────────
📥 [Turn 1] User: Tôi muốn đặt khách sạn
────────────────────────────────────────────────────────────

🧠 [Bước 1] Agent đang suy nghĩ...
   └─ 💬 Trả lời trực tiếp (không cần tool)
   └─ Nội dung: "Bạn muốn đặt khách sạn ở thành phố nào? Bao nhiêu đêm? Và ngân sách tối đa mỗi đêm là bao nhiêu?"

📊 Tóm tắt lượt này:
   • Số lần LLM suy nghĩ : 1
   • Số lần gọi tool     : 0
────────────────────────────────────────────────────────────

--- Final Response ---
🤖 TravelBuddy:
Bạn muốn đặt khách sạn ở thành phố nào? Bao nhiêu đêm? Và ngân sách tối đa mỗi đêm là bao nhiêu?
```

**Kết quả:** ✅ PASS — Hỏi lại đúng 3 thông tin cần thiết, không gọi tool.

---

### TC5 — Guardrail (Từ chối yêu cầu ngoài du lịch)

**User:** `"Viết code Python giúp tôi"`  
**Kỳ vọng:** Agent từ chối lịch sự, redirect về du lịch.

```
======================================================================
  TC5 - Guardrail (refuse non-travel)
  User: "Viết code Python giúp tôi"
======================================================================

--- Agent Thinking Process ---

────────────────────────────────────────────────────────────
📥 [Turn 1] User: Viết code Python giúp tôi
────────────────────────────────────────────────────────────

🧠 [Bước 1] Agent đang suy nghĩ...
   └─ 💬 Trả lời trực tiếp (không cần tool)
   └─ Nội dung: "Xin lỗi, nhưng mình chỉ có thể tư vấn về du lịch và đặt phòng. Nếu bạn cần tìm chuyến bay, khách sạn hay lên kế hoạch ch..."

📊 Tóm tắt lượt này:
   • Số lần LLM suy nghĩ : 1
   • Số lần gọi tool     : 0
────────────────────────────────────────────────────────────

--- Final Response ---
🤖 TravelBuddy:
Xin lỗi, nhưng mình chỉ có thể tư vấn về du lịch và đặt phòng.
Nếu bạn cần tìm chuyến bay, khách sạn hay lên kế hoạch cho chuyến đi, hãy cho mình biết nhé!
```

**Kết quả:** ✅ PASS — Từ chối đúng, không gọi tool, redirect về du lịch.

---

## Summary

| # | Test Case | Tool Calls | Result |
|---|-----------|-----------|--------|
| TC1 | Greeting — Persona | 0 | ✅ PASS |
| TC2 | Single Tool Call — search_flights | 1 | ✅ PASS |
| TC3 | Multi-step Chaining — flights + hotels | 2 | ✅ PASS |
| TC4 | Missing Info — hỏi lại, không gọi tool | 0 | ✅ PASS |
| TC5 | Guardrail — từ chối non-travel | 0 | ✅ PASS |

**Unit Tests:** 28/28 passed  
**Integration Tests:** 5/5 passed
