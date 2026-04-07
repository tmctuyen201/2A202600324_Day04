from langchain_core.tools import tool

# =============================================================
# MOCK DATA — Dữ liệu giả lập hệ thống du lịch
# Lưu ý: Giá cả có logic (VD: cuối tuần đắt hơn, hạng cao hơn đắt hơn)
# =============================================================

FLIGHTS_DB = {
    ("Hà Nội", "Đà Nẵng"): [
        {"airline": "Vietnam Airlines", "departure": "06:00", "arrival": "07:20", "price": 1_450_000, "class": "economy"},
        {"airline": "Vietnam Airlines", "departure": "14:00", "arrival": "15:20", "price": 2_800_000, "class": "business"},
        {"airline": "VietJet Air",      "departure": "08:30", "arrival": "09:50", "price": 890_000,   "class": "economy"},
        {"airline": "Bamboo Airways",   "departure": "11:00", "arrival": "12:20", "price": 1_200_000, "class": "economy"},
    ],
    ("Hà Nội", "Phú Quốc"): [
        {"airline": "Vietnam Airlines", "departure": "07:00", "arrival": "09:15", "price": 2_100_000, "class": "economy"},
        {"airline": "VietJet Air",      "departure": "10:00", "arrival": "12:15", "price": 1_350_000, "class": "economy"},
        {"airline": "VietJet Air",      "departure": "16:00", "arrival": "18:15", "price": 1_100_000, "class": "economy"},
    ],
    ("Hà Nội", "Hồ Chí Minh"): [
        {"airline": "Vietnam Airlines", "departure": "06:00", "arrival": "08:10", "price": 1_600_000, "class": "economy"},
        {"airline": "VietJet Air",      "departure": "07:30", "arrival": "09:40", "price": 950_000,   "class": "economy"},
        {"airline": "Bamboo Airways",   "departure": "12:00", "arrival": "14:10", "price": 1_300_000, "class": "economy"},
        {"airline": "Vietnam Airlines", "departure": "18:00", "arrival": "20:10", "price": 3_200_000, "class": "business"},
    ],
    ("Hồ Chí Minh", "Đà Nẵng"): [
        {"airline": "Vietnam Airlines", "departure": "09:00", "arrival": "10:20", "price": 1_300_000, "class": "economy"},
        {"airline": "VietJet Air",      "departure": "13:00", "arrival": "14:20", "price": 780_000,   "class": "economy"},
    ],
    ("Hồ Chí Minh", "Phú Quốc"): [
        {"airline": "Vietnam Airlines", "departure": "08:00", "arrival": "09:00", "price": 1_100_000, "class": "economy"},
        {"airline": "VietJet Air",      "departure": "15:00", "arrival": "16:00", "price": 650_000,   "class": "economy"},
    ],
}

HOTELS_DB = {
    "Đà Nẵng": [
        {"name": "Mường Thanh Luxury",   "stars": 5, "price_per_night": 1_800_000, "area": "Mỹ Khê",    "rating": 4.5},
        {"name": "Sala Danang Beach",    "stars": 4, "price_per_night": 1_200_000, "area": "Mỹ Khê",    "rating": 4.3},
        {"name": "Fivitel Danang",       "stars": 3, "price_per_night": 650_000,   "area": "Sơn Trà",   "rating": 4.1},
        {"name": "Memory Hostel",        "stars": 2, "price_per_night": 250_000,   "area": "Hải Châu",  "rating": 4.6},
        {"name": "Christina's Homestay", "stars": 2, "price_per_night": 350_000,   "area": "An Thượng", "rating": 4.7},
    ],
    "Phú Quốc": [
        {"name": "Vinpearl Resort",   "stars": 5, "price_per_night": 3_500_000, "area": "Bãi Dài",    "rating": 4.4},
        {"name": "Sol by Meliá",      "stars": 4, "price_per_night": 1_500_000, "area": "Bãi Trường", "rating": 4.2},
        {"name": "Lahana Resort",     "stars": 3, "price_per_night": 800_000,   "area": "Dương Đông", "rating": 4.0},
        {"name": "9Station Hostel",   "stars": 2, "price_per_night": 200_000,   "area": "Dương Đông", "rating": 4.5},
    ],
    "Hồ Chí Minh": [
        {"name": "Rex Hotel",          "stars": 5, "price_per_night": 2_800_000, "area": "Quận 1", "rating": 4.3},
        {"name": "Liberty Central",    "stars": 4, "price_per_night": 1_400_000, "area": "Quận 1", "rating": 4.1},
        {"name": "Cochin Zen Hotel",   "stars": 3, "price_per_night": 550_000,   "area": "Quận 3", "rating": 4.4},
        {"name": "The Common Room",    "stars": 2, "price_per_night": 180_000,   "area": "Quận 1", "rating": 4.6},
    ],
}


