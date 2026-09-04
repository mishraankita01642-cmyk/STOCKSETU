"""
PS-3 E-Commerce Multi-Warehouse Inventory & Location Tracking System

SQLite deterministic seed generator.

Run:
    python seed.py

Dependencies:
    pip install Faker

Output:
    inventory.db
"""

from pathlib import Path
from datetime import datetime, timedelta
import sqlite3
import random
import sys

try:
    from faker import Faker
except ImportError:
    print("Faker is not installed.")
    print("Install it using:")
    print("    pip install Faker")
    sys.exit(1)


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DB_FILE = BASE_DIR / "inventory.db"
SCHEMA_FILE = BASE_DIR / "schema.sql"

RANDOM_SEED = 20260904

PRODUCT_COUNT = 750
ORDER_COUNT = 25

WAREHOUSE_NAME = "MAIN_WH"

ROWS = ["A", "B", "C", "D"]
BINS_PER_ROW = 10

LOW_STOCK_THRESHOLD = 5


# ============================================================
# RANDOM / FAKER SETUP
# ============================================================

random.seed(RANDOM_SEED)

fake = Faker()
fake.seed_instance(RANDOM_SEED)


# ============================================================
# PRODUCT DATA
# ============================================================

PRODUCT_TEMPLATES = {
    "Electronics": [
        "LED Monitor",
        "Desktop Speaker",
        "USB Microphone",
        "Webcam",
        "Wireless Adapter",
        "Bluetooth Speaker",
        "Portable SSD",
        "External Hard Drive",
        "Smart Plug",
        "Digital Alarm Clock",
    ],

    "Accessories": [
        "Wireless Mouse",
        "Mechanical Keyboard",
        "Laptop Stand",
        "USB Hub",
        "Mouse Pad",
        "Keyboard Wrist Rest",
        "HDMI Cable",
        "USB-C Cable",
        "Ethernet Cable",
        "Laptop Sleeve",
    ],

    "Home Appliances": [
        "Electric Kettle",
        "Table Fan",
        "Air Purifier",
        "Room Heater",
        "Coffee Maker",
        "Hand Blender",
        "Toaster",
        "Desk Lamp",
        "Digital Weighing Scale",
        "Mini Vacuum Cleaner",
    ],

    "Office Supplies": [
        "Notebook",
        "Ball Pen Set",
        "Stapler",
        "Paper Punch",
        "Desk Organizer",
        "Document Folder",
        "Calculator",
        "Sticky Notes",
        "Whiteboard Marker Set",
        "File Storage Box",
    ],

    "Gaming": [
        "Gaming Mouse",
        "Gaming Keyboard",
        "Gaming Headset",
        "Game Controller",
        "Gaming Mouse Pad",
        "Controller Stand",
        "USB Gaming Microphone",
        "Gaming Webcam",
        "RGB Desk Light",
        "Console Cooling Stand",
    ],

    "Mobile Devices": [
        "Android Smartphone",
        "5G Smartphone",
        "Feature Phone",
        "Power Bank",
        "Wireless Charger",
        "Fast Charger",
        "Phone Stand",
        "Phone Case",
        "Screen Protector",
        "Car Phone Holder",
    ],
}

BRANDS = [
    "NovaTech",
    "ByteCraft",
    "Orbit",
    "ZenCore",
    "PixelPro",
    "TechNest",
    "AeroLink",
    "Voltix",
    "Nexora",
    "CoreMax",
    "PrimeGear",
    "SmartEdge",
]

PRODUCT_VARIANTS = [
    "Basic",
    "Standard",
    "Pro",
    "Plus",
    "Max",
    "Lite",
    "Premium",
    "Ultra",
]


# ============================================================
# DATABASE CREATION
# ============================================================

def create_database():
    """
    Delete old database and create a fresh SQLite database.
    """

    if DB_FILE.exists():
        DB_FILE.unlink()

    connection = sqlite3.connect(DB_FILE)

    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA journal_mode = WAL")

    schema = SCHEMA_FILE.read_text(encoding="utf-8")

    connection.executescript(schema)

    return connection


# ============================================================
# CREATE LOCATIONS
# ============================================================

