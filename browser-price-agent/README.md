# Browser Price Agent

A browser agent that opens real product pages (no retailer API required), reads the live product name and price via Playwright tools, and returns a clean markdown table. It uses a Haystack Agent with an Ollama LLM (local or remote) and the Playwright MCP server for navigation and accessibility snapshots.

---

## Tech Stack

| Tool                                                       | Purpose                                                                   |
| ---------------------------------------------------------- | ------------------------------------------------------------------------- |
| [Haystack](https://haystack.deepset.ai/)                      | Agent orchestration (tool loop + exit conditions)                         |
| [ollama-haystack](https://pypi.org/project/ollama-haystack/)  | Ollama chat generator for Haystack                                        |
| [mcp-haystack](https://pypi.org/project/mcp-haystack/)        | Connect Haystack tools to an MCP server                                   |
| [Ollama](https://ollama.com/)                                 | Local/remote LLM inference                                                |
| [Playwright MCP](https://github.com/microsoft/playwright-mcp) | Browser automation tools (`browser_navigate`, `browser_snapshot`, …) |
| [Node.js](https://nodejs.org/) + npx                          | Runs the Playwright MCP server                                            |
| Bash scripts                                               | Start MCP and run smoke / price-check flows (WSL/Linux)                   |

---

## Project Structure

```
browser-price-agent/
├── requirements.txt           # Python dependencies
├── start_playwright_mcp.sh    # Start Playwright MCP (headless Chrome-for-testing)
├── run_price_check.sh         # Run price check with the project venv
├── price_check/
│   └── check_price.py         # Real PDP price extraction agent
└── README.md
```

---

## Installation

1. Clone or open this project, then create/activate a virtual environment (example path used in WSL):

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
2. Install Python dependencies:

   ```bash
   cd browser-price-agent
   pip install -r requirements.txt
   ```
3. Install Node 18+ (nvm recommended on WSL — system Node 12 is too old for Playwright MCP):

   ```bash
   # if using nvm
   export NVM_DIR="$HOME/.nvm"
   source "$NVM_DIR/nvm.sh"
   nvm use 20
   ```
4. Install the Playwright MCP browser (chrome-for-testing):

   ```bash
   npx --yes @playwright/mcp@latest install-browser chrome-for-testing
   ```

   If OS libraries are missing, also run (will prompt for sudo):

   ```bash
   npx playwright install --with-deps chromium
   ```

---

## Configuration

This project needs:

1. **Ollama** (local or remote) with a tool-capable model
2. **Playwright MCP** listening on `http://localhost:8931`

Edit the top of `price_check/check_price.py` (and `testing/smoke_test.py` for the smoke test):

| Variable         | Default                       | Notes                                                            |
| ---------------- | ----------------------------- | ---------------------------------------------------------------- |
| `OLLAMA_URL`   | `http://localhost:11434`    | Change to a remote Ollama base URL when needed                   |
| `OLLAMA_MODEL` | `qwen2.5:7b`                | Prefer tool-capable models; small Qwen 3.5 4B can break tool XML |
| `MCP_URL`      | `http://localhost:8931/mcp` | Must match the MCP start script port                             |
| `PRODUCT_URL`  | Logitech MX Master 3S page    | Swap for any public product page                                 |

Pull a model on the Ollama host if needed:

```bash
ollama pull qwen2.5:7b
```

No `.env` or cloud API keys are required for the Ollama path.

---

## Usage

Use **two terminals** (WSL/Linux).

### 1) Start Playwright MCP

```bash
bash price_agent/start_playwright_mcp.sh
```

Keep this terminal open. You should see `Listening on http://localhost:8931`.

If the port is busy:

```bash
pkill -f 'playwright-mcp' || true
bash price_agent/start_playwright_mcp.sh
```

### 2) Price check

```bash
bash price_agent/run_price_check.sh
```

Expected final answer shape:

```markdown
| Name | Price | URL |
|------|-------|-----|
| MX Master 3s Wireless Mouse - 8K Optical Sensor | $89.99 | https://... |
```

Override the venv path if needed:

```bash
VENV=/path/to/venv bash browser-price-agent/run_price_check.sh
```

---

## Contributing

Contributions to this project are welcome! If you have ideas for improvements, bug fixes, or new features, feel free to open an issue or submit a pull request.

---

## License

This project is licensed under the MIT License - see the [MIT License](https://opensource.org/licenses/MIT) file for details.