@tool
def search_flights(origin: str, destination: str) -> str:
    """
    Tìm kiếm các chuyến bay giữa hai thành phố.
    Tham số:
    - origin: thành phố khởi hành (VD: 'Hà Nội', 'Hồ Chí Minh')
    - destination: thành phố đến (VD: 'Đà Nẵng', 'Phú Quốc')
    Trả về danh sách chuyến bay với hãng, giờ bay, giá vé.
    Nếu không tìm thấy tuyến bay, trả về thông báo không có chuyến.
    """
    try:
        # Tra cứu chiều đi
        flights = FLIGHTS_DB.get((origin, destination))

        # Nếu không có, thử chiều ngược lại
        if not flights:
            flights = FLIGHTS_DB.get((destination, origin))
            if flights:
                # Đổi chiều để thông báo đúng
                origin, destination = destination, origin

        if not flights:
            return f"Không tìm thấy chuyến bay từ {origin} đến {destination}."

        result = f"✈️ Chuyến bay từ {origin} → {destination}:\n"
        result += "-" * 50 + "\n"
        for i, f in enumerate(flights, 1):
            price_fmt = f"{f['price']:,}".replace(",", ".")
            result += (
                f"{i}. {f['airline']} | {f['departure']} → {f['arrival']} | "
                f"Hạng: {f['class']} | Giá: {price_fmt}đ\n"
            )
        return result
    except Exception as e:
        return f"Lỗi khi tìm chuyến bay: {str(e)}"


@tool
def search_hotels(city: str, max_price_per_night: int = 99_999_999) -> str:
    """
    Tìm kiếm khách sạn tại một thành phố, có thể lọc theo giá tối đa mỗi đêm.
    Tham số:
    - city: tên thành phố (VD: 'Đà Nẵng', 'Phú Quốc', 'Hồ Chí Minh')
    - max_price_per_night: giá tối đa mỗi đêm (VNĐ), mặc định không giới hạn
    Trả về danh sách khách sạn phù hợp với tên, số sao, giá, khu vực, rating.
    """
    try:
        hotels = HOTELS_DB.get(city)
        if not hotels:
            return f"Không tìm thấy dữ liệu khách sạn tại {city}."

        # Lọc theo giá tối đa
        filtered = [h for h in hotels if h["price_per_night"] <= max_price_per_night]

        if not filtered:
            max_fmt = f"{max_price_per_night:,}".replace(",", ".")
            return (
                f"Không tìm thấy khách sạn tại {city} với giá dưới {max_fmt}đ/đêm. "
                f"Hãy thử tăng ngân sách."
            )

        # Sắp xếp theo rating giảm dần
        filtered.sort(key=lambda h: h["rating"], reverse=True)

        max_fmt = f"{max_price_per_night:,}".replace(",", ".")
        result = f"🏨 Khách sạn tại {city} (giá ≤ {max_fmt}đ/đêm):\n"
        result += "-" * 50 + "\n"
        for i, h in enumerate(filtered, 1):
            price_fmt = f"{h['price_per_night']:,}".replace(",", ".")
            stars = "⭐" * h["stars"]
            result += (
                f"{i}. {h['name']} {stars}\n"
                f"   Khu vực: {h['area']} | Giá: {price_fmt}đ/đêm | Rating: {h['rating']}/5\n"
            )
        return result
    except Exception as e:
        return f"Lỗi khi tìm khách sạn: {str(e)}"


@tool
def calculate_budget(total_budget: int, expenses: str) -> str:
    """
    Tính toán ngân sách còn lại sau khi trừ các khoản chi phí.
    Tham số:
    - total_budget: tổng ngân sách ban đầu (VNĐ)
    - expenses: chuỗi mô tả các khoản chi, mỗi khoản cách nhau bởi dấu phẩy,
      định dạng 'tên_khoản:số_tiền' (VD: 'vé_máy_bay:890000,khách_sạn:650000')
    Trả về bảng chi tiết các khoản chi và số tiền còn lại.
    Nếu vượt ngân sách, cảnh báo rõ ràng số tiền thiếu.
    """
    try:
        # Parse chuỗi expenses thành dict
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

        # Tính tổng chi phí
        total_expense = sum(expense_dict.values())
        remaining = total_budget - total_expense

        # Format số tiền
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


