# Rose

## Ticket Manager (Kanban)

The Kanban ticketing app lives in `ticketmanager/`. Run it from the **repository root** (this directory) so that the `ticketmanager` package is on the path.

### Setup

From the repo root:

```bash
uv pip install -e ticketmanager
# or: pip install -e ticketmanager
```

### Run

From the repo root (with this directory on `PYTHONPATH`):

```bash
uvicorn ticketmanager.app.main:app --reload
```

Or from `ticketmanager/`:

```bash
cd ticketmanager
set PYTHONPATH=..
uv run uvicorn ticketmanager.app.main:app --reload
```

Then open http://127.0.0.1:8000 for the Kanban UI. The REST API is under http://127.0.0.1:8000/api/tickets.

---

## Agentmanager

The Agentmanager service lets you create and manage LLM agents (Ollama or OpenAI) with optional MCP tools and per-agent AGENT.md instructions. Config is stored in SQLite. The service does **not** manage conversation state; callers send full chat history plus the current user message and receive only the next assistant message.

### Setup

From the repo root:

```bash
uv pip install -e agentmanager
# or: pip install -e agentmanager
```

### Run

From the repo root (with this directory on `PYTHONPATH`):

```bash
uvicorn agentmanager.app.main:app --reload --port 8001
```

Or from `agentmanager/`:

```bash
cd agentmanager
set PYTHONPATH=..
uv run uvicorn agentmanager.app.main:app --reload --port 8001
```

Then open http://127.0.0.1:8001 for the agent management UI. The REST API is under http://127.0.0.1:8001/api/agents and http://127.0.0.1:8001/api/chat.

**Environment (optional):**

- `OPENAI_API_KEY` – required when using OpenAI as a provider for an agent.
- `OLLAMA_BASE_URL` – default base URL for Ollama when an agent does not set one. You can also set **per-agent** Ollama base URL when creating or editing an agent (API field `ollama_base_url`, or the "Ollama base URL" field in the UI). Per-agent URL overrides the env default.

### Chat API

- **POST /api/chat** – body: `{"agent_id": "<uuid>", "messages": [{"role": "user"|"assistant"|"system", "content": "..."}]}`. The last message is the current user message. Response: `{"content": "<assistant reply>"}`. The service does not store conversations; the caller provides full history each time.

---

## Message Queue

The Message Queue service stores per-session conversation history and exposes send, poll, and history endpoints. A session is a conversation between two participants (people or agents). When a message is sent, the session’s “unseen” flag is set; clients poll to see if there is a new message, then fetch history (which clears the unseen flag).

### Setup

From the repo root:

```bash
uv pip install -e messagequeue
# or: pip install -e messagequeue
```

### Run

From the repo root (with this directory on `PYTHONPATH`):

```bash
uvicorn messagequeue.app.main:app --reload --port 8002
```

Or from `messagequeue/`:

```bash
cd messagequeue
set PYTHONPATH=..
uv run uvicorn messagequeue.app.main:app --reload --port 8002
```

Then the REST API is under http://127.0.0.1:8002/api/messages, http://127.0.0.1:8002/api/poll, and http://127.0.0.1:8002/api/sessions/{session_id}/history.

### API

- **POST /api/sessions** – body: `{"participants": [{"name": "<string>", "isAgent": true|false}, {"name": "<string>", "isAgent": true|false}], "sessionId": "<optional>"}`. Exactly two participants. Returns `{"sessionId": "<uuid or provided id>"}`. If `sessionId` is provided and that session exists, returns it (idempotent). Otherwise creates a new session.
- **POST /api/sessions/find** – body: same as create (two participants). Returns `{"sessionId": "<uuid>"}` for the session between those two participants (order-independent). 404 if no such session exists.
- **POST /api/messages** – body: `{"sessionId": "<string>", "user": "<string>", "message": "<string>"}`. Appends the message to the session and sets the unseen flag. Returns 404 if the session does not exist.
- **GET /api/poll?sessionId=<id>** – returns `{"has_unseen": true|false}`. No side effects.
- **GET /api/sessions/updated** – returns `{"session_ids": ["<id>", ...]}`: all session ids that have an unseen update.
- **GET /api/sessions/{session_id}/history** – returns `{"participants": [{"name": "...", "isAgent": true|false}, ...], "messages": [{"user": "...", "message": "..."}, ...]}` in order. Participants are the two users defined at session creation. Clears the unseen flag for that session so the next poll returns `false`. Optional query param `clear_unseen` (default `true`) – set to `false` to read history without clearing (e.g. for DiscordGateway). Returns 404 if the session does not exist.

