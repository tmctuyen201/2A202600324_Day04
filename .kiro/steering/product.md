# TravelBuddy AI Agent

A Vietnamese travel assistant built with LangGraph and Google Gemini. The agent helps users search for flights, find hotels, and calculate travel budgets through natural conversation.

## Key Features
- Flight search between Vietnamese cities (Hà Nội, Đà Nẵng, Phú Quốc, Hồ Chí Minh)
- Hotel search with budget filtering
- Budget calculation and expense tracking
- Multi-step tool chaining for complete trip planning

## Agent Behavior
- Responds in Vietnamese
- Automatically calls tools when required parameters are provided
- Only asks for missing information when planning complete packages
- Refuses non-travel related requests (guardrail)