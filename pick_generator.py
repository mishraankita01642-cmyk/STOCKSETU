import sqlite3

def setup_mock_database():
    """Creates a temporary in-memory SQLite database for testing."""
    # Using ':memory:' keeps everything in RAM without touching disk
    conn = sqlite3.connect(':memory:')
    # Enable dict-like column access
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 1. Create Tables
    cursor.executescript('''
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sku TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL
        );

        CREATE TABLE locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            warehouse_name TEXT NOT NULL,
            row_number TEXT NOT NULL,
            bin_number TEXT NOT NULL,
            location_code TEXT UNIQUE NOT NULL
        );

        CREATE TABLE stock (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            location_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 0,
            UNIQUE(product_id, location_id)
        );

        CREATE TABLE stock_movements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            from_location_id INTEGER,
            to_location_id INTEGER,
            quantity INTEGER NOT NULL,
            movement_type TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')

    # 2. Seed Mock Data
    cursor.executescript('''
        INSERT INTO products (id, sku, name) VALUES 
            (1, 'MOUSE-01', 'Wireless Mouse'),
            (2, 'KEY-01', 'Mechanical Keyboard');

        INSERT INTO locations (id, warehouse_name, row_number, bin_number, location_code) VALUES 
            (101, 'WH-01', 'A', 'A02', 'WH-01-A-A02'),
            (102, 'WH-01', 'B', 'B01', 'WH-01-B-B01');

        -- Wireless Mouse in Bin A02 (Qty: 37), Keyboard in Bin B01 (Qty: 10)
        INSERT INTO stock (product_id, location_id, quantity) VALUES 
            (1, 101, 37),
            (2, 102, 10);
    ''')
    conn.commit()
    return conn

# ==========================================
# YOUR CORE BUSINESS LOGIC (PERSON 4b)
# ==========================================

def process_order_fulfillment(conn, order_items):
    """
    Takes an order array, finds bin locations, generates a pick list,
    deducts stock balances, and writes audit movement logs atomically.
    """
    cursor = conn.cursor()
    pick_list = []

    try:
        # Use Python context manager for atomic database transaction
        with conn:
            for item in order_items:
                product_id = item['product_id']
                requested_qty = item['qty']

                # Find available stock and exact bin coordinates
                cursor.execute('''
                    SELECT s.product_id, s.location_id, s.quantity, p.name AS product_name, 
                           l.location_code, l.row_number, l.bin_number
                    FROM stock s
                    JOIN products p ON s.product_id = p.id
                    JOIN locations l ON s.location_id = l.id
                    WHERE s.product_id = ? AND s.quantity >= ?
                    LIMIT 1
                ''', (product_id, requested_qty))

                stock_record = cursor.fetchone()

                if not stock_record:
                    raise ValueError(f"Insufficient stock for Product ID: {product_id}")

                # 1. Build pick list response item
                pick_list.append({
                    "product_name": stock_record["product_name"],
                    "location_code": stock_record["location_code"],
                    "row": stock_record["row_number"],
                    "bin": stock_record["bin_number"],
                    "qty_to_pick": requested_qty
                })

                # 2. Reduce stock balance
                cursor.execute('''
                    UPDATE stock 
                    SET quantity = quantity - ? 
                    WHERE product_id = ? AND location_id = ?
                ''', (requested_qty, product_id, stock_record["location_id"]))

                # 3. Write outward audit movement record
                cursor.execute('''
                    INSERT INTO stock_movements (product_id, from_location_id, to_location_id, quantity, movement_type)
                    VALUES (?, ?, NULL, ?, 'OUTWARD')
                ''', (product_id, stock_record["location_id"], requested_qty))

        return pick_list

    except Exception as e:
        conn.rollback()
        raise e

# ==========================================
# RUN INDEPENDENT TESTS
# ==========================================
if __name__ == "__main__":
    conn = setup_mock_database()
    print("--- STARTING PYTHON ORDER PICK GENERATOR TEST ---\n")

    # Test Case 1: Order #ORD1024 (2 Mice, 1 Keyboard)
    mock_order = [
        {"product_id": 1, "qty": 2},
        {"product_id": 2, "qty": 1}
    ]

    print("📥 Submitting Order #ORD1024...")
    pick_list = process_order_fulfillment(conn, mock_order)

    print("\n✅ GENERATED PICK LIST:")
    for item in pick_list:
        print(f"  • {item['product_name']} ➔ Row {item['row']}, Bin {item['bin']} ({item['location_code']}) ➔ Pick {item['qty_to_pick']}")

    print("\n📊 UPDATED STOCK BALANCES:")
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.name, s.quantity, l.location_code 
        FROM stock s 
        JOIN products p ON s.product_id = p.id 
        JOIN locations l ON s.location_id = l.id
    ''')
    for row in cursor.fetchall():
        print(f"  • {row['name']}: {row['quantity']} units left in {row['location_code']}")

    print("\n📜 AUDIT LOGS (stock_movements):")
    cursor.execute('SELECT * FROM stock_movements')
    for row in cursor.fetchall():
        print(f"  • Log #{row['id']}: Product {row['product_id']} | -{row['quantity']} units | Type: {row['movement_type']}")

    print("\n🚨 Testing Out-Of-Stock Guardrail...")
    try:
        process_order_fulfillment(conn, [{"product_id": 1, "qty": 100}])
    except ValueError as err:
        print(f"✅ Handled correctly: {err}")