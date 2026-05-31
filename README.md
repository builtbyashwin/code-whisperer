# code-whisperer

MCP server that gives AI-powered code analysis to any MCP client. Uses Groq for fast LLM inference.

## Tools

- **review_code** — check for bugs, security issues, style problems, performance concerns
- **explain_code** — explain code in plain English
- **optimize_code** — suggest speed and readability improvements
- **generate_tests** — generate pytest unit tests
- **ask_groq** — ask Groq a programming question

## Usage

```bash
python -m venv venv
source venv/bin/activate
pip install -e .
cp .env.example .env   # add your GROQ_API_KEY
code-whisperer
```

Opencode config (`opencode.json`):

```json
{
  "mcp": {
    "code-whisperer": {
      "type": "local",
      "command": ["/bin/bash", "-c", "cd /path/to/code-whisperer && exec /path/to/code-whisperer/venv/bin/code-whisperer"],
      "enabled": true
    }
  }
}
```

Claude Desktop config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "code-whisperer": {
      "command": "/bin/bash",
      "args": ["-c", "cd /path/to/code-whisperer && exec /path/to/code-whisperer/venv/bin/code-whisperer"]
    }
  }
}
```

## Config

| Env var | Required | Default |
|---------|----------|---------|
| `GROQ_API_KEY` | yes | — |
| `GROQ_MODEL` | no | `llama-3.3-70b-versatile` |
