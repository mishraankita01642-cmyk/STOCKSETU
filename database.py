import sqlite3

# Name of our temporary database
DB_NAME = "stocksetu_test.db"


# Function to connect to the database
def get_connection():
    return sqlite3.connect(DB_NAME)


# Function to create all required tables
def create_tables():

    # Connect to database
    conn = get_connection()

    # Create cursor
    cursor = conn.cursor()

    # -----------------------------
    # PRODUCTS TABLE
    # -----------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            sku TEXT UNIQUE NOT NULL,
            category TEXT
        )
    """)

    # -----------------------------
    # LOCATIONS TABLE
    # -----------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS locations (
            location_id INTEGER PRIMARY KEY,
            warehouse_code TEXT NOT NULL,
            row_code TEXT NOT NULL,
            bin_code TEXT UNIQUE NOT NULL
        )
    """)

    # -----------------------------
    # INVENTORY TABLE
    # -----------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            inventory_id INTEGER PRIMARY KEY,
            product_id INTEGER NOT NULL,
            location_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,

            FOREIGN KEY (product_id)
                REFERENCES products(product_id),

            FOREIGN KEY (location_id)
                REFERENCES locations(location_id)
        )
    """)

    # Save changes
    conn.commit()

    # Close database connection
    conn.close()


# Run this part only when database.py
# is executed directly
if __name__ == "__main__":

    create_tables()

    print("Database and tables created successfully!")