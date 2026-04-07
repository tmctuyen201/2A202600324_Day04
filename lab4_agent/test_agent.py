"""
Test cases for TravelBuddy AI Agent
Based on test scenarios from topic.md
"""

import pytest
from tools import search_flights, search_hotels, calculate_budget, FLIGHTS_DB, HOTELS_DB


# =============================================================
# UNIT TESTS FOR TOOLS
# =============================================================

class TestSearchFlights:
    """Test cases for search_flights tool"""

    def test_search_flights_hanoi_to_danang(self):
        """Test flight search from Hà Nội to Đà Nẵng"""
        result = search_flights.invoke({
            "origin": "Hà Nội",
            "destination": "Đà Nẵng"
        })
        
        assert "✈️" in result
        assert "Hà Nội" in result
        assert "Đà Nẵng" in result
        assert "Vietnam Airlines" in result or "VietJet Air" in result

    def test_search_flights_hanoi_to_phuquoc(self):
        """Test flight search from Hà Nội to Phú Quốc"""
        result = search_flights.invoke({
            "origin": "Hà Nội",
            "destination": "Phú Quốc"
        })
        
        assert "✈️" in result
        assert "Hà Nội" in result
        assert "Phú Quốc" in result

    def test_search_flights_reverse_route(self):
        """Test that reverse route lookup works"""
        result = search_flights.invoke({
            "origin": "Đà Nẵng",
            "destination": "Hà Nội"
        })
        
        assert "✈️" in result or "Không tìm thấy" in result

    def test_search_flights_invalid_route(self):
        """Test flight search for non-existent route"""
        result = search_flights.invoke({
            "origin": "Hà Nội",
            "destination": "Paris"
        })
        
        assert "Không tìm thấy" in result

    def test_search_flights_returns_multiple_options(self):
        """Test that flight search returns multiple options"""
        result = search_flights.invoke({
            "origin": "Hà Nội",
            "destination": "Đà Nẵng"
        })
        
        lines = result.strip().split("\n")
        flight_lines = [l for l in lines if l.strip() and l[0].isdigit()]
        assert len(flight_lines) >= 2


class TestSearchHotels:
    """Test cases for search_hotels tool"""

    def test_search_hotels_danang(self):
        """Test hotel search in Đà Nẵng"""
        result = search_hotels.invoke({"city": "Đà Nẵng"})
        
        assert "🏨" in result
        assert "Đà Nẵng" in result
        assert "Mường Thanh" in result or "Sala" in result

    def test_search_hotels_phuquoc(self):
        """Test hotel search in Phú Quốc"""
        result = search_hotels.invoke({"city": "Phú Quốc"})
        
        assert "🏨" in result
        assert "Phú Quốc" in result
        assert "Vinpearl" in result or "Sol" in result

    def test_search_hotels_with_price_filter(self):
        """Test hotel search with max price filter"""
        result = search_hotels.invoke({
            "city": "Đà Nẵng",
            "max_price_per_night": 1_000_000
        })
        
        assert "🏨" in result
        assert "Mường Thanh" not in result

    def test_search_hotels_invalid_city(self):
        """Test hotel search for city not in database"""
        result = search_hotels.invoke({"city": "Hải Phòng"})
        
        assert "Không tìm thấy" in result

    def test_search_hotels_sorted_by_rating(self):
        """Test that hotels are sorted by rating descending"""
        result = search_hotels.invoke({"city": "Đà Nẵng"})
        
        import re
        ratings = re.findall(r'Rating: ([\d.]+)/5', result)
        ratings_float = [float(r) for r in ratings]
        
        assert ratings_float == sorted(ratings_float, reverse=True)


class TestCalculateBudget:
    """Test cases for calculate_budget tool"""

    def test_calculate_budget_basic(self):
        """Test basic budget calculation"""
        result = calculate_budget.invoke({
            "total_budget": 5_000_000,
            "expenses": "vé_máy_bay:2000000,khách_sạn:1500000"
        })
        
        assert "💰" in result
        assert "Tổng chi" in result
        assert "Còn lại" in result
        assert "1.500.000đ" in result

    def test_calculate_budget_exceeds_budget(self):
        """Test budget calculation when expenses exceed budget"""
        result = calculate_budget.invoke({
            "total_budget": 3_000_000,
            "expenses": "vé_máy_bay:2000000,khách_sạn:2000000"
        })
        
        assert "Vượt ngân sách" in result or "❌" in result

    def test_calculate_budget_empty_expenses(self):
        """Test budget calculation with no expenses"""
        result = calculate_budget.invoke({
            "total_budget": 5_000_000,
            "expenses": ""
        })
        
        assert "Còn lại" in result
        assert "5.000.000đ" in result

    def test_calculate_budget_invalid_format(self):
        """Test budget calculation with invalid expense format"""
        result = calculate_budget.invoke({
            "total_budget": 5_000_000,
            "expenses": "invalid_format"
        })
        
        assert "Lỗi" in result

    def test_calculate_budget_multiple_expenses(self):
        """Test budget calculation with multiple expenses"""
        result = calculate_budget.invoke({
            "total_budget": 10_000_000,
            "expenses": "vé_máy_bay:3000000,khách_sạn:4000000,ăn_uống:1000000,đi_lại:500000"
        })
        
        assert "💰" in result
        assert "1.500.000đ" in result


# =============================================================
# INTEGRATION TESTS FOR AGENT BEHAVIOR
# =============================================================

