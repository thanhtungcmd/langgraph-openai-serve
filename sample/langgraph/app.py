"""Expose the simple graph through the OpenAI-compatible LGOS API."""

from fastapi import FastAPI
from langgraph_openai_serve import GraphRegistry, LanggraphOpenaiServe

from graph import simple_graph_config

app = FastAPI(title="Simple LangGraph API")
graphs = GraphRegistry(
    registry={
        "simple-graph": simple_graph_config,
    }
)

LanggraphOpenaiServe(app=app, graphs=graphs).bind_openai_api()
