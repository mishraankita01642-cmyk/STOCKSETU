from database import get_connection


def insert_data():

    # Connect to database
    conn = get_connection()
    cursor = conn.cursor()

    # --------------------------------
    # PRODUCT DATA
    # --------------------------------
    products = [
        (1, "Wireless Mouse", "WM001", "Electronics"),
        (2, "Keyboard", "KB001", "Electronics"),
        (3, "USB Cable", "USB001", "Accessories"),
        (4, "Webcam", "WC001", "Electronics")
    ]

    cursor.executemany("""
        INSERT OR IGNORE INTO products
        (product_id, name, sku, category)
        VALUES (?, ?, ?, ?)
    """, products)

    # --------------------------------
    # LOCATION DATA
    # --------------------------------
    locations = [
        (1, "WH-01", "A", "A01"),
        (2, "WH-01", "A", "A02"),
        (3, "WH-01", "A", "A03"),
        (4, "WH-01", "B", "B01"),
        (5, "WH-01", "B", "B02"),
        (6, "WH-01", "C", "C01"),
        (7, "WH-01", "C", "C02")
    ]

    cursor.executemany("""
        INSERT OR IGNORE INTO locations
        (location_id, warehouse_code, row_code, bin_code)
        VALUES (?, ?, ?, ?)
    """, locations)

    # --------------------------------
    # INVENTORY DATA
    # --------------------------------
    inventory = [
        (1, 1, 1, 15),   # Wireless Mouse → A01 → 15
        (2, 1, 2, 37),   # Wireless Mouse → A02 → 37
        (3, 2, 4, 20),   # Keyboard → B01 → 20
        (4, 2, 5, 3),    # Keyboard → B02 → 3
        (5, 3, 3, 4),    # USB Cable → A03 → 4
        (6, 4, 6, 12)    # Webcam → C01 → 12
    ]

    cursor.executemany("""
        INSERT OR IGNORE INTO inventory
        (inventory_id, product_id, location_id, quantity)
        VALUES (?, ?, ?, ?)
    """, inventory)

    # Save changes
    conn.commit()

    # Close connection
    conn.close()

    print("Test data inserted successfully!")


# Run the function
if __name__ == "__main__":
    insert_data()
