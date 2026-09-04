import sqlite3
from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Point directly to your friend's SQLite database file
DB_FILE = "inventory.db"


def get_db():
    """Establishes connection to the actual SQLite database file."""
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def process_order_fulfillment(conn, order_items):
    """Takes an order array, finds bin locations, generates a pick list,

    deducts stock balances, and writes audit movement logs atomically.
    """
    cursor = conn.cursor()
    pick_list = []

    try:
        with conn:
            for item in order_items:
                product_id = item["product_id"]
                requested_qty = item["qty"]

                cursor.execute(
                    """
                    SELECT s.product_id, s.location_id, s.quantity, p.name AS product_name, 
                           l.location_code, l.row_number, l.bin_number
                    FROM stock s
                    JOIN products p ON s.product_id = p.id
                    JOIN locations l ON s.location_id = l.id
                    WHERE s.product_id = ? AND s.quantity >= ?
                    LIMIT 1
                """,
                    (product_id, requested_qty),
                )

                stock_record = cursor.fetchone()

                if not stock_record:
                    raise ValueError(
                        f"Insufficient stock for Product ID: {product_id}"
                    )

                pick_list.append({
                    "product_name": stock_record["product_name"],
                    "location_code": stock_record["location_code"],
                    "row": stock_record["row_number"],
                    "bin": stock_record["bin_number"],
                    "qty_to_pick": requested_qty,
                })

                # Deduct stock
                cursor.execute(
                    """
                    UPDATE stock 
                    SET quantity = quantity - ? 
                    WHERE product_id = ? AND location_id = ?
                """,
                    (requested_qty, product_id, stock_record["location_id"]),
                )

                # Log stock movement
                cursor.execute(
                    """
                    INSERT INTO stock_movements (product_id, from_location_id, to_location_id, quantity, movement_type)
                    VALUES (?, ?, NULL, ?, 'OUTWARD')
                """,
                    (product_id, stock_record["location_id"], requested_qty),
                )

        return pick_list

    except Exception as e:
        conn.rollback()
        raise e


app = FastAPI(title="Pick Generator API")

# Enable CORS for frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic Schemas (Updated for Pydantic v2)
class OrderItem(BaseModel):
    product_id: int = Field(..., json_schema_extra={"examples": [1]})
    qty: int = Field(..., gt=0, json_schema_extra={"examples": [2]})


class OrderRequest(BaseModel):
    items: List[OrderItem]


# Endpoints
@app.get("/")
def read_root():
    return {"status": "Pick Generator API connected to inventory.db"}


@app.get("/api/stock")
def get_current_stock():
    """Returns current inventory stock levels from inventory.db."""
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT p.id as product_id, p.name, s.quantity, l.location_code 
            FROM stock s 
            JOIN products p ON s.product_id = p.id 
            JOIN locations l ON s.location_id = l.id
        """)
        rows = cursor.fetchall()
        return {"stock": [dict(row) for row in rows]}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Database query failed: {str(e)}"
        )
    finally:
        conn.close()


@app.post("/api/generate-pick-list")
def generate_pick_list(order: OrderRequest):
    """Processes stock deduction and generates pick list in inventory.db."""
    conn = get_db()
    order_items_dict = [item.model_dump() for item in order.items]
    try:
        pick_list = process_order_fulfillment(conn, order_items_dict)
        return {"success": True, "pick_list": pick_list}
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err))
    except Exception as err:
        raise HTTPException(
            status_code=500, detail=f"Server error during processing: {str(err)}"
        )
    finally:
        conn.close()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)