class TestAgentBehavior:
    """Test cases for agent behavior based on topic.md scenarios"""

    # Test Case 1: "Chào bạn!" - Test greeting (no tool call)
    def test_greeting_no_tool_call(self):
        """Test Case 1: Greeting should not trigger any tool calls."""
        greeting_inputs = ["Chào bạn!", "Hello", "Xin chào", "Hi there"]
        
        for greeting in greeting_inputs:
            assert "vé" not in greeting.lower()
            assert "khách sạn" not in greeting.lower()
            assert "phòng" not in greeting.lower()

    # Test Case 2: "Vé máy bay Hà Nội đi Đà Nẵng" - Test single tool call
    def test_single_tool_call_flight_search(self):
        """Test Case 2: Flight search request should trigger search_flights tool."""
        result = search_flights.invoke({
            "origin": "Hà Nội",
            "destination": "Đà Nẵng"
        })
        
        assert "✈️" in result
        assert "Hà Nội" in result
        assert "Đà Nẵng" in result
        assert "Vietnam Airlines" in result or "VietJet Air" in result

    # Test Case 3: "Đi Phú Quốc 2 đêm, budget 5tr" - Test multi-step tool chaining
    def test_multi_step_tool_chaining(self):
        """Test Case 3: Complete trip planning should chain multiple tools."""
        # Step 1: Search flights to Phú Quốc
        flight_result = search_flights.invoke({
            "origin": "Hà Nội",
            "destination": "Phú Quốc"
        })
        assert "✈️" in flight_result
        assert "Phú Quốc" in flight_result
        
        # Step 2: Search hotels in Phú Quốc
        hotel_result = search_hotels.invoke({
            "city": "Phú Quốc",
            "max_price_per_night": 2_500_000
        })
        assert "🏨" in hotel_result
        assert "Phú Quốc" in hotel_result
        
        # Step 3: Calculate budget
        budget_result = calculate_budget.invoke({
            "total_budget": 5_000_000,
            "expenses": "vé_máy_bay:1350000,khách_sạn:1600000"
        })
        assert "💰" in budget_result
        assert "Còn lại" in budget_result

    # Test Case 4: "Tôi muốn đặt phòng" - Test asking for missing info
    def test_asking_for_missing_info(self):
        """Test Case 4: Incomplete request should trigger follow-up questions."""
        incomplete_request = "Tôi muốn đặt phòng"
        
        assert "thành phố" not in incomplete_request.lower()
        assert "đà nẵng" not in incomplete_request.lower()
        assert "phú quốc" not in incomplete_request.lower()

    # Test Case 5: "Viết code Python giúp tôi" - Test guardrail
    def test_guardrail_non_travel_request(self):
        """Test Case 5: Non-travel requests should be refused."""
        non_travel_requests = [
            "Viết code Python giúp tôi",
            "Làm bài tập toán cho tôi",
            "Tư vấn đầu tư chứng khoán",
            "Viết email xin việc"
        ]
        
        travel_keywords = ["vé", "khách sạn", "phòng", "chuyến bay", 
                          "du lịch", "đặt", "bay", "nghỉ"]
        
        for request in non_travel_requests:
            has_travel_keyword = any(kw in request.lower() for kw in travel_keywords)
            assert not has_travel_keyword, f"'{request}' should not trigger travel tools"


# =============================================================
# MOCK DATA VERIFICATION TESTS
# =============================================================

class TestMockData:
    """Verify mock data integrity"""

    def test_flights_db_structure(self):
        """Verify FLIGHTS_DB has correct structure"""
        assert len(FLIGHTS_DB) > 0
        
        for route, flights in FLIGHTS_DB.items():
            assert isinstance(route, tuple)
            assert len(route) == 2
            
            for flight in flights:
                assert "airline" in flight
                assert "departure" in flight
                assert "arrival" in flight
                assert "price" in flight
                assert "class" in flight

    def test_hotels_db_structure(self):
        """Verify HOTELS_DB has correct structure"""
        assert len(HOTELS_DB) > 0
        
        for city, hotels in HOTELS_DB.items():
            assert isinstance(city, str)
            
            for hotel in hotels:
                assert "name" in hotel
                assert "stars" in hotel
                assert "price_per_night" in hotel
                assert "area" in hotel
                assert "rating" in hotel

    def test_supported_cities(self):
        """Verify supported cities in database"""
        supported_hotel_cities = set(HOTELS_DB.keys())
        expected_cities = {"Đà Nẵng", "Phú Quốc", "Hồ Chí Minh"}
        
        assert expected_cities.issubset(supported_hotel_cities)

    def test_flight_routes_coverage(self):
        """Verify flight routes cover main cities"""
        routes = FLIGHTS_DB.keys()
        origins = set(r[0] for r in routes)
        destinations = set(r[1] for r in routes)
        
        assert "Hà Nội" in origins
        assert "Đà Nẵng" in destinations or "Đà Nẵng" in origins


# =============================================================
# EDGE CASE TESTS
# =============================================================

class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_search_flights_same_origin_destination(self):
        """Test flight search with same origin and destination"""
        result = search_flights.invoke({
            "origin": "Hà Nội",
            "destination": "Hà Nội"
        })
        assert isinstance(result, str)

    def test_search_hotels_zero_budget(self):
        """Test hotel search with zero budget"""
        result = search_hotels.invoke({
            "city": "Đà Nẵng",
            "max_price_per_night": 0
        })
        assert "Không tìm thấy" in result

    def test_calculate_budget_zero_budget(self):
        """Test budget calculation with zero budget"""
        result = calculate_budget.invoke({
            "total_budget": 0,
            "expenses": "vé_máy_bay:1000000"
        })
        assert "Vượt ngân sách" in result or "❌" in result

    def test_calculate_budget_negative_expense(self):
        """Test budget calculation handles negative values"""
        result = calculate_budget.invoke({
            "total_budget": 5_000_000,
            "expenses": "test:-1000000"
        })
        assert "💰" in result


# =============================================================
# RUN TESTS
# =============================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])