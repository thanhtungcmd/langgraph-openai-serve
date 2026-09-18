"""A tool-enabled LangGraph model for OpenAI-compatible coding agents."""

import os
from typing import Annotated, Sequence

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import AIMessage, BaseMessage, SystemMessage
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph_openai_serve import (
    ClientFunctionTool,
    ClientToolChoice,
    GraphConfig,
    GraphRequest,
    NamedFunctionToolChoice,
)
from pydantic import BaseModel, Field


class ExternalToolsState(BaseModel):
    """Messages and client-owned tools for one coding-agent invocation."""

    messages: Annotated[Sequence[BaseMessage], add_messages]
    tools: tuple[ClientFunctionTool, ...] = Field(default_factory=tuple)
    tool_choice: ClientToolChoice | None = None


def request_to_input(
    request: GraphRequest,
    messages: list[BaseMessage],
) -> ExternalToolsState:
    """Preserve the whole tool conversation for a client-owned tool loop."""
    return ExternalToolsState(
        messages=messages,
        tools=request.tools,
        tool_choice=request.tool_choice,
    )


async def generate(state: ExternalToolsState) -> dict[str, list[AIMessage]]:
    """Ask Anthropic to choose tools while leaving execution to the client."""
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
    conversation = [
        SystemMessage(
            content=(
                "You are a coding assistant. Use the supplied tools when they are "
                "needed to inspect or change the user's workspace."
            )
        ),
        *state.messages,
    ]
    if state.tools:
        binding_options: dict[str, object] = {}
        if state.tool_choice is not None:
            binding_options["tool_choice"] = _anthropic_tool_choice(state.tool_choice)
        response = await model.bind_tools(
            [_anthropic_tool(tool) for tool in state.tools],
            **binding_options,
        ).ainvoke(conversation)
    else:
        response = await model.ainvoke(conversation)
    return {"messages": [response]}


def _anthropic_tool(tool: ClientFunctionTool) -> dict[str, object]:
    """Translate LGOS's protocol-neutral tool shape for ChatAnthropic."""
    definition: dict[str, object] = {"name": tool.name}
    if tool.description is not None:
        definition["description"] = tool.description
    if tool.parameters is not None:
        definition["input_schema"] = dict(tool.parameters)
    return definition


def _anthropic_tool_choice(tool_choice: ClientToolChoice) -> str | dict[str, str]:
    """Map OpenAI's client tool choice onto Anthropic's binding options."""
    if isinstance(tool_choice, NamedFunctionToolChoice):
        return {"type": "tool", "name": tool_choice.name}
    if tool_choice == "required":
        return "any"
    if tool_choice in {"auto", "none"}:
        return tool_choice
    msg = "This graph only supports client-owned function tools."
    raise ValueError(msg)


workflow = StateGraph(ExternalToolsState)
workflow.add_node("generate", generate)
workflow.add_edge("generate", END)
workflow.set_entry_point("generate")

simple_external_tools_graph_config = GraphConfig(
    graph=workflow.compile(),
    description="Streams a coding-agent response with client-owned function tools.",
    streamable_node_names=["generate"],
    request_to_input=request_to_input,
)
