# Teaching Resources

Use these as primary sources when teaching or reviewing concepts.

## Agent Orchestration

- [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview)
  - Use for: StateGraph, durable execution, streaming, persistence, human-in-the-loop, LangSmith integration.
  - Trust level: official documentation.

## Evaluation

- [LangSmith LLM-as-a-judge evaluator](https://docs.langchain.com/langsmith/llm-as-judge)
  - Use for: judge rubrics, evaluation workflows, scoring subjective output quality.
  - Trust level: official documentation.

## MCP

- [FastMCP tools documentation](https://gofastmcp.com/servers/tools)
  - Use for: exposing Python functions as MCP tools with typed inputs and tool metadata.
  - Trust level: official FastMCP documentation.

## API And Deployment

- [FastAPI in Containers - Docker](https://fastapi.tiangolo.com/deployment/docker/)
  - Use for: containerizing FastAPI services and deployment structure.
  - Trust level: official FastAPI documentation.

- [FastAPI First Steps](https://fastapi.tiangolo.com/tutorial/first-steps/)
  - Use for: app creation, path operation decorators, and running the development server.
  - Trust level: official FastAPI documentation.

- [FastAPI Request Body](https://fastapi.tiangolo.com/tutorial/body/)
  - Use for: request JSON validation with Pydantic models.
  - Trust level: official FastAPI documentation.

- [FastAPI async/await](https://fastapi.tiangolo.com/async/)
  - Use for: deciding when endpoint functions should be async.
  - Trust level: official FastAPI documentation.

- [FastAPI manual server docs](https://fastapi.tiangolo.com/deployment/manually/)
  - Use for: understanding ASGI servers such as Uvicorn.
  - Trust level: official FastAPI documentation.

## Local Project References

- `/home/snowaflic/Multi_agent_job_description_assistant`
  - Use for: supervisor-as-tools agent, evals, LangSmith tracing, resume project.

- `/home/snowaflic/rags`
  - Use for: PDF loading, chunking, embeddings, ChromaDB vector storage, semantic retrieval.

## Retrieval

- [LangChain BM25Retriever API reference](https://reference.langchain.com/python/langchain_community/retrievers/bm25/)
  - Use for: lexical retrieval over text chunks without embeddings.
  - Trust level: official LangChain API reference.

- [Chroma query guide](https://docs.trychroma.com/docs/querying-collections/query-and-get)
  - Use for: vector-store querying, top-k retrieval, and metadata retrieval.
  - Trust level: official Chroma documentation.

- [Elastic full-text search guide](https://www.elastic.co/docs/solutions/search/full-text)
  - Use for: production full-text search concepts and exact lexical retrieval.
  - Trust level: official Elastic documentation.

- [Redis full-text search for RAG](https://redis.io/blog/full-text-search-for-rag-the-precision-layer/)
  - Use for: why lexical retrieval is useful as the precision layer in RAG.
  - Trust level: official Redis engineering blog.
