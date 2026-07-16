"""
AI Orchestrator built with LangGraph.

Graph flow:

    START -> retrieve_memory -> retrieve_documents -> decide_tools -> build_context -> END

The graph's job is to assemble the final list of chat messages (system + tool
results + history + user turn) that gets handed to Ollama for the actual
(streamed) generation. Streaming itself happens in the chat endpoint using
OllamaClient.stream_chat, using the messages this graph produces — LangGraph
nodes here are non-streaming by design, since they represent discrete
retrieval/decision steps, not token generation.
"""

from typing import List, Optional, TypedDict

from langgraph.graph import END, START, StateGraph

from app.llm.ollama_client import get_ollama_client
from app.memory.memory_service import MemoryService
from app.prompts.system_prompts import build_system_prompt
from app.rag.ingestion_service import IngestionService
from app.tools.registry import get_tool_registry
from app.utils.logger import get_logger

logger = get_logger(__name__)

MAX_TOOL_ROUNDS = 3


class OrchestratorState(TypedDict, total=False):
    user_id: str
    model: str
    user_message: str
    history: List[dict]              # prior turns as {"role", "content"}
    use_memory: bool
    use_rag: bool
    document_ids: List[str]

    memory_snippets: List[str]
    document_snippets: List[str]
    tool_messages: List[dict]        # tool-role messages appended after tool execution
    final_messages: List[dict]       # the fully assembled message list ready for generation


async def _retrieve_memory(state: OrchestratorState) -> OrchestratorState:
    if not state.get("use_memory", True):
        state["memory_snippets"] = []
        return state

    memory_service = MemoryService()
    snippets = await memory_service.retrieve_relevant_memories(
        user_id=state["user_id"], query=state["user_message"], k=4
    )
    state["memory_snippets"] = snippets
    return state


async def _retrieve_documents(state: OrchestratorState) -> OrchestratorState:
    if not state.get("use_rag", True):
        state["document_snippets"] = []
        return state

    ingestion_service = IngestionService()
    snippets = await ingestion_service.retrieve_context(
        query=state["user_message"],
        user_id=state["user_id"],
        document_ids=state.get("document_ids", []),
        k=4,
    )
    state["document_snippets"] = snippets
    return state


async def _decide_and_run_tools(state: OrchestratorState) -> OrchestratorState:
    """Give the model a chance to call tools before generating the final answer.

    Uses a non-streaming decision call with function-calling. If the model
    requests a tool, we execute it and loop (bounded by MAX_TOOL_ROUNDS),
    feeding the tool result back in as a `tool` role message.
    """
    registry = get_tool_registry()
    ollama = get_ollama_client()

    working_messages = list(state.get("history", [])) + [
        {"role": "user", "content": state["user_message"]}
    ]
    tool_messages: List[dict] = []

    for _ in range(MAX_TOOL_ROUNDS):
        response = await ollama.chat(
            model=state["model"],
            messages=working_messages + tool_messages,
            tools=registry.function_definitions(),
        )

        tool_calls = response.get("tool_calls") or []
        if not tool_calls:
            break

        for call in tool_calls:
            function = call.get("function", {})
            name = function.get("name")
            arguments = function.get("arguments", {}) or {}
            logger.info("orchestrator.tool_call", tool=name, arguments=arguments)
            result = await registry.invoke(name, arguments)
            tool_messages.append(
                {"role": "tool", "content": result, "name": name}
            )

    state["tool_messages"] = tool_messages
    return state


def _build_context(state: OrchestratorState) -> OrchestratorState:
    system_prompt = build_system_prompt(
        memory_snippets=state.get("memory_snippets"),
        document_snippets=state.get("document_snippets"),
    )

    messages: List[dict] = [{"role": "system", "content": system_prompt}]
    messages.extend(state.get("history", []))
    messages.extend(state.get("tool_messages", []))
    messages.append({"role": "user", "content": state["user_message"]})

    state["final_messages"] = messages
    return state


def _build_graph():
    graph = StateGraph(OrchestratorState)

    graph.add_node("retrieve_memory", _retrieve_memory)
    graph.add_node("retrieve_documents", _retrieve_documents)
    graph.add_node("decide_and_run_tools", _decide_and_run_tools)
    graph.add_node("build_context", _build_context)

    graph.add_edge(START, "retrieve_memory")
    graph.add_edge("retrieve_memory", "retrieve_documents")
    graph.add_edge("retrieve_documents", "decide_and_run_tools")
    graph.add_edge("decide_and_run_tools", "build_context")
    graph.add_edge("build_context", END)

    return graph.compile()


_compiled_graph = None


def get_orchestrator_graph():
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = _build_graph()
    return _compiled_graph


async def build_generation_messages(
    user_id: str,
    model: str,
    user_message: str,
    history: List[dict],
    use_memory: bool = True,
    use_rag: bool = True,
    document_ids: Optional[List[str]] = None,
) -> List[dict]:
    """Run the orchestrator graph and return the message list ready for streaming generation."""
    graph = get_orchestrator_graph()

    initial_state: OrchestratorState = {
        "user_id": user_id,
        "model": model,
        "user_message": user_message,
        "history": history,
        "use_memory": use_memory,
        "use_rag": use_rag,
        "document_ids": document_ids or [],
    }

    final_state = await graph.ainvoke(initial_state)
    return final_state["final_messages"]
