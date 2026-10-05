# LocalMCP Starter

> A beginner-friendly, local MCP server you can run on your own machine in minutes.

If you are just getting started with MCP (Model Context Protocol) and want to see how tools, servers, and AI agents work together — this is the right place to start. No cloud setup, no API keys, no complex infrastructure. Just Python, a CSV file, and a running Ollama model.

Built on the Superstore sales dataset, this project exposes 7 simple analytical tools that can be queried by Claude Desktop or a LangChain agent — making it a great hands-on introduction to the MCP ecosystem.

---

## Tech Stack

| Layer      | Technology                                      |
| ---------- | ----------------------------------------------- |
| MCP Server | [FastMCP](https://github.com/jlowin/fastmcp) 3.4.2 |
| Data       | Pandas + Superstore CSV                         |
| LLM        | Ollama (qwen2.5:7b)                             |
| Agent      | LangChain 1.3.x + langchain-mcp-adapters        |
| Transport  | stdio (Claude Desktop) / subprocess (LangChain) |

---

## Project Structure

```
simple_localmCP/
├── Superstore.csv          # Dataset
├── tools.py                # 7 data functions using pandas
├── server.py               # FastMCP server exposing tools over stdio
├── langchain_client.py     # LangChain agent demo
├── requirements.txt
└── README.md
```

---

## Installation

**1. Clone the repository**

```bash
git clone --no-checkout --depth=1 --filter=blob:none https://github.com/IshaanLabs/Awesome-AI-Agents.git
cd Awesome-AI-Agents
git sparse-checkout set beginner-friendly-LocalMCP-Server
git checkout
cd beginner-friendly-LocalMCP-Server
```

**2. Install Python dependencies**

```bash
pip install -r requirements.txt
```

**3. Install Ollama and pull the model**

Download Ollama from [ollama.com](https://ollama.com) then run:

```bash
ollama pull qwen2.5:7b
```

---

## Configuration

### Claude Desktop

Open your `claude_desktop_config.json` and add:

```json
{
  "mcpServers": {
    "superstore": {
      "command": "C:\\Users\\<your-username>\\AppData\\Local\\Programs\\Python\\Python310\\python.exe",
      "args": ["D:\\path\\to\\beginner-friendly-LocalMCP-Server\\server.py"]
    }
  }
}
```

> Make sure `fastmcp` and `pandas` are installed on the Windows Python used by Claude Desktop.

---

## Usage

### Run MCP server directly

```bash
python server.py
```

### Run LangChain agent demo

```bash
python langchain_client.py
```

---

## Tools Available

| Tool                   | Description                                           |
| ---------------------- | ----------------------------------------------------- |
| `summary`            | Total sales, profit, and order count                  |
| `sales_by_category`  | Breakdown by Furniture / Office Supplies / Technology |
| `top_products`       | Top N products by Sales or Profit                     |
| `sales_by_region`    | Sales and profit per region                           |
| `orders_by_customer` | All orders for a given customer name                  |
| `loss_making_orders` | All orders with negative profit, sorted by worst loss |
| `segment_summary`    | Summary for Consumer / Corporate / Home Office        |

---

## Sample Queries

**Summary**

- What is the total sales and profit in the dataset?
- How many orders are there in total?

**Category**

- Which product category generates the most profit?
- Compare sales across Furniture, Office Supplies, and Technology.

**Products**

- What are the top 5 products by sales?
- Show me the top 3 most profitable products.
- Which 10 products have the highest sales?

**Region**

- Which region has the highest sales?
- Compare profit across all regions.
- Which region is least profitable?

**Customer**

- Show me all orders for Tracy Blumstein.
- What did Joel Eaton buy?
- Find all orders for customer Brosina Hoffman.

**Loss Analysis**

- Which orders are losing money?
- Show me all orders with negative profit.
- What are the worst loss-making orders?

**Segment**

- Give me a sales summary for the Corporate segment.
- How is the Consumer segment performing?
- Compare Home Office segment sales and profit.

**Multi-tool (LangChain agent)**

- Which region and category combination should we focus on to improve profit?
- What percentage of total sales comes from the West region?
- Are there customers with both profitable and loss-making orders?

---

## Contributing

Contributions to this project are welcome! If you have ideas for improvements, bug fixes, or new features, feel free to open an issue or submit a pull request.

---

## License

This project is licensed under the MIT License - see the [MIT License](https://opensource.org/licenses/MIT) file for details.
