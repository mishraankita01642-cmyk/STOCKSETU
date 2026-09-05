import sqlite3
from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

DB_FILE = "inventory.db"


def get_db():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def process_order_fulfillment(conn, order_items):
    """Fulfills orders by selecting available inventory locations."""
    cursor = conn.cursor()
    pick_list = []

    try:
        with conn:
            for item in order_items:
                product_id = item["product_id"]
                requested_qty = item["qty"]

                cursor.execute(
                    """
                    SELECT i.product_id, i.location_id, i.quantity,
                           p.name AS product_name, l.*
                    FROM inventory i
                    JOIN products p ON i.product_id = p.id
                    JOIN locations l ON i.location_id = l.id
                    WHERE i.product_id = ? AND i.quantity >= ?
                    LIMIT 1
                    """,
                    (product_id, requested_qty),
                )

                stock_record = cursor.fetchone()

                if not stock_record:
                    raise ValueError(
                        f"Insufficient stock for Product ID: {product_id}"
                    )

                rec_dict = dict(stock_record)

                loc_code = rec_dict.get(
                    "location_code",
                    f"{rec_dict.get('zone', 'WH')}-"
                    f"{rec_dict.get('aisle', rec_dict.get('row_number', '0'))}-"
                    f"{rec_dict.get('shelf', rec_dict.get('bin_number', '0'))}"
                )

                pick_list.append({
                    "product_name": stock_record["product_name"],
                    "location_code": loc_code,
                    "qty_to_pick": requested_qty,
                })

                # Deduct inventory
                cursor.execute(
                    """
                    UPDATE inventory
                    SET quantity = quantity - ?
                    WHERE product_id = ? AND location_id = ?
                    """,
                    (requested_qty, product_id, stock_record["location_id"]),
                )

                # Log stock movement
                cursor.execute(
                    """
                    INSERT INTO stock_movements
                    (
                        product_id,
                        from_location_id,
                        to_location_id,
                        quantity,
                        movement_type,
                        timestamp
                    )
                    VALUES
                     (?, ?, NULL, ?, 'PICK', CURRENT_TIMESTAMP)
                    """,
                    (
                        product_id,
                        stock_record["location_id"],
                        requested_qty,
                    ),
                )

        return pick_list

    except Exception as e:
        conn.rollback()
        raise e


app = FastAPI(title="Pick Generator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class OrderItem(BaseModel):
    product_id: int = Field(..., json_schema_extra={"examples": [1]})
    qty: int = Field(..., gt=0, json_schema_extra={"examples": [2]})


class OrderRequest(BaseModel):
    items: List[OrderItem]


@app.get("/")
def read_root():
    return {"status": "Pick Generator API connected to inventory.db"}


@app.get("/api/stock")
def get_current_stock():
    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT p.id AS product_id,
                   p.name,
                   i.quantity,
                   l.*
            FROM inventory i
            JOIN products p ON i.product_id = p.id
            JOIN locations l ON i.location_id = l.id
            LIMIT 100
            """
        )

        rows = cursor.fetchall()

        stock_data = []

        for row in rows:
            r = dict(row)

            loc_code = r.get(
                "location_code",
                f"WH-{r.get('zone', r.get('row_number', 'A'))}-{r.get('shelf', r.get('bin_number', '1'))}"
            )

            stock_data.append({
                "product_id": r["product_id"],
                "name": r["name"],
                "quantity": r["quantity"],
                "location_code": loc_code,
            })

        return {"stock": stock_data}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database query failed: {str(e)}"
        )

    finally:
        conn.close()


@app.post("/api/generate-pick-list")
def generate_pick_list(order: OrderRequest):
    conn = get_db()

    try:
        order_items_dict = [item.model_dump() for item in order.items]

        pick_list = process_order_fulfillment(
            conn,
            order_items_dict,
        )

        return {
            "success": True,
            "pick_list": pick_list,
        }

    except ValueError as err:
        raise HTTPException(
            status_code=400,
            detail=str(err)
        )

    except Exception as err:
        raise HTTPException(
            status_code=500,
            detail=f"Server error during processing: {str(err)}"
        )

    finally:
        conn.close()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )