const express = require("express");
const cors = require("cors");
const sqlite3 = require("sqlite3").verbose();
const path = require("path");

const app = express();

app.use(cors());
app.use(express.json());

// Product + location + stock (shared by all product routes)
const PRODUCT_QUERY = `
  SELECT p.id, p.name, p.sku,
         l.warehouse, l."row" AS row, l.bin,
         (SELECT SUM(quantity) FROM inventory WHERE product_id = p.id) AS quantity
  FROM products p
  LEFT JOIN inventory i ON i.id = (SELECT MIN(id) FROM inventory WHERE product_id = p.id)
  LEFT JOIN locations l ON l.id = i.location_id
`;

// Connect to SQLite Database
const dbPath = path.join(__dirname, "database", "inventory.db");

const db = new sqlite3.Database(dbPath, (err) => {
  if (err) {
    console.error("Database connection failed:", err.message);
  } else {
    console.log("Connected to SQLite Database");
  }
});

// Get all products
app.get("/api/products", (req, res) => {
  db.all(PRODUCT_QUERY, [], (err, rows) => {
    if (err) {
      return res.status(500).json({
        error: err.message
      });
    }

    res.json(rows);
  });
});

// Get product by ID
app.get("/api/products/:id", (req, res) => {
  db.get(
    PRODUCT_QUERY + " WHERE p.id = ?",
    [req.params.id],
    (err, row) => {
      if (err) {
        return res.status(500).json({
          error: err.message
        });
      }

      if (!row) {
        return res.status(404).json({
          message: "Product not found"
        });
      }

      res.json(row);
    }
  );
});

// Search products
app.get("/api/search/:name", (req, res) => {
  const searchTerm = `%${req.params.name}%`;

  db.all(
    PRODUCT_QUERY + " WHERE p.name LIKE ?",
    [searchTerm],
    (err, rows) => {
      if (err) {
        return res.status(500).json({
          error: err.message
        });
      }

      res.json(rows);
    }
  );
});

// Order lookup: items + where to pick them
app.get("/api/orders/:orderNumber", (req, res) => {
  const sql = `
    SELECT o.order_number, o.status,
           p.name, oi.quantity AS qty,
           l.warehouse, l."row" AS row, l.bin
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.id
    JOIN products p ON p.id = oi.product_id
    LEFT JOIN inventory i ON i.id = (SELECT MIN(id) FROM inventory WHERE product_id = p.id)
    LEFT JOIN locations l ON l.id = i.location_id
    WHERE o.order_number = ? COLLATE NOCASE
    ORDER BY l.bin
  `;

  db.all(sql, [req.params.orderNumber], (err, rows) => {
    if (err) return res.status(500).json({ error: err.message });
    if (rows.length === 0) return res.status(404).json({ message: "Order not found" });

    res.json({
      order_number: rows[0].order_number,
      status: rows[0].status,
      route: rows.map((r) => r.bin).join(" → "),
      items: rows.map(({ name, qty, warehouse, row, bin }) => ({ name, qty, warehouse, row, bin })),
    });
  });
});

// Status Check
app.get("/api/status", (req, res) => {
  res.json({
    status: "Running",
    service: "Warehouse Backend",
    database: "Connected"
  });
});

// Serve React build (must be AFTER all /api routes)
app.use(express.static(path.join(__dirname, "dist")));
app.get(/.*/, (req, res) => {
  res.sendFile(path.join(__dirname, "dist", "index.html"));
});

const PORT = process.env.PORT || 5000;

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
