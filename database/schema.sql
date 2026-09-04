PRAGMA foreign_keys = ON;

BEGIN TRANSACTION;

-- ============================================================
-- PRODUCTS
-- ============================================================
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    sku TEXT UNIQUE NOT NULL
);

-- ============================================================
-- LOCATIONS
-- ============================================================
CREATE TABLE locations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    warehouse TEXT NOT NULL,
    "row" TEXT NOT NULL,
    bin TEXT NOT NULL,

    UNIQUE (warehouse, "row", bin)
);

-- ============================================================
-- INVENTORY
-- ============================================================
CREATE TABLE inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    location_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity >= 0),

    FOREIGN KEY (product_id)
        REFERENCES products(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    FOREIGN KEY (location_id)
        REFERENCES locations(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    UNIQUE (product_id, location_id)
);

-- ============================================================
-- ORDERS
-- ============================================================
CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_number TEXT UNIQUE NOT NULL,
    status TEXT NOT NULL,
    created_at DATETIME NOT NULL,

    CHECK (
        status IN (
            'Pending',
            'Processing',
            'Shipped',
            'Delivered'
        )
    )
);

-- ============================================================
-- ORDER ITEMS
-- ============================================================
CREATE TABLE order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),

    FOREIGN KEY (order_id)
        REFERENCES orders(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    FOREIGN KEY (product_id)
        REFERENCES products(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

-- ============================================================
-- STOCK MOVEMENTS
-- ============================================================
CREATE TABLE stock_movements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    from_location_id INTEGER,
    to_location_id INTEGER,
    movement_type TEXT NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    timestamp DATETIME NOT NULL,

    FOREIGN KEY (product_id)
        REFERENCES products(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    FOREIGN KEY (from_location_id)
        REFERENCES locations(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    FOREIGN KEY (to_location_id)
        REFERENCES locations(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CHECK (
        movement_type IN (
            'RECEIVE',
            'PICK',
            'TRANSFER',
            'ADJUSTMENT'
        )
    ),

    -- RECEIVE: new stock enters a location
    -- PICK: stock leaves a location
    -- TRANSFER: stock moves between two locations
    -- ADJUSTMENT: inventory correction at a location
    CHECK (
        (movement_type = 'RECEIVE'
            AND from_location_id IS NULL
            AND to_location_id IS NOT NULL)

        OR

        (movement_type = 'PICK'
            AND from_location_id IS NOT NULL
            AND to_location_id IS NULL)

        OR

        (movement_type = 'TRANSFER'
            AND from_location_id IS NOT NULL
            AND to_location_id IS NOT NULL
            AND from_location_id != to_location_id)

        OR

        (movement_type = 'ADJUSTMENT'
            AND (
                (from_location_id IS NULL AND to_location_id IS NOT NULL)
                OR
                (from_location_id IS NOT NULL AND to_location_id IS NULL)
            )
        )
    )
);

-- ============================================================
-- INDEXES
-- ============================================================

-- Product search
CREATE INDEX idx_products_name
ON products(name);

CREATE INDEX idx_products_sku
ON products(sku);

-- Inventory lookups
CREATE INDEX idx_inventory_product
ON inventory(product_id);

CREATE INDEX idx_inventory_location
ON inventory(location_id);

-- Location lookups
CREATE INDEX idx_locations_warehouse_row
ON locations(warehouse, "row");

CREATE INDEX idx_locations_bin
ON locations(bin);

-- Order lookups
CREATE INDEX idx_orders_status
ON orders(status);

CREATE INDEX idx_orders_created_at
ON orders(created_at);

-- Order item lookups
CREATE INDEX idx_order_items_order
ON order_items(order_id);

CREATE INDEX idx_order_items_product
ON order_items(product_id);

-- Stock movement history
CREATE INDEX idx_stock_movements_product
ON stock_movements(product_id);

CREATE INDEX idx_stock_movements_timestamp
ON stock_movements(timestamp);

CREATE INDEX idx_stock_movements_from_location
ON stock_movements(from_location_id);

CREATE INDEX idx_stock_movements_to_location
ON stock_movements(to_location_id);

COMMIT;