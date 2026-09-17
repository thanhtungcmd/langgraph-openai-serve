"""A minimal LLM-backed graph adapted from the demo simple graph."""

import os
from typing import Annotated, Literal, Sequence

from langchain_core.messages import AIMessage, BaseMessage, SystemMessage
from langchain_anthropic import ChatAnthropic
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.runtime import Runtime
from langgraph_openai_serve import ClientSettings, GraphConfig
from pydantic import BaseModel, Field

DEFAULT_SYSTEM_PROMPT = (
    "You are a helpful assistant called LangGraph OpenAI Serve. "
    "Chat with the user with a friendly tone."
)


class AgentState(BaseModel):
    """State passed through the message graph."""

    messages: Annotated[Sequence[BaseMessage], add_messages]


class SimpleContext(ClientSettings):
    """Runtime settings that OpenAI-compatible clients may configure."""

    use_history: bool = Field(
        default=False,
        title="Use conversation history",
        description="Include prior user and assistant messages in each generation.",
    )
    audience: Literal["general", "beginner", "expert"] = Field(
        default="general",
        title="Audience",
        description="Adapt terminology and assumed knowledge to the selected audience.",
    )


async def generate(
    state: AgentState,
    runtime: Runtime[SimpleContext],
) -> dict[str, list[AIMessage]]:
    """Generate a response from Claude through the Anthropic API."""
    model = ChatAnthropic(
        model=os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5"),
        api_key=os.environ["ANTHROPIC_API_KEY"],
        base_url=os.getenv("ANTHROPIC_BASE_URL"),
        default_headers={
            "anthropic-workspace-id": os.environ["ANTHROPIC_WORKSPACE_ID"],
        },
        max_tokens=1024,
        temperature=0.7,
    )
    context = runtime.context or SimpleContext()
    messages = state.messages if context.use_history else state.messages[-1:]
    response = await model.ainvoke(
        [
            SystemMessage(
                content=(
                    f"{DEFAULT_SYSTEM_PROMPT} "
                    f"Adapt explanations for {context.audience} readers."
                )
            ),
            *messages,
        ]
    )
    return {"messages": [response]}


workflow = StateGraph(AgentState, context_schema=SimpleContext)
workflow.add_node("generate", generate)
workflow.add_edge("generate", END)
workflow.set_entry_point("generate")

simple_graph = workflow.compile()
simple_graph_config = GraphConfig(
    graph=simple_graph,
    description="Streams model output with configurable history and audience settings.",
    streamable_node_names=["generate"],
    client_settings=SimpleContext,
)
