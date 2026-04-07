# Project Structure

```
lab4_agent/
├── .env                # Environment variables (GEMINI_API_KEY)
├── system_prompt.txt   # Agent persona, rules, and constraints
├── tools.py            # Tool implementations with mock data
├── agent.py            # Main agent with LangGraph StateGraph
└── test_api.py         # API connection verification
```

## File Responsibilities

### agent.py
- `AgentLogger` class - Logs agent thinking process
- `AgentState` TypedDict - State schema with message history
- `agent_node()` - LLM invocation with tool binding
- `logged_tool_node()` - Tool execution with timing
- StateGraph construction with conditional edges

### tools.py
- `FLIGHTS_DB` - Mock flight data (routes, prices, times)
- `HOTELS_DB` - Mock hotel data (names, prices, ratings)
- `@tool search_flights()` - Flight search by origin/destination
- `@tool search_hotels()` - Hotel search with price filter
- `@tool calculate_budget()` - Budget calculation from expense string

### system_prompt.txt
- `<persona>` - Agent personality (friendly Vietnamese travel buddy)
- `<rules>` - Behavior rules (language, tool calling logic)
- `<tools_instruction>` - Tool usage workflow
- `<response_format>` - Output structure for trip planning
- `<constraints>` - Guardrails (refuse non-travel requests)

## Data Flow
1. User input → agent_node (LLM decides tool calls)
2. Tool calls → logged_tool_node (execute tools)
3. Tool results → agent_node (LLM synthesizes response)
4. Final response → user