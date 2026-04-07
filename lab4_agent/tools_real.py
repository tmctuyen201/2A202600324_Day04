"""
tools_real.py — Real API version của các tools TravelBuddy

APIs sử dụng:
- Flights : Amadeus Self-Service API (free tier, 2000 req/month)
            https://developers.amadeus.com/self-service
- Hotels  : Google Places API (Text Search)
            https://developers.google.com/maps/documentation/places/web-service
- Budget  : Pure Python (không cần API)

Cấu hình trong .env:
    AMADEUS_API_KEY=...
    AMADEUS_API_SECRET=...
    GOOGLE_PLACES_API_KEY=...
"""

import os
import requests
from langchain_core.tools import tool
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────
# CITY → IATA CODE mapping (Vietnam)
# ─────────────────────────────────────────────
CITY_TO_IATA = {
    "hà nội": "HAN",
    "ha noi": "HAN",
    "đà nẵng": "DAD",
    "da nang": "DAD",
    "phú quốc": "PQC",
    "phu quoc": "PQC",
    "hồ chí minh": "SGN",
    "ho chi minh": "SGN",
    "sài gòn": "SGN",
    "sai gon": "SGN",
    "hcm": "SGN",
}

def _city_to_iata(city: str) -> str | None:
    return CITY_TO_IATA.get(city.lower().strip())


# ─────────────────────────────────────────────
# AMADEUS AUTH
# ─────────────────────────────────────────────
_amadeus_token: str | None = None

def _get_amadeus_token() -> str:
    global _amadeus_token
    if _amadeus_token:
        return _amadeus_token

    resp = requests.post(
        "https://test.api.amadeus.com/v1/security/oauth2/token",
        data={
            "grant_type": "client_credentials",
            "client_id": os.getenv("AMADEUS_API_KEY"),
            "client_secret": os.getenv("AMADEUS_API_SECRET"),
        },
        timeout=10,
    )
    resp.raise_for_status()
    _amadeus_token = resp.json()["access_token"]
    return _amadeus_token