def create_locations(connection):
    """
    Creates:

    MAIN_WH
      A01-A10
      B01-B10
      C01-C10
      D01-D10
    """

    locations = []

    for row in ROWS:

        for number in range(1, BINS_PER_ROW + 1):

            bin_name = f"{row}{number:02d}"

            locations.append(
                (
                    WAREHOUSE_NAME,
                    row,
                    bin_name
                )
            )

    connection.executemany(
        """
        INSERT INTO locations
        (
            warehouse,
            "row",
            bin
        )
        VALUES (?, ?, ?)
        """,
        locations
    )

    return connection.execute(
        """
        SELECT id, warehouse, "row", bin
        FROM locations
        ORDER BY id
        """
    ).fetchall()


# ============================================================
# CREATE PRODUCTS
# ============================================================

def create_products(connection):
    """
    Generates 750 products programmatically.

    SKU format:

        SH0001
        SH0002
        SH0003
        ...
        SH0750
    """

    categories = list(PRODUCT_TEMPLATES.keys())

    products = []

    for product_id in range(1, PRODUCT_COUNT + 1):

        category = random.choice(categories)

        product_type = random.choice(
            PRODUCT_TEMPLATES[category]
        )

        brand = random.choice(BRANDS)

        variant = random.choice(PRODUCT_VARIANTS)

        name = f"{brand} {product_type} {variant}"

        sku = f"SH{product_id:04d}"

        products.append(
            (
                name,
                sku
            )
        )

    connection.executemany(
        """
        INSERT INTO products
        (
            name,
            sku
        )
        VALUES (?, ?)
        """,
        products
    )

    return connection.execute(
        """
        SELECT id, name, sku
        FROM products
        ORDER BY id
        """
    ).fetchall()


# ============================================================
# INITIAL INVENTORY
# ============================================================

