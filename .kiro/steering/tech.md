# Tech Stack

## Core Technologies
- **Python 3.x** - Primary language
- **LangGraph** - Agent workflow orchestration with StateGraph
- **LangChain** - LLM integration framework
- **Google Gemini** - LLM (gemini-3.1-flash-lite-preview)
- **python-dotenv** - Environment variable management

## Key Libraries
- `langchain-google-genai` - Gemini integration
- `langchain-core` - Core LangChain components (tools, messages)
- `langgraph.prebuilt` - ToolNode, tools_condition

## Project Structure
```
lab4_agent/
├── .env              # GEMINI_API_KEY
├── system_prompt.txt # Agent persona and rules
├── tools.py          # Tool definitions (search_flights, search_hotels, calculate_budget)
├── agent.py          # LangGraph StateGraph implementation
└── test_api.py       # API connection test
```

## Commands
```bash
# Install dependencies
pip install langchain langchain-google-genai langgraph python-dotenv streamlit pytest

# Test API connection
python test_api.py

# Run agent (CLI mode)
python agent.py

# Run Streamlit web app
streamlit run app.py

# Run tests (disable asyncio plugin to avoid Windows blocking issue)
pytest test_agent.py -v -p no:asyncio
```

## Environment Variables
- `GEMINI_API_KEY` - Required for LLM calls

## Mock Data
- `FLIGHTS_DB` - Flight routes between Vietnamese cities
- `HOTELS_DB` - Hotels in Đà Nẵng, Phú Quốc, Hồ Chí Minh