---

## DiscordGateway

The DiscordGateway service runs a Discord bot that relays channel messages to the message queue and sends agent replies back to Discord. It does **not** use the message queue’s poll/updated mechanism (reserved for the heartbeat); instead it checks session history directly until the agent reply appears. The UI lets you set a Discord bot token and assign agents (from Agentmanager) to specific Discord channels. An API endpoint allows sending a message to a channel from the bot (e.g. when a task is done later and the user is not in an active conversation).

### Setup

From the repo root:

```bash
uv pip install -e discordgateway
# or: pip install -e discordgateway
```

### Run

From the repo root (with this directory on `PYTHONPATH`):

```bash
uvicorn discordgateway.app.main:app --reload --port 8003
```

Or from `discordgateway/`:

```bash
cd discordgateway
set PYTHONPATH=..
uv run uvicorn discordgateway.app.main:app --reload --port 8003
```

Then open http://127.0.0.1:8003 for the config UI. Set a Discord bot token (from the Discord Developer Portal), invite the bot to your server, and assign an agent to each channel where the bot should respond. Messages in those channels are relayed to the message queue; the Heartbeat service drives the agent reply, and the reply is sent back to the channel.

### Environment

- `AGENTMANAGER_URL` – base URL for agentmanager (default: `http://agentmanager:8000` in Docker).
- `MESSAGEQUEUE_URL` – base URL for message queue (default: `http://messagequeue:8000` in Docker).

### API

- **GET /api/config** – returns `{"token_set": true|false, "token_preview": "…"}` (last 4 chars of token if set).
- **POST /api/config** – body: `{"token": "<string>|null"}`. Set or clear the Discord bot token. Restart the service for the bot to connect with a new token.
- **GET /api/channel-assignments** – list of `{"guild_id", "channel_id", "agent_id"}`.
- **POST /api/channel-assignments** – body: `{"guild_id", "channel_id", "agent_id"}`. Create or update an assignment.
- **DELETE /api/channel-assignments/{guild_id}/{channel_id}** – remove an assignment.
- **GET /api/guilds** – list of guilds and text channels from the bot’s cache (for UI dropdowns). Empty if bot is not connected.
- **POST /api/send-to-channel** – body: `{"channel_id": "<snowflake>", "message": "<text>"}`. Send a message to that Discord channel from the bot. Use for out-of-band notifications (e.g. task completed later). Returns 404 if the bot is not connected or the channel is not found.

---

## Heartbeat

The Heartbeat service runs 24/7 in a loop. It connects to agentmanager (to invoke agents), messagequeue (to send and poll messages), and ticketmanager (to find tickets that need work). It acts as user **RoseHeartBeat** with `isAgent=false` so it does not trigger agent self-replies.

Each iteration:

1. **Chat updates:** Poll the message queue for sessions with unseen updates. For each such session, determine which agent should respond (if two agents, the one that did not send the last message; if one agent, that agent). Invoke the agent via agentmanager and post the reply to the session.
2. **Ticket dispatch:** Fetch tickets in `todo` or `review` status. For each ticket, get-or-create a dedicated session `RoseHeartbeat-task-{ticket_id}` with participants RoseHeartBeat and the ticket’s assignee. If the session has no messages yet, send a single task message (title + instructions) as RoseHeartBeat so the agent receives the work in a clean context window.

### Setup

From the repo root:

```bash
uv pip install -e heartbeat
# or: pip install -e heartbeat
```

### Run

From the repo root (with this directory on `PYTHONPATH`):

```bash
python -m heartbeat.app.main
```

Or from `heartbeat/`:

```bash
cd heartbeat
set PYTHONPATH=..
uv run python -m heartbeat.app.main
```

### Environment

