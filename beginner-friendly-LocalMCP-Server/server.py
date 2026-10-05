from fastmcp import FastMCP
from tools import (
    get_summary,
    get_sales_by_category,
    get_top_products,
    get_sales_by_region,
    get_orders_by_customer,
    get_loss_making_orders,
    filter_by_segment,
)

mcp = FastMCP("superstore-mcp")


@mcp.tool()
def summary() -> dict:
    """Get total sales, profit, and order count for the Superstore dataset."""
    print("Tool called: summary")
    return get_summary()


@mcp.tool()
def sales_by_category() -> list:
    """Get sales and profit breakdown by product category."""
    print("Tool called: sales_by_category")
    return get_sales_by_category()


@mcp.tool()
def top_products(n: int = 5, by: str = "Sales") -> list:
    """Get top N products by Sales or Profit. by must be 'Sales' or 'Profit'."""
    print(f"Tool called: top_products n={n} by={by}")
    return get_top_products(n, by)


@mcp.tool()
def sales_by_region() -> list:
    """Get sales and profit per region (South, West, Central, East)."""
    print("Tool called: sales_by_region")
    return get_sales_by_region()


@mcp.tool()
def orders_by_customer(customer_name: str) -> list:
    """Get all orders for a customer. Supports partial name match."""
    print(f"Tool called: orders_by_customer customer_name={customer_name}")
    return get_orders_by_customer(customer_name)


@mcp.tool()
def loss_making_orders() -> list:
    """Get all orders where profit is negative, sorted by worst loss first."""
    print("Tool called: loss_making_orders")
    return get_loss_making_orders()


@mcp.tool()
def segment_summary(segment: str) -> dict:
    """Get sales and profit summary for a segment: Consumer, Corporate, or Home Office."""
    print(f"Tool called: segment_summary segment={segment}")
    return filter_by_segment(segment)


if __name__ == "__main__":
    print("Starting Superstore MCP server (stdio)...")
    mcp.run(transport="stdio")
