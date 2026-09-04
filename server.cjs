const express = require("express");
const cors = require("cors");
const sqlite3 = require("sqlite3").verbose();
const path = require("path");

const app = express();
app.get("/test", (req, res) => {
  res.send("TEST WORKS");
});
app.use(cors());
app.use(express.json());

/* =========================
   DATABASE CONNECTION
========================= */

const dbPath = path.join(
  __dirname,
  "database",
  "inventory.db"
);

const db = new sqlite3.Database(dbPath, (err) => {
  if (err) {
    console.error(
      "Database connection failed:",
      err.message
    );
  } else {
    console.log(
      "Connected to SQLite Database"
    );
  }
});

/* =========================
   TEST ROUTE
========================= */

app.get("/test", (req, res) => {
  res.send("TEST ROUTE WORKING");
});

/* =========================
   HOME ROUTE
========================= */

app.get("/", (req, res) => {
  res.send("Warehouse Backend Running");
});

/* =========================
   GET ALL PRODUCTS
========================= */

app.get("/api/products", (req, res) => {
  db.all(
    "SELECT * FROM products",
    [],
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

/* =========================
   GET PRODUCT BY ID
========================= */

app.get("/api/products/:id", (req, res) => {
  db.get(
    "SELECT * FROM products WHERE id = ?",
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

/* =========================
   SEARCH PRODUCT BY NAME
========================= */

console.log("SEARCH ROUTE LOADED");

app.get("/api/search/:name", (req, res) => {
  const searchTerm = `%${req.params.name}%`;

  db.all(
    "SELECT * FROM products WHERE name LIKE ?",
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

/* =========================
   STATUS ROUTE
========================= */

app.get("/api/status", (req, res) => {
  res.json({
    status: "Running",
    service: "Warehouse Backend",
    database: "Connected"
  });
});

/* =========================
   SERVER START
========================= */

const PORT = 5000;

app.listen(PORT, "0.0.0.0", () => {
  console.log(`Server running on port ${PORT}`);
});

