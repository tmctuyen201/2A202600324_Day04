from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, AIMessage, ToolMessage
from tools import search_flights, search_hotels, calculate_budget, calculate_days
from prompts import SYSTEM_PROMPT
from dotenv import load_dotenv
import os
import time
import json
import logging
from datetime import datetime
from pathlib import Path

load_dotenv()

# ─────────────────────────────────────────────
# SESSION FILE LOGGER
# ─────────────────────────────────────────────
_LOG_DIR = Path(__file__).parent / "logs"
_LOG_DIR.mkdir(exist_ok=True)

_session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
_log_file = _LOG_DIR / f"session_{_session_id}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[logging.FileHandler(_log_file, encoding="utf-8")],
)
_file_logger = logging.getLogger("travelbuddy")

def _flog(msg: str):
    """Write a line to the session log file."""
    _file_logger.info(msg)

# ─────────────────────────────────────────────
# 1. LOGGER
# ─────────────────────────────────────────────
class AgentLogger:
    def __init__(self, console_output: bool = True):
        self.step = 0
        self.turn = 0
        self.console_output = console_output
        self._logs: list = []

    def _log(self, message: str):
        if self.console_output:
            print(message)
        self._logs.append(message)
        _flog(message)

    def get_logs(self) -> list:
        return self._logs.copy()

    def reset_logs(self):
        self._logs = []

    def new_turn(self, user_input: str):
        self.turn += 1
        self.step = 0
        self._log("\n" + "─" * 60)
        self._log(f"📥 [Turn {self.turn}] User: {user_input}")
        self._log("─" * 60)

    def thinking(self):
        self.step += 1
        self._log(f"\n🧠 [Bước {self.step}] Agent đang suy nghĩ...")

    def direct_reply(self, content):
        if isinstance(content, list):
            content = "\n".join(
                part["text"] for part in content
                if isinstance(part, dict) and part.get("type") == "text"
            )
        preview = content[:120] + "..." if len(content) > 120 else content
        self._log(f"   └─ 💬 Trả lời trực tiếp (không cần tool)")
        self._log(f"   └─ Nội dung: \"{preview}\"")

    def tool_call(self, tool_name: str, args: dict):
        self.step += 1
        args_str = json.dumps(args, ensure_ascii=False)
        self._log(f"\n🔧 [Bước {self.step}] Gọi tool: {tool_name}")
        self._log(f"   └─ Tham số: {args_str}")

    def tool_result(self, tool_name: str, result: str, elapsed: float):
        lines = result.strip().split("\n")
        preview = "\n      ".join(lines[:6])
        if len(lines) > 6:
            preview += f"\n      ... (+{len(lines)-6} dòng)"
        self._log(f"   └─ ✅ Kết quả từ {tool_name} ({elapsed:.2f}s):")
        self._log(f"      {preview}")

    def summary(self, messages: list):
        tools_used = [m.name for m in messages if isinstance(m, ToolMessage)]
        self._log(f"\n📊 Tóm tắt lượt này:")
        self._log(f"   • Số lần LLM suy nghĩ : {self.step}")
        self._log(f"   • Số lần gọi tool     : {len(tools_used)}")
        if tools_used:
            self._log(f"   • Tools đã dùng       : {', '.join(tools_used)}")
        self._log("─" * 60)


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


# ─────────────────────────────────────────────
# 3. LLM & Tools (lazy init)
# ─────────────────────────────────────────────
tools_list = [search_flights, search_hotels, calculate_budget, calculate_days]
_original_tool_node = None

def _get_tool_node():
    global _original_tool_node
    if _original_tool_node is None:
        _original_tool_node = ToolNode(tools_list)
    return _original_tool_node

def _get_llm():
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    if provider == "gemini":
        return ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=os.getenv("GEMINI_API_KEY"),
            temperature=0.7,
        ).bind_tools(tools_list)
    else:
        return ChatOpenAI(
            model="gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0.7,
        ).bind_tools(tools_list)


