const express = require("express");
const cors = require("cors");

const app = express();

app.use(cors());
app.use(express.json());

const products = [
  {
    id: 1,
    name: "Wireless Mouse",
    warehouse: "WH-01",
    row: "A",
    bin: "A02",
    quantity: 37
  },
  {
    id: 2,
    name: "Keyboard",
    warehouse: "WH-01",
    row: "B",
    bin: "B01",
    quantity: 20
  },
  {
    id: 3,
    name: "Monitor",
    warehouse: "WH-02",
    row: "C",
    bin: "C03",
    quantity: 15
  },
  {
    id: 4,
    name: "Laptop",
    warehouse: "WH-03",
    row: "D",
    bin: "D01",
    quantity: 8
  },
  {
  id: 5,
  name: "Headphones",
  warehouse: "WH-02",
  row: "A",
  bin: "A05",
  quantity: 25
  },
  {
  id: 6,
  name: "Webcam",
  warehouse: "WH-01",
  row: "C",
  bin: "C02",
  quantity: 18
  },
  {
  id: 7,
  name: "SSD 1TB",
  warehouse: "WH-03",
  row: "B",
  bin: "B04",
  quantity: 12
  },
  {
  id: 8,
  name: "Gaming Mouse",
  warehouse: "WH-02",
  row: "D",
  bin: "D03",
  quantity: 30
  },
  {
  id: 9,
  name: "USB Keyboard",
  warehouse: "WH-01",
  row: "A",
  bin: "A01",
  quantity: 45
  },
  {
  id: 10,
  name: "Laptop Charger",
  warehouse: "WH-03",
  row: "C",
  bin: "C05",
  quantity: 22
  }
];
app.get("/", (req, res) => {
  res.send("Warehouse Backend Running");
});

app.get("/api/products", (req, res) => {
  res.json(products);
});

app.get("/api/products/:id", (req, res) => {
  const product = products.find(
    p => p.id === parseInt(req.params.id)
  );

  if (!product) {
    return res.status(404).json({
      message: "Product not found"
    });
  }

  res.json(product);
});
app.get("/api/status", (req, res) => {
  res.json({
    status: "Running",
    service: "Warehouse Backend"
  });
});
const PORT = 5000;

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
