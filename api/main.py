from fastapi import FastAPI
from langchain_core.messages import HumanMessage
from pydantic import BaseModel
from agent.agent import graph_app

app = FastAPI(title="Agentic Support Triage API")
    
@app.get("/health")
def health():
    return{
        "status": "ok"
    }
    
class AIRequest(BaseModel):
    message: str
    thread_id: str = "api-demo"
    
    
class AIResponse(BaseModel):
    answer: str
    routes_called : list[str]
    shall_be_escalated: bool
    
    

def _called_routes(result: dict) -> list[str]:
    routes = []
    for message in result["messages"]:
        for tool_call in getattr(message, "tool_calls", []) or []:
            name = tool_call.get("name")
            if name and name.startswith("route_to_"):
                routes.append(name)
    return list(dict.fromkeys(routes))
 



def _needs_escalation(result: dict, routes_called: list[str]) -> bool:
    if "route_to_escalation" in routes_called:
        return True

    all_text = "\n".join(str(getattr(message, "content", "")) for message in result["messages"])
    return "needs_escalation=True" in all_text


@app.post("/triage", response_model=AIResponse)
async def triage(request: AIRequest):
    results = await graph_app.ainvoke(
        {"messages": [HumanMessage(content=request.message)]},
        config={
            "configurable": {"thread_id": request.thread_id},
            "tags": ["api", "customer-support-triage"],
            "metadata": {
                "entrypoint": "fastapi",
                "thread_id": request.thread_id,
            },
        },
    )
    last_message = results["messages"][-1].content
    routes_called = _called_routes(results)

    return AIResponse(
        answer=last_message,
        routes_called=routes_called,
        shall_be_escalated=_needs_escalation(results, routes_called),
    )
