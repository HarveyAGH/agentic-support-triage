# Dockerfile — put this in the root of your triage project
FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install uv && uv pip install --system -r pyproject.toml 2>/dev/null || pip install langchain langchain-aws langchain-community langgraph pydantic python-dotenv ddgs

COPY . .

CMD ["python", "agent/agent.py"]