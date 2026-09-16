# LangGraph + Open WebUI with Docker Compose

This sample runs a small LangGraph application behind LGOS's OpenAI-compatible
`/v1` API and connects Open WebUI to it. The graph is based on
`demo/api/src/lgos_demo_api/graphs/simple.py`: it sends the latest user message
to an OpenAI-compatible model provider and streams the answer back.

## Run it

1. Create the local configuration and supply a real model-provider API key:

   ```bash
   cd sample
   cp .env.example .env
   ```

   Edit `.env` and set `OPENAI_API_KEY`. Change `OPENAI_BASE_URL` and
   `OPENAI_MODEL` when using another OpenAI-compatible provider.

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

## Architecture

```mermaid
flowchart LR
    browser[Browser] --> ui[Open WebUI :3000]
    ui -->|OpenAI-compatible /v1| graph[LGOS + simple-graph :8000]
    graph --> provider[LLM provider]
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