- `AGENTMANAGER_URL` – base URL for agentmanager (default: `http://agentmanager:8000` in Docker).
- `MESSAGEQUEUE_URL` – base URL for message queue (default: `http://messagequeue:8000`).
- `TICKETMANAGER_URL` – base URL for ticketmanager API (default: `http://web:8000` in Docker).
- `HEARTBEAT_SLEEP_SECONDS` – seconds to sleep between loop iterations (default: `10`).

---

## Control Panel

The Control Panel is a single navigation page that embeds all other service UIs in an iframe. Use it to manage the platform from one tab instead of opening Ticket Manager, Agentmanager, Message Queue, and Discord Gateway separately.

### Setup

From the repo root:

```bash
uv pip install -e controlpanel
```

### Run

From the repo root:

```bash
uvicorn controlpanel.app.main:app --reload --port 8010
```

Or from `controlpanel/`:

```bash
cd controlpanel
set PYTHONPATH=..
uv run uvicorn controlpanel.app.main:app --reload --port 8010
```

Then open http://127.0.0.1:8010. Use the nav links to switch between Ticket Manager, Agentmanager, Message Queue (API docs), Discord Gateway, and Events in the frame.

### Events

The Control Panel has an **Events** page: a vertical list of events and the time they happened. Other services can report events so they appear there.

- **POST /api/events** – body: `{"source": "<service name>", "event": "<event type>", "message": "<optional detail>"}`. Example: `{"source": "ticketmanager", "event": "ticket.created", "message": "Ticket 'Fix bug' created"}`. Returns `201` with `{"id": "<uuid>"}`.
- **GET /api/events** – query: `limit` (default 100). Returns `{"events": [...]}` newest first; each event has `id`, `timestamp`, `source`, `event`, `message`.

Events are stored in memory (last 500). Set `CONTROL_PANEL_URL` (e.g. `http://localhost:8010` when running locally, or `http://controlpanel:8010` from another container) so services can report. The following events are reported automatically when the URL is set:

| Service        | Event                  | When |
|----------------|------------------------|------|
| discordgateway | `discord.user_message` | User sends a message in Discord |
| discordgateway | `discord.agent_reply`  | AI responds in Discord |
| agentmanager   | `agent.created`        | An agent is created (API or UI) |
| agentmanager   | `agent.requested`      | A chat request is made (POST /api/chat) |
| heartbeat      | `heartbeat.found_message` | Heartbeat finds a session with new messages |
| heartbeat      | `heartbeat.found_task` | Heartbeat dispatches a task to an agent (todo/review ticket) |

### Environment

- `TICKETMANAGER_URL` – base URL for Ticket Manager (default: `http://localhost:8000`).
- `AGENTMANAGER_URL` – base URL for Agentmanager (default: `http://localhost:8001`).
- `MESSAGEQUEUE_URL` – base URL for Message Queue (default: `http://localhost:8002`).
- `DISCORDGATEWAY_URL` – base URL for Discord Gateway (default: `http://localhost:8003`).

These URLs are used for iframe `src` and must be reachable from the browser (e.g. `localhost` with published ports when using Docker).

---

## Docker

From the repo root:

```bash
docker compose up --build
```

- **Control Panel:** http://127.0.0.1:8010 – single page with nav; opens all other services in an iframe.
- **Ticket Manager:** http://127.0.0.1:8000 (Kanban UI and `/api/tickets`).
- **Agentmanager:** http://127.0.0.1:8001 (agent UI and `/api/agents`, `/api/chat`).
- **Message Queue:** http://127.0.0.1:8002 (`/api/messages`, `/api/poll`, `/api/sessions/{id}/history`).
- **DiscordGateway:** http://127.0.0.1:8003 (config UI and `/api/config`, `/api/channel-assignments`, `/api/send-to-channel`).
- **Heartbeat:** runs in the background; no HTTP port. Uses `RoseHeartBeat` (isAgent=false) and task sessions `RoseHeartbeat-task-{ticket_id}`.

SQLite data for each service is stored in named volumes and persists between runs. For Agentmanager with OpenAI agents, set `OPENAI_API_KEY` in the environment or in a `.env` file when using Docker Compose.

All service UIs (Control Panel, Ticket Manager, Agentmanager, Discord Gateway) share the same design tokens and base styles from `platform_theme/theme.css`; each service adds only its own component CSS for a consistent look across the platform.