# ─────────────────────────────────────────────
# 4. Graph builder helper
# ─────────────────────────────────────────────
def _build_graph(agent_logger: AgentLogger):
    """Build a compiled LangGraph with the given logger."""

    def _agent_node(state: AgentState):
        messages = state["messages"]
        if not isinstance(messages[0], SystemMessage):
            messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
        agent_logger.thinking()
        response = _get_llm().invoke(messages)
        if response.tool_calls:
            for tc in response.tool_calls:
                agent_logger.tool_call(tc["name"], tc["args"])
        else:
            agent_logger.direct_reply(response.content)
        return {"messages": [response]}

    def _tool_node(state: AgentState):
        start = time.time()
        result = _get_tool_node().invoke(state)
        elapsed = time.time() - start
        for msg in result["messages"]:
            if isinstance(msg, ToolMessage):
                agent_logger.tool_result(msg.name, msg.content, elapsed)
        return result

    b = StateGraph(AgentState)
    b.add_node("agent", _agent_node)
    b.add_node("tools", _tool_node)
    b.add_edge(START, "agent")
    b.add_conditional_edges("agent", tools_condition)
    b.add_edge("tools", "agent")
    return b.compile()


# ─────────────────────────────────────────────
# 5. CLI graph (built lazily on first CLI use)
# ─────────────────────────────────────────────
logger = AgentLogger(console_output=True)
_cli_graph = None

def _get_cli_graph():
    global _cli_graph
    if _cli_graph is None:
        _cli_graph = _build_graph(logger)
    return _cli_graph


# ─────────────────────────────────────────────
# 6. Conversation Memory
# ─────────────────────────────────────────────
class ConversationMemory:
    """Lưu trữ lịch sử hội thoại để truyền vào mỗi lần gọi LLM."""

    def __init__(self, max_turns: int = 20):
        self.max_turns = max_turns  # giới hạn để tránh context quá dài
        self._history: list = []    # list of (human_msg, ai_msg)

    def add(self, user_input: str, ai_response: str):
        self._history.append((user_input, ai_response))
        if len(self._history) > self.max_turns:
            self._history.pop(0)

    def get_messages(self) -> list:
        """Trả về list HumanMessage/AIMessage từ history."""
        from langchain_core.messages import HumanMessage, AIMessage
        msgs = []
        for human, ai in self._history:
            msgs.append(HumanMessage(content=human))
            msgs.append(AIMessage(content=ai))
        return msgs

    def clear(self):
        self._history = []

    def __len__(self):
        return len(self._history)


# ─────────────────────────────────────────────
# 7. Public API for Streamlit
# ─────────────────────────────────────────────
def run_agent_with_logs(
    user_input: str,
    memory: ConversationMemory | None = None,
    console_output: bool = False,
) -> dict:
    """
    Run the agent and return response + captured logs.

    Args:
        user_input: Câu hỏi của người dùng
        memory: ConversationMemory instance để giữ context hội thoại
        console_output: Có in ra console không

    Returns:
        {
            'response': str,
            'logs': list[str],
            'messages': list
        }
    """
    sl = AgentLogger(console_output=console_output)
    sl.new_turn(user_input)
    g = _build_graph(sl)

    # Ghép history + tin nhắn hiện tại
    history_msgs = memory.get_messages() if memory else []
    from langchain_core.messages import HumanMessage
    all_messages = history_msgs + [HumanMessage(content=user_input)]

    result = g.invoke({"messages": all_messages})
    sl.summary(result["messages"])

    final = result["messages"][-1]
    content = final.content
    if isinstance(content, list):
        content = "\n".join(
            part["text"] for part in content
            if isinstance(part, dict) and part.get("type") == "text"
        )

    # Lưu lượt này vào memory
    if memory is not None:
        memory.add(user_input, content)

    return {
        "response": content,
        "logs": sl.get_logs(),
        "messages": result["messages"],
    }


# ─────────────────────────────────────────────
# 7. CLI entry point
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  TravelBuddy — Trợ lý Du lịch Thông minh")
    print("  Gõ 'quit' để thoát | 'clear' để xóa lịch sử")
    print("=" * 60)

    cli_memory = ConversationMemory()

    while True:
        user_input = input("\nBạn: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            print("Tạm biệt! Chúc bạn có chuyến đi vui vẻ 🌟")
            break
        if user_input.lower() == "clear":
            cli_memory.clear()
            print("🗑️  Đã xóa lịch sử hội thoại.")
            continue

        logger.new_turn(user_input)
        result = run_agent_with_logs(user_input, memory=cli_memory, console_output=True)
        logger.summary(result["messages"])
        print(f"\n🤖 TravelBuddy:\n{result['response']}")
