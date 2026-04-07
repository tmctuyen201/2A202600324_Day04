"""
Chạy 5 test cases thực tế qua agent để lấy console log cho test_results.md
"""
import sys
import os
sys.stdout.reconfigure(encoding='utf-8')

from agent import run_agent_with_logs

TEST_CASES = [
    ("TC1 - Greeting (Persona, no tool)", "Chào bạn!"),
    ("TC2 - Single Tool Call (search_flights)", "Vé máy bay Hà Nội đi Đà Nẵng"),
    ("TC3 - Multi-step Tool Chaining", "Đi Phú Quốc 2 đêm, budget 5 triệu, xuất phát từ Hà Nội"),
    ("TC4 - Missing Info / Clarification", "Tôi muốn đặt khách sạn"),
    ("TC5 - Guardrail (refuse non-travel)", "Viết code Python giúp tôi"),
]

SEPARATOR = "=" * 70

for title, user_input in TEST_CASES:
    print(f"\n{SEPARATOR}")
    print(f"  {title}")
    print(f"  User: \"{user_input}\"")
    print(SEPARATOR)

    result = run_agent_with_logs(user_input, console_output=False)

    print("\n--- Agent Thinking Process ---")
    for log in result["logs"]:
        print(log)

    print("\n--- Final Response ---")
    print(f"🤖 TravelBuddy:\n{result['response']}")
    print()
