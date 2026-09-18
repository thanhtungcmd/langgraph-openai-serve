"""Expose the simple graph through the OpenAI-compatible LGOS API."""

import json

from fastapi import FastAPI
from starlette.middleware.base import RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from langgraph_openai_serve import GraphRegistry, LanggraphOpenaiServe

from external_tools import simple_external_tools_graph_config
from graph import simple_graph_config

app = FastAPI(title="Simple LangGraph API")


@app.middleware("http")
async def accept_chat_store(
    request: Request,
    call_next: RequestResponseEndpoint,
) -> Response:
    """Ignore OpenCode's optional Chat Completions storage preference.

    The sample pins LGOS 0.18.0, whose Chat request schema predates `store`
    and `prompt_cache_key`. This stateless sample has no response storage or
    prompt-cache namespace to configure.
    """
    if request.url.path == "/v1/chat/completions":
        try:
            payload = json.loads(await request.body())
        except json.JSONDecodeError:
            payload = None
        if isinstance(payload, dict):
            removed = False
            for field in ("store", "prompt_cache_key"):
                if field in payload:
                    payload.pop(field)
                    removed = True
            if removed:
                request._body = json.dumps(payload).encode()
    return await call_next(request)


graphs = GraphRegistry(
    registry={
        "simple-graph": simple_graph_config,
        "simple-graph-external-tools": simple_external_tools_graph_config,
    }
)

LanggraphOpenaiServe(app=app, graphs=graphs).bind_openai_api()