def create_initial_inventory(
    connection,
    products,
    locations
):
    """
    Assign every product to exactly one valid location.

    At least 10% of products are deliberately low stock.

    Stock ranges:

        Low       : 0-5
        Medium    : 20-150
        High      : 151-500
    """

    inventory = []

    movement_records = []

    movement_id = 1

    base_time = datetime(2026, 8, 1, 8, 0, 0)

    # At least 10% low-stock products.
    low_stock_count = max(
        int(PRODUCT_COUNT * 0.10),
        75
    )

    low_stock_products = set(
        random.sample(
            range(1, PRODUCT_COUNT + 1),
            low_stock_count
        )
    )

    for index, product in enumerate(products):

        product_id = product[0]

        location = random.choice(locations)

        location_id = location[0]

        # ----------------------------------------------------
        # Generate realistic quantity
        # ----------------------------------------------------

        if product_id in low_stock_products:

            quantity = random.randint(0, 5)

        else:

            stock_type = random.choices(
                ["medium", "high"],
                weights=[70, 30],
                k=1
            )[0]

            if stock_type == "medium":
                quantity = random.randint(20, 150)
            else:
                quantity = random.randint(151, 500)

        # ----------------------------------------------------
        # Inventory row
        # ----------------------------------------------------

        inventory.append(
            (
                product_id,
                location_id,
                quantity
            )
        )

        # ----------------------------------------------------
        # Initial RECEIVE movement
        # ----------------------------------------------------

        movement_time = (
            base_time
            + timedelta(minutes=index * 5)
        )

        # A zero-stock product still gets a RECEIVE history
        # only when quantity > 0.
        if quantity > 0:

            movement_records.append(
                (
                    product_id,
                    None,
                    location_id,
                    "RECEIVE",
                    quantity,
                    movement_time.isoformat(sep=" ")
                )
            )

            movement_id += 1

    connection.executemany(
        """
        INSERT INTO inventory
        (
            product_id,
            location_id,
            quantity
        )
        VALUES (?, ?, ?)
        """,
        inventory
    )

    connection.executemany(
        """
        INSERT INTO stock_movements
        (
            product_id,
            from_location_id,
            to_location_id,
            movement_type,
            quantity,
            timestamp
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        movement_records
    )

    return inventory


# ============================================================
# INVENTORY BALANCE HELPERS
# ============================================================

def load_balances(connection):
    """
    Creates an in-memory representation:

        (product_id, location_id) -> quantity
    """

    rows = connection.execute(
        """
        SELECT
            product_id,
            location_id,
            quantity
        FROM inventory
        """
    ).fetchall()

    balances = {}

    for product_id, location_id, quantity in rows:

        balances[
            (product_id, location_id)
        ] = quantity

    return balances


def update_inventory_row(
    connection,
    product_id,
    location_id,
    new_quantity
):
    """
    Updates the inventory row.
    """

    connection.execute(
        """
        UPDATE inventory

        SET quantity = ?

        WHERE product_id = ?
        AND location_id = ?
        """,
        (
            new_quantity,
            product_id,
            location_id
        )
    )


# ============================================================
# TRANSFER MOVEMENTS
# ============================================================

def create_transfers(
    connection,
    locations,
    balances,
    movement_records,
    movement_counter
):
    """
    Creates realistic TRANSFER movements.

    Only transfers products that actually have
    sufficient stock.
    """

    candidates = [
        key
        for key, quantity in balances.items()
        if quantity >= 10
    ]

    if not candidates:
        return movement_counter

    transfer_count = min(
        100,
        len(candidates)
    )

    base_time = datetime(2026, 8, 10, 9, 0, 0)

    for i in range(transfer_count):

        product_id, source_location_id = random.choice(
            candidates
        )

        available = balances[
            (product_id, source_location_id)
        ]

        if available < 5:
            continue

        destination_location = random.choice(locations)

        destination_location_id = destination_location[0]

        if destination_location_id == source_location_id:
            continue

        quantity = random.randint(
            1,
            min(20, available)
        )

        # Remove from source.
        balances[
            (product_id, source_location_id)
        ] -= quantity

        # Add to destination.
        balances[
            (product_id, destination_location_id)
        ] = balances.get(
            (product_id, destination_location_id),
            0
        ) + quantity

        # Update source.
        update_inventory_row(
            connection,
            product_id,
            source_location_id,
            balances[
                (product_id, source_location_id)
            ]
        )

        # Destination may already have an inventory row.
        destination_exists = connection.execute(
            """
            SELECT id
            FROM inventory
            WHERE product_id = ?
            AND location_id = ?
            """,
            (
                product_id,
                destination_location_id
            )
        ).fetchone()

        if destination_exists:

            update_inventory_row(
                connection,
                product_id,
                destination_location_id,
                balances[
                    (product_id, destination_location_id)
                ]
            )

        else:

            connection.execute(
                """
                INSERT INTO inventory
                (
                    product_id,
                    location_id,
                    quantity
                )
                VALUES (?, ?, ?)
                """,
                (
                    product_id,
                    destination_location_id,
                    balances[
                        (product_id, destination_location_id)
                    ]
                )
            )

        movement_time = (
            base_time
            + timedelta(minutes=i * 15)
        )

        movement_records.append(
            (
                product_id,
                source_location_id,
                destination_location_id,
                "TRANSFER",
                quantity,
                movement_time.isoformat(sep=" ")
            )
        )

        movement_counter += 1

    return movement_counter


# ============================================================
# ADJUSTMENT MOVEMENTS
# ============================================================

def create_adjustments(
    connection,
    locations,
    balances,
    movement_records,
    movement_counter
):
    """
    Creates inventory adjustments.

    Adjustments are always safe:
    inventory never becomes negative.
    """

    candidate_keys = list(balances.keys())

    adjustment_count = min(
        50,
        len(candidate_keys)
    )

    base_time = datetime(2026, 8, 15, 10, 0, 0)

    for i in range(adjustment_count):

        product_id, location_id = random.choice(
            candidate_keys
        )

        current_quantity = balances[
            (product_id, location_id)
        ]

        # Mostly small corrections.
        adjustment = random.randint(-3, 10)

        # Don't allow negative inventory.
        if current_quantity + adjustment < 0:
            adjustment = 0

        if adjustment == 0:
            continue

        new_quantity = (
            current_quantity
            + adjustment
        )

        balances[
            (product_id, location_id)
        ] = new_quantity

        update_inventory_row(
            connection,
            product_id,
            location_id,
            new_quantity
        )

        movement_time = (
            base_time
            + timedelta(minutes=i * 20)
        )

        if adjustment > 0:

            movement_records.append(
                (
                    product_id,
                    None,
                    location_id,
                    "ADJUSTMENT",
                    adjustment,
                    movement_time.isoformat(sep=" ")
                )
            )

        else:

            movement_records.append(
                (
                    product_id,
                    location_id,
                    None,
                    "ADJUSTMENT",
                    abs(adjustment),
                    movement_time.isoformat(sep=" ")
                )
            )

        movement_counter += 1

    return movement_counter


# ============================================================
# ORDERS
# ============================================================

def create_orders(
    connection,
    products,
    locations,
    balances,
    movement_records,
    movement_counter
):
    """
    Creates 25 orders.

    Every order:
        - has 1-5 items
        - references valid products
        - only orders available stock
        - creates PICK movements
        - decreases inventory
    """

    statuses = [
        "Pending",
        "Processing",
        "Shipped",
        "Delivered"
    ]

    # Products with at least 1 unit available.
    available_products = [
        product_id
        for (product_id, location_id), quantity
        in balances.items()
        if quantity > 0
    ]

    base_time = datetime(2026, 8, 20, 9, 0, 0)

    order_records = []

    order_item_records = []

    for order_id in range(1, ORDER_COUNT + 1):

        order_number = (
            f"ORD-{10000 + order_id}"
        )

        status = random.choice(statuses)

        created_at = (
            base_time
            + timedelta(hours=order_id * 6)
        )

        order_records.append(
            (
                order_number,
                status,
                created_at.isoformat(sep=" ")
            )
        )

    connection.executemany(
        """
        INSERT INTO orders
        (
            order_number,
            status,
            created_at
        )
        VALUES (?, ?, ?)
        """,
        order_records
    )

    # --------------------------------------------------------
    # Generate items after orders exist.
    # --------------------------------------------------------

    order_rows = connection.execute(
        """
        SELECT id, order_number, created_at
        FROM orders
        ORDER BY id
        """
    ).fetchall()

    item_id = 1

    for order_id, order_number, created_at in order_rows:

        # Refresh list because stock changes after every order.
        available_products = list({
            product_id
            for (
                product_id,
                location_id
            ), quantity in balances.items()
            if quantity > 0
        })

        if not available_products:
            break

        item_count = random.randint(
            1,
            min(5, len(available_products))
        )

        selected_products = random.sample(
            available_products,
            item_count
        )

        for product_id in selected_products:

            # Find locations containing this product.
            product_locations = [
                (
                    location_id,
                    quantity
                )
                for (
                    p_id,
                    location_id
                ), quantity in balances.items()
                if p_id == product_id
                and quantity > 0
            ]

            if not product_locations:
                continue

            # Choose a location with stock.
            location_id, available_quantity = random.choice(
                product_locations
            )

            ordered_quantity = random.randint(
                1,
                min(5, available_quantity)
            )

            # ------------------------------------------------
            # Create order item
            # ------------------------------------------------

            order_item_records.append(
                (
                    order_id,
                    product_id,
                    ordered_quantity
                )
            )

            # ------------------------------------------------
            # Deduct inventory
            # ------------------------------------------------

            balances[
                (product_id, location_id)
            ] -= ordered_quantity

            update_inventory_row(
                connection,
                product_id,
                location_id,
                balances[
                    (product_id, location_id)
                ]
            )

            # ------------------------------------------------
            # PICK movement
            # ------------------------------------------------

            pick_time = (
                datetime.fromisoformat(created_at)
                + timedelta(minutes=random.randint(5, 60))
            )

            movement_records.append(
                (
                    product_id,
                    location_id,
                    None,
                    "PICK",
                    ordered_quantity,
                    pick_time.isoformat(sep=" ")
                )
            )

            movement_counter += 1

            item_id += 1

    connection.executemany(
        """
        INSERT INTO order_items
        (
            order_id,
            product_id,
            quantity
        )
        VALUES (?, ?, ?)
        """,
        order_item_records
    )

    return movement_counter


# ============================================================
# SAVE MOVEMENTS
# ============================================================

def save_movements(
    connection,
    movement_records
):
    """
    Saves movements generated by transfers,
    adjustments and picks.

    Initial RECEIVE movements are already inserted
    by create_initial_inventory().
    """

    connection.executemany(
        """
        INSERT INTO stock_movements
        (
            product_id,
            from_location_id,
            to_location_id,
            movement_type,
            quantity,
            timestamp
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        movement_records
    )


# ============================================================
# VERIFY DATA
# ============================================================

def verify_database(connection):
    """
    Runs integrity checks.
    """

    print("\nRunning database verification...")

    # --------------------------------------------------------
    # Foreign keys
    # --------------------------------------------------------

    fk_errors = connection.execute(
        "PRAGMA foreign_key_check"
    ).fetchall()

    if fk_errors:
        raise RuntimeError(
            f"Foreign key errors found: {fk_errors}"
        )

    print("✓ Foreign key integrity: PASS")

    # --------------------------------------------------------
    # Counts
    # --------------------------------------------------------

    tables = [
        "products",
        "locations",
        "inventory",
        "orders",
        "order_items",
        "stock_movements"
    ]

    print("\nRecord counts:")

    for table in tables:

        count = connection.execute(
            f"SELECT COUNT(*) FROM {table}"
        ).fetchone()[0]

        print(
            f"  {table:<18} {count}"
        )

    # --------------------------------------------------------
    # Product count
    # --------------------------------------------------------

    product_count = connection.execute(
        "SELECT COUNT(*) FROM products"
    ).fetchone()[0]

    if not 500 <= product_count <= 1000:
        raise RuntimeError(
            "Product count is outside required range."
        )

    print("✓ Product count 500-1000: PASS")

    # --------------------------------------------------------
    # Location count
    # --------------------------------------------------------

    location_count = connection.execute(
        "SELECT COUNT(*) FROM locations"
    ).fetchone()[0]

    if location_count != 40:
        raise RuntimeError(
            "Expected exactly 40 locations."
        )

    print("✓ 40 warehouse bins: PASS")

    # --------------------------------------------------------
    # Every product has inventory
    # --------------------------------------------------------

    missing_inventory = connection.execute(
        """
        SELECT p.id
        FROM products p
        LEFT JOIN inventory i
            ON i.product_id = p.id
        WHERE i.id IS NULL
        """
    ).fetchall()

    if missing_inventory:
        raise RuntimeError(
            f"Products without inventory: {missing_inventory[:10]}"
        )

    print("✓ Every product has inventory: PASS")

    # --------------------------------------------------------
    # Low-stock percentage
    # --------------------------------------------------------

    low_stock_count = connection.execute(
        """
        SELECT COUNT(*)
        FROM (
            SELECT
                p.id,
                COALESCE(SUM(i.quantity), 0) AS total_stock
            FROM products p
            LEFT JOIN inventory i
                ON i.product_id = p.id
            GROUP BY p.id
            HAVING total_stock <= 5
        )
        """
    ).fetchone()[0]

    low_stock_percentage = (
        low_stock_count / product_count
    ) * 100

    print(
        f"✓ Low-stock products: "
        f"{low_stock_count} "
        f"({low_stock_percentage:.2f}%)"
    )

    if low_stock_percentage < 10:
        raise RuntimeError(
            "Less than 10% products are low stock."
        )

    # --------------------------------------------------------
    # Invalid inventory quantities
    # --------------------------------------------------------

    invalid_inventory = connection.execute(
        """
        SELECT COUNT(*)
        FROM inventory
        WHERE quantity < 0
        """
    ).fetchone()[0]

    if invalid_inventory:
        raise RuntimeError(
            "Negative inventory found."
        )

    print("✓ No negative inventory: PASS")

    # --------------------------------------------------------
    # Orders with invalid quantities
    # --------------------------------------------------------

    invalid_orders = connection.execute(
        """
        SELECT COUNT(*)
        FROM order_items oi
        WHERE oi.quantity <= 0
        """
    ).fetchone()[0]

    if invalid_orders:
        raise RuntimeError(
            "Invalid order quantities found."
        )

    print("✓ Order quantities valid: PASS")

    # --------------------------------------------------------
    # SKU uniqueness
    # --------------------------------------------------------

    duplicate_skus = connection.execute(
        """
        SELECT sku, COUNT(*)
        FROM products
        GROUP BY sku
        HAVING COUNT(*) > 1
        """
    ).fetchall()

    if duplicate_skus:
        raise RuntimeError(
            f"Duplicate SKUs: {duplicate_skus}"
        )

    print("✓ SKU uniqueness: PASS")

    # --------------------------------------------------------
    # Location uniqueness
    # --------------------------------------------------------

    duplicate_locations = connection.execute(
        """
        SELECT warehouse, "row", bin, COUNT(*)
        FROM locations
        GROUP BY warehouse, "row", bin
        HAVING COUNT(*) > 1
        """
    ).fetchall()

    if duplicate_locations:
        raise RuntimeError(
            f"Duplicate locations: {duplicate_locations}"
        )

    print("✓ Location uniqueness: PASS")

    # --------------------------------------------------------
    # Movement references
    # --------------------------------------------------------

    invalid_movements = connection.execute(
        """
        SELECT COUNT(*)
        FROM stock_movements sm
        LEFT JOIN products p
            ON p.id = sm.product_id
        WHERE p.id IS NULL
        """
    ).fetchone()[0]

    if invalid_movements:
        raise RuntimeError(
            "Invalid stock movement product references."
        )

    print("✓ Stock movement references: PASS")

    print("\n====================================")
    print("DATABASE VERIFICATION SUCCESSFUL ✓")
    print("====================================")


# ============================================================
# MAIN
# ============================================================

def main():

    print("====================================")
    print("PS-3 DATABASE SEEDER")
    print("====================================")

    print("\nCreating fresh SQLite database...")

    connection = create_database()

    try:

        # ----------------------------------------------------
        # Products
        # ----------------------------------------------------

        print("Generating products...")

        products = create_products(
            connection
        )

        print(
            f"Created {len(products)} products."
        )

        # ----------------------------------------------------
        # Locations
        # ----------------------------------------------------

        print("Generating warehouse locations...")

        locations = create_locations(
            connection
        )

        print(
            f"Created {len(locations)} locations."
        )

        # ----------------------------------------------------
        # Initial inventory
        # ----------------------------------------------------

        print("Generating initial inventory...")

        inventory = create_initial_inventory(
            connection,
            products,
            locations
        )

        print(
            f"Created {len(inventory)} inventory records."
        )

        # ----------------------------------------------------
        # Load current balances
        # ----------------------------------------------------

        balances = load_balances(
            connection
        )

        movement_records = []

        movement_counter = 1

        # ----------------------------------------------------
        # Transfers
        # ----------------------------------------------------

        print("Generating stock transfers...")

        movement_counter = create_transfers(
            connection,
            locations,
            balances,
            movement_records,
            movement_counter
        )

        # ----------------------------------------------------
        # Adjustments
        # ----------------------------------------------------

        print("Generating inventory adjustments...")

        movement_counter = create_adjustments(
            connection,
            locations,
            balances,
            movement_records,
            movement_counter
        )

        # ----------------------------------------------------
        # Orders + PICK movements
        # ----------------------------------------------------

        print("Generating orders...")

        movement_counter = create_orders(
            connection,
            products,
            locations,
            balances,
            movement_records,
            movement_counter
        )

        # ----------------------------------------------------
        # Save generated movements
        # ----------------------------------------------------

        print("Saving stock movement history...")

        save_movements(
            connection,
            movement_records
        )

        # ----------------------------------------------------
        # Commit
        # ----------------------------------------------------

        connection.commit()

        # ----------------------------------------------------
        # Verification
        # ----------------------------------------------------

        verify_database(
            connection
        )

        print("\nDatabase created successfully:")
        print(DB_FILE)

    except Exception:

        connection.rollback()

        raise

    finally:

        connection.close()


if __name__ == "__main__":
    main()