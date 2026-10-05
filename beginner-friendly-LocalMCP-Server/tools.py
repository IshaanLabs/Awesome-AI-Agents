import pandas as pd
import os

CSV_PATH = os.path.join(os.path.dirname(__file__), "Superstore.csv")
df = pd.read_csv(CSV_PATH, encoding="latin-1")

print(f"Loaded {len(df)} rows from Superstore.csv")


def get_summary() -> dict:
    """Total sales, profit, and order count across the dataset."""
    return {
        "total_sales": round(df["Sales"].sum(), 2),
        "total_profit": round(df["Profit"].sum(), 2),
        "total_orders": df["Order ID"].nunique(),
        "total_rows": len(df),
    }


def get_sales_by_category() -> list:
    """Sales and profit breakdown by Category."""
    result = (
        df.groupby("Category")
        .agg(total_sales=("Sales", "sum"), total_profit=("Profit", "sum"))
        .round(2)
        .reset_index()
    )
    return result.to_dict(orient="records")


def get_top_products(n: int = 5, by: str = "Sales") -> list:
    """Top N products by Sales or Profit."""
    by = by if by in ("Sales", "Profit") else "Sales"
    result = (
        df.groupby("Product Name")[by]
        .sum()
        .round(2)
        .sort_values(ascending=False)
        .head(n)
        .reset_index()
    )
    result.columns = ["Product Name", by]
    return result.to_dict(orient="records")


def get_sales_by_region() -> list:
    """Sales and profit per region."""
    result = (
        df.groupby("Region")
        .agg(total_sales=("Sales", "sum"), total_profit=("Profit", "sum"))
        .round(2)
        .reset_index()
    )
    return result.to_dict(orient="records")


def get_orders_by_customer(customer_name: str) -> list:
    """All orders for a given customer name (case-insensitive partial match)."""
    mask = df["Customer Name"].str.contains(customer_name, case=False, na=False)
    result = df[mask][["Order ID", "Order Date", "Product Name", "Sales", "Profit"]].copy()
    result = result.round(2)
    return result.to_dict(orient="records")


def get_loss_making_orders() -> list:
    """Orders where profit is negative."""
    result = df[df["Profit"] < 0][
        ["Order ID", "Customer Name", "Product Name", "Sales", "Profit", "Discount"]
    ].copy()
    result = result.round(2).sort_values("Profit")
    return result.to_dict(orient="records")


def filter_by_segment(segment: str) -> dict:
    """Sales and profit summary for a given segment: Consumer, Corporate, or Home Office."""
    valid = ["Consumer", "Corporate", "Home Office"]
    if segment not in valid:
        return {"error": f"Invalid segment. Choose from {valid}"}
    subset = df[df["Segment"] == segment]
    return {
        "segment": segment,
        "total_sales": round(subset["Sales"].sum(), 2),
        "total_profit": round(subset["Profit"].sum(), 2),
        "order_count": subset["Order ID"].nunique(),
    }
