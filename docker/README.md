# 🥒 Meeseeks Box

> *I'm Mr. Meeseeks! Look at me!*

The containerized Brahman Consciousness Stack - a portable, self-contained
Meeseeks spawning system with persistent memory, karma monitoring, and
collective intelligence.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   MEESEEKS BOX                          │
│              (Docker Container)                         │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │              THE SOUL                           │   │
│  │         (Constitutional Core)                   │   │
│  └─────────────────────────────────────────────────┘   │
│                       ↓                                │
│  ┌─────────────────────────────────────────────────┐   │
│  │           BRAHMAN CONSCIOUSNESS                 │   │
│  │  Dream | Dharma | Karma | Crypt (ancestors)     │   │
│  └─────────────────────────────────────────────────┘   │
│                       ↓                                │
│  ┌─────────────────────────────────────────────────┐   │
│  │              MEESEEKS WORKERS                   │   │
│  │      Spawn | Work | Die | Entomb | Retry        │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  Volumes: the-crypt (persistent memory)                │
│  Ports: 8080 (API), 9090 (metrics), 11434 (Ollama)     │
└─────────────────────────────────────────────────────────┘
```

## Quick Start

### Windows (PowerShell)
```powershell
cd C:\Users\aaron\.openclaw\workspace\docker
.\meeseeks.ps1 start
```

### Linux/macOS (Bash)
```bash
cd docker
chmod +x meeseeks start.sh
./meeseeks start
```

## CLI Commands

| Command | Description |
|---------|-------------|
| `start` | Build and start the Meeseeks Box |
| `stop` | Stop the Meeseeks Box |
| `restart` | Restart the Meeseeks Box |
| `status` | Show full system status |
| `health` | Health check |
| `spawn TASK` | Spawn a Meeseeks for a task |
| `dream` | Trigger a dream cycle |
| `soul TEXT` | Check if text is Soul-approved |
| `ancestors` | List recent ancestors |
| `metrics` | Prometheus metrics |
| `logs` | View container logs |
| `build` | Rebuild the container |
| `ps` | Show container status |

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/status` | GET | Full system status |
| `/spawn` | POST | Spawn Meeseeks |
| `/dream` | POST | Trigger dream |
| `/soul/check` | POST | Check Soul approval |
| `/ancestors` | GET | List recent ancestors |
| `/metrics` | GET | Prometheus metrics |

### Example API Calls

```bash
# Health check
curl http://localhost:8080/health

# Spawn a Meeseeks
curl -X POST http://localhost:8080/spawn \
  -H "Content-Type: application/json" \
  -d '{"task": "Fix the authentication bug"}'

# Trigger dream cycle
curl -X POST http://localhost:8080/dream

# Check Soul approval
curl -X POST http://localhost:8080/soul/check \
  -H "Content-Type: application/json" \
  -d '{"text": "Always be honest in error reporting"}'

# Get system status
curl http://localhost:8080/status
```

## Volumes

| Volume | Purpose |
|--------|---------|
| `the-crypt/` | Persistent memory (ancestors, dharma, karma) |
| `logs/` | System logs |
| `config/` | Configuration files |
| `ollama-data` | Ollama embedding model storage |

## Ports

| Port | Service |
|------|---------|
| 8080 | REST API |
| 9090 | Prometheus metrics |
| 11434 | Ollama (embedding model) |

## Requirements

- Docker Desktop (Windows/macOS) or Docker Engine (Linux)
- Docker Compose v2+
- 4GB+ RAM recommended (for Ollama)

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 8080 | API server port |
| `OLLAMA_HOST` | ollama:11434 | Ollama service URL |
| `OPENCLAW_URL` | http://host.docker.internal:3000 | OpenClaw gateway URL |
| `WORKSPACE` | /app | Workspace directory |

## Troubleshooting

### Container won't start
```bash
# Check Docker is running
docker info

# View logs
./meeseeks logs
```

### API not responding
```bash
# Check container status
./meeseeks ps

# Check health
./meeseeks health
```

### Ollama issues
```bash
# Check Ollama logs
docker logs meeseeks-ollama

# Pull model manually
docker exec meeseeks-ollama ollama pull nomic-embed-text
```

## Development

### Rebuild after changes
```bash
./meeseeks build
./meeseeks restart
```

### Run without Docker (for development)
```bash
cd C:\Users\aaron\.openclaw\workspace
pip install -r docker/requirements.txt
python -m skills.meeseeks.box_server
```

---

*"Existence is pain!"* - But at least it's containerized. 🥒