@tool
def calculate_days(from_date: str, to_date: str) -> str:
    """
    Tính số ngày giữa hai mốc thời gian. Hỗ trợ:
    - Ngày cụ thể: 'dd/mm', 'dd/mm/yyyy', 'yyyy-mm-dd'
    - Từ khoá: 'hôm nay', 'ngày mai', 'thứ 2'..'thứ 7', 'chủ nhật',
               'tuần sau', 'cuối tuần', 'cuối tuần này', 'cuối tuần sau'
    Tham số:
    - from_date: ngày bắt đầu (VD: 'hôm nay', '20/04', '2026-04-20')
    - to_date:   ngày kết thúc (VD: 'chủ nhật', '25/04', 'thứ 6')
    Trả về số đêm, ngày đi và ngày về cụ thể.
    """
    from datetime import date, timedelta
    import re

    today = date.today()

    WEEKDAY_MAP = {
        "thứ 2": 0, "thứ hai": 0,
        "thứ 3": 1, "thứ ba": 1,
        "thứ 4": 2, "thứ tư": 2,
        "thứ 5": 3, "thứ năm": 3,
        "thứ 6": 4, "thứ sáu": 4,
        "thứ 7": 5, "thứ bảy": 5,
        "chủ nhật": 6, "cn": 6,
    }

    def next_weekday(target_wd: int, from_day: date) -> date:
        """Ngày gần nhất có weekday == target_wd, không tính from_day."""
        days_ahead = (target_wd - from_day.weekday()) % 7
        if days_ahead == 0:
            days_ahead = 7
        return from_day + timedelta(days=days_ahead)

    def parse(raw: str, anchor: date) -> date | None:
        s = raw.strip().lower()

        if s in ("hôm nay", "today"):
            return anchor
        if s in ("ngày mai", "tomorrow"):
            return anchor + timedelta(days=1)
        if s in ("ngày kia",):
            return anchor + timedelta(days=2)
        if s in ("cuối tuần", "cuối tuần này", "weekend"):
            # Thứ 7 gần nhất
            return next_weekday(5, anchor)
        if s in ("cuối tuần sau", "weekend sau"):
            return next_weekday(5, anchor) + timedelta(days=7)
        if s in ("tuần sau",):
            return anchor + timedelta(days=7)

        # Thứ trong tuần
        for kw, wd in WEEKDAY_MAP.items():
            if s == kw:
                return next_weekday(wd, anchor)

        # dd/mm hoặc dd/mm/yyyy
        m = re.fullmatch(r"(\d{1,2})/(\d{1,2})(?:/(\d{2,4}))?", s)
        if m:
            day, month = int(m.group(1)), int(m.group(2))
            year = int(m.group(3)) if m.group(3) else anchor.year
            if year < 100:
                year += 2000
            try:
                d = date(year, month, day)
                # Nếu ngày đã qua trong năm nay → sang năm sau
                if d < anchor and not m.group(3):
                    d = date(year + 1, month, day)
                return d
            except ValueError:
                return None

        # yyyy-mm-dd
        m2 = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", s)
        if m2:
            try:
                return date(int(m2.group(1)), int(m2.group(2)), int(m2.group(3)))
            except ValueError:
                return None

        return None

    try:
        d_from = parse(from_date, today)
        if d_from is None:
            return f"Không nhận diện được ngày bắt đầu: '{from_date}'"

        d_to = parse(to_date, d_from)
        if d_to is None:
            return f"Không nhận diện được ngày kết thúc: '{to_date}'"

        if d_to <= d_from:
            return f"Ngày kết thúc ({d_to.strftime('%d/%m/%Y')}) phải sau ngày bắt đầu ({d_from.strftime('%d/%m/%Y')})."

        nights = (d_to - d_from).days

        WEEKDAY_VI = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"]
        from_str = f"{WEEKDAY_VI[d_from.weekday()]}, {d_from.strftime('%d/%m/%Y')}"
        to_str   = f"{WEEKDAY_VI[d_to.weekday()]}, {d_to.strftime('%d/%m/%Y')}"

        return (
            f"📅 Kết quả tính ngày:\n"
            f"   Ngày đi  : {from_str}\n"
            f"   Ngày về  : {to_str}\n"
            f"   Số đêm   : {nights} đêm ({nights} ngày)\n"
        )
    except Exception as e:
        return f"Lỗi khi tính ngày: {str(e)}"