# ─────────────────────────────────────────────
# TOOL 1: search_flights (Amadeus)
# ─────────────────────────────────────────────
@tool
def search_flights(origin: str, destination: str) -> str:
    """
    Tìm kiếm các chuyến bay giữa hai thành phố (dữ liệu thật từ Amadeus API).
    Tham số:
    - origin: thành phố khởi hành (VD: 'Hà Nội', 'Hồ Chí Minh')
    - destination: thành phố đến (VD: 'Đà Nẵng', 'Phú Quốc')
    Trả về danh sách chuyến bay với hãng, giờ bay, giá vé thực tế.
    """
    try:
        origin_iata = _city_to_iata(origin)
        dest_iata = _city_to_iata(destination)

        if not origin_iata:
            return f"Không nhận diện được thành phố khởi hành: '{origin}'. Hỗ trợ: Hà Nội, Đà Nẵng, Phú Quốc, Hồ Chí Minh."
        if not dest_iata:
            return f"Không nhận diện được thành phố đến: '{destination}'. Hỗ trợ: Hà Nội, Đà Nẵng, Phú Quốc, Hồ Chí Minh."

        from datetime import date, timedelta
        depart_date = (date.today() + timedelta(days=7)).isoformat()

        token = _get_amadeus_token()
        resp = requests.get(
            "https://test.api.amadeus.com/v2/shopping/flight-offers",
            headers={"Authorization": f"Bearer {token}"},
            params={
                "originLocationCode": origin_iata,
                "destinationLocationCode": dest_iata,
                "departureDate": depart_date,
                "adults": 1,
                "max": 5,
                "currencyCode": "VND",
            },
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json().get("data", [])

        if not data:
            return f"Không tìm thấy chuyến bay từ {origin} đến {destination} trong 7 ngày tới."

        result = f"✈️ Chuyến bay từ {origin} → {destination} (khởi hành ~{depart_date}):\n"
        result += "-" * 55 + "\n"

        for i, offer in enumerate(data, 1):
            seg = offer["itineraries"][0]["segments"][0]
            airline = seg["carrierCode"]
            dep_time = seg["departure"]["at"][11:16]
            arr_time = seg["arrival"]["at"][11:16]
            price_raw = float(offer["price"]["grandTotal"])
            price_fmt = f"{int(price_raw):,}".replace(",", ".")
            cabin = offer["travelerPricings"][0]["fareDetailsBySegment"][0].get("cabin", "ECONOMY").lower()
            result += f"{i}. {airline} | {dep_time} → {arr_time} | Hạng: {cabin} | Giá: {price_fmt}đ\n"

        return result

    except requests.HTTPError as e:
        return f"Lỗi API Amadeus ({e.response.status_code}): {e.response.text[:200]}"
    except Exception as e:
        return f"Lỗi khi tìm chuyến bay: {str(e)}"


# ─────────────────────────────────────────────
# TOOL 2: search_hotels (Google Places API)
# ─────────────────────────────────────────────
@tool
def search_hotels(city: str, max_price_per_night: int = 99_999_999) -> str:
    """
    Tìm kiếm khách sạn tại một thành phố (dữ liệu thật từ Google Places API).
    Tham số:
    - city: tên thành phố (VD: 'Đà Nẵng', 'Phú Quốc', 'Hồ Chí Minh')
    - max_price_per_night: giá tối đa mỗi đêm (VNĐ), mặc định không giới hạn
    Trả về danh sách khách sạn với tên, rating, địa chỉ.
    """
    try:
        api_key = os.getenv("GOOGLE_PLACES_API_KEY")
        if not api_key:
            return "Chưa cấu hình GOOGLE_PLACES_API_KEY trong .env"

        resp = requests.post(
            "https://places.googleapis.com/v1/places:searchText",
            headers={
                "Content-Type": "application/json",
                "X-Goog-Api-Key": api_key,
                "X-Goog-FieldMask": "places.displayName,places.rating,places.formattedAddress,places.priceLevel,places.userRatingCount",
            },
            json={
                "textQuery": f"khách sạn {city} Vietnam",
                "languageCode": "vi",
                "maxResultCount": 8,
            },
            timeout=15,
        )
        resp.raise_for_status()
        places = resp.json().get("places", [])

        if not places:
            return f"Không tìm thấy khách sạn tại {city}."

        # priceLevel: PRICE_LEVEL_INEXPENSIVE=1, MODERATE=2, EXPENSIVE=3, VERY_EXPENSIVE=4
        PRICE_ESTIMATE = {
            "PRICE_LEVEL_FREE": 0,
            "PRICE_LEVEL_INEXPENSIVE": 300_000,
            "PRICE_LEVEL_MODERATE": 800_000,
            "PRICE_LEVEL_EXPENSIVE": 2_000_000,
            "PRICE_LEVEL_VERY_EXPENSIVE": 4_000_000,
        }

        max_fmt = f"{max_price_per_night:,}".replace(",", ".")
        result = f"🏨 Khách sạn tại {city} (giá ≤ {max_fmt}đ/đêm — ước tính):\n"
        result += "-" * 55 + "\n"

        count = 0
        for p in places:
            price_level = p.get("priceLevel", "PRICE_LEVEL_MODERATE")
            est_price = PRICE_ESTIMATE.get(price_level, 800_000)

            if est_price > max_price_per_night:
                continue

            name = p["displayName"]["text"]
            rating = p.get("rating", "N/A")
            address = p.get("formattedAddress", "")
            reviews = p.get("userRatingCount", 0)
            est_fmt = f"{est_price:,}".replace(",", ".")

            count += 1
            result += f"{count}. {name}\n"
            result += f"   📍 {address}\n"
            result += f"   ⭐ {rating}/5 ({reviews} đánh giá) | Giá ước tính: ~{est_fmt}đ/đêm\n"

        if count == 0:
            return f"Không tìm thấy khách sạn tại {city} trong ngân sách {max_fmt}đ/đêm."

        result += "\n⚠️ Giá ước tính dựa theo mức giá Google Places, cần kiểm tra trực tiếp để có giá chính xác."
        return result

    except requests.HTTPError as e:
        return f"Lỗi Google Places API ({e.response.status_code}): {e.response.text[:200]}"
    except Exception as e:
        return f"Lỗi khi tìm khách sạn: {str(e)}"


# ─────────────────────────────────────────────
# TOOL 3: calculate_budget (pure Python, không đổi)
# ─────────────────────────────────────────────
@tool
def calculate_budget(total_budget: int, expenses: str) -> str:
    """
    Tính toán ngân sách còn lại sau khi trừ các khoản chi phí.
    Tham số:
    - total_budget: tổng ngân sách ban đầu (VNĐ)
    - expenses: chuỗi mô tả các khoản chi, mỗi khoản cách nhau bởi dấu phẩy,
      định dạng 'tên_khoản:số_tiền' (VD: 'vé_máy_bay:890000,khách_sạn:650000')
    """
    try:
        expense_dict = {}
        if expenses.strip():
            for item in expenses.split(","):
                item = item.strip()
                if ":" not in item:
                    return f"Lỗi định dạng: '{item}' không đúng dạng 'tên:số_tiền'."
                parts = item.split(":", 1)
                name = parts[0].strip().replace("_", " ")
                try:
                    amount = int(parts[1].strip())
                except ValueError:
                    return f"Lỗi: '{parts[1].strip()}' không phải số nguyên hợp lệ."
                expense_dict[name] = amount

        total_expense = sum(expense_dict.values())
        remaining = total_budget - total_expense

        def fmt(n: int) -> str:
            return f"{n:,}".replace(",", ".")

        result = "💰 Bảng chi phí:\n"
        result += "-" * 40 + "\n"
        for name, amount in expense_dict.items():
            result += f"  - {name.capitalize()}: {fmt(amount)}đ\n"
        result += "-" * 40 + "\n"
        result += f"  Tổng chi:  {fmt(total_expense)}đ\n"
        result += f"  Ngân sách: {fmt(total_budget)}đ\n"
        result += "-" * 40 + "\n"

        if remaining >= 0:
            result += f"  ✅ Còn lại:  {fmt(remaining)}đ\n"
        else:
            result += f"  ❌ Vượt ngân sách {fmt(abs(remaining))}đ! Cần điều chỉnh.\n"

        return result
    except Exception as e:
        return f"Lỗi khi tính ngân sách: {str(e)}"
