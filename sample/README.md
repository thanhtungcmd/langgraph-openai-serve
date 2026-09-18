# LangGraph + Open WebUI with Docker Compose

This sample runs a small LangGraph application behind LGOS's OpenAI-compatible
`/v1` API and connects Open WebUI and an optional OpenCode coding agent to it. The graph is based on
`demo/api/src/lgos_demo_api/graphs/simple.py`: it sends the latest user message
to Claude Haiku 4.5 through the Anthropic API and streams the answer back.

The sample pins its LGOS dependency because graph streaming configuration is a
package API and must remain compatible with the graph source in this directory.

## Run it

1. Create the local configuration and supply Anthropic API credentials:

   ```bash
   cd sample
   cp .env.example .env
   ```

   Edit `.env` and set `ANTHROPIC_API_KEY` and `ANTHROPIC_WORKSPACE_ID`.
   `ANTHROPIC_BASE_URL` defaults to `https://api.anthropic.com`; change it only
   when using an Anthropic-compatible proxy. The default model is
   `claude-haiku-4-5`; change `ANTHROPIC_MODEL` to select another model
   available to your Anthropic workspace.

2. Start the services:

   ```bash
   docker compose up --build
   ```

3. Open [http://localhost:3000](http://localhost:3000), select
   `simple-graph`, and start a chat. Authentication is disabled for this local
   sample.

The LangGraph API is available at `http://localhost:8000/v1`. For diagnostics:

```bash
curl http://localhost:8000/v1/models
```

Stop the stack with `docker compose down`. Add `--volumes` to also remove Open
WebUI's locally stored accounts and conversations.

## Run OpenCode

The optional OpenCode profile uses the `simple-graph-external-tools` model. Its
tool loop stays in OpenCode: it reads and changes the repository mounted at
`/workspace`, while LangGraph selects function calls through the standard
OpenAI Chat Completions API.

Start the LangGraph service, then run the interactive agent:

```bash
docker compose up --build -d langgraph
docker compose run --rm opencode
```

OpenCode is configured to use `lgos/simple-graph-external-tools`. The default
mount is the repository parent of `sample/`; any agent-approved file changes
therefore affect your working copy. Set `OPENCODE_IMAGE` to use another pinned
OpenCode image version.

## Architecture

```mermaid
flowchart LR
    browser[Browser] --> ui[Open WebUI :3000]
    ui -->|OpenAI-compatible /v1| graph[LGOS + simple-graph :8000]
    agent[OpenCode] -->|OpenAI-compatible /v1| tools[LGOS + simple-graph-external-tools :8000]
    graph --> provider[LLM provider]
    tools --> provider
```

Open WebUI uses the Docker service name `langgraph`, not `localhost`, to reach
the API. Its connection settings are deliberately non-persistent so changes in
`docker-compose.yml` apply on the next start.

!!! warning

    Anyone who can reach port 3000 can use this Open WebUI instance. Do not
    expose it to an untrusted network. Open WebUI can only disable authentication
    for a fresh installation; if a prior sample volume contains users, remove it
    before restarting with `docker compose down --volumes`. This deletes the
    sample's chats and accounts.
