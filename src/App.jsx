

import { useEffect, useState } from "react";
import "./App.css";

// Backend API
const API_URL = "http://localhost:5000/api";
  import.meta.env.VITE_API_URL || "http://172.25.162.142:5000/api";

function App() {
  const [products, setProducts] = useState([]);
  const [darkMode, setDarkMode] = useState(false);
  const [search, setSearch] = useState("");
  const [searchResult, setSearchResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Load products from backend
  useEffect(() => {
    setLoading(true);
    setError("");

    fetch(`${API_URL}/products`)
      .then((response) => {
        if (!response.ok) {
          throw new Error("Failed to load products");
        }

        return response.json();
      })
      .then((data) => {
        setProducts(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Backend error:", err);

        setError(
          "Unable to connect to backend. Make sure the backend is running."
        );

        setLoading(false);
      });
  }, []);

  // Search product
  const handleProductSearch = () => {
    if (!search.trim()) {
      setSearchResult(null);
      return;
    }

    setLoading(true);
    setError("");

    const value = search.toLowerCase().trim();

    const result = products.find(
      (product) =>
        product.name?.toLowerCase().includes(value) ||
        String(product.id).includes(value)
    );

    setSearchResult(result || "not-found");
    setLoading(false);
  };

  return (
    <div className={`app ${darkMode ? "dark" : ""}`}>

      {/* ================= HEADER ================= */}
      <header className="header">

        <div className="brand">
          🇮🇳 <span>StockSetu</span>
        </div>

        <nav>
          <a href="#dashboard">Dashboard</a>
          <a href="#search">Product Search</a>
          <a href="#orders">Orders</a>
        </nav>
        <button
  className="theme-toggle"
  onClick={() => setDarkMode(!darkMode)}
>
  {darkMode ? "☀️ Light" : "🌙 Dark"}
</button>

      </header>


      {/* ================= HERO ================= */}
      <section className="hero" id="dashboard">

        <div>

          <p className="tagline">
            भारत का स्मार्ट इन्वेंटरी सिस्टम 🇮🇳
          </p>

          <h1>
            Multi-Warehouse
            <br />
            <span>Inventory Tracking</span>
          </h1>

          <p className="subtitle">
            <button className="hero-btn">
  Explore Inventory →
</button>
           India's Smart Warehouse Inventory Platform.
Track inventory, locate products, and optimize warehouse operations.
          </p>

        </div>


        <div className="hero-card">

          <div className="india-icon">
            📦
          </div>

          <h3>
            StockSetu
          </h3>

          <p>
            Connecting every stock to the right location.
          </p>

        </div>

      </section>
      <section className="section">

  <div className="stats">

    <div className="stat-card">
      <h3>10</h3>
      <p>Products</p>
    </div>

    <div className="stat-card">
      <h3>3</h3>
      <p>Warehouses</p>
    </div>

    <div className="stat-card">
      <h3>125</h3>
      <p>Orders Processed</p>
    </div>

    <div className="stat-card">
      <h3>99%</h3>
      <p>Accuracy</p>
    </div>

  </div>

</section>


      {/* ================= PRODUCT SEARCH ================= */}
      <section className="section" id="search">

        <div className="section-title">

          <span>
            🔎
          </span>

          <div>

            <h2>
              Product Search
            </h2>

            <p>
              Search products from the live inventory database
            </p>

          </div>

        </div>


        {/* SEARCH BAR */}
        <div className="search-box">

          <input
            type="text"
            placeholder="Search e.g. Wireless Mouse"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                handleProductSearch();
              }
            }}
          />

          <button onClick={handleProductSearch}>
            Search
          </button>

        </div>


        {/* BACKEND ERROR */}
        {error && (
          <div className="error">

            {error}

            <br />

            <small>
              Backend: {API_URL}
            </small>

          </div>
        )}


        {/* LOADING */}
        {loading && (
          <div className="loading">
            Loading inventory...
          </div>
        )}


        {/* PRODUCT NOT FOUND */}
        {searchResult === "not-found" && (
          <div className="error">
            Product not found.
          </div>
        )}


        {/* PRODUCT RESULT */}
        {searchResult && searchResult !== "not-found" && (

          <div className="product-card">

            <div>

              <h3>
                {searchResult.name}
              </h3>

              <p>
                Product ID: {searchResult.id}
              </p>

            </div>


            <div className="location-grid">

              <div>
                <small>🏢 Warehouse</small>

                <strong>
                  {searchResult.warehouse}
                </strong>
              </div>


              <div>
                <small>📍 Row</small>

                <strong>
                  {searchResult.row}
                </strong>
              </div>


              <div>
                <small>📦 Bin</small>

                <strong>
                  {searchResult.bin}
                </strong>
              </div>


              <div>
                <small>✅ Available</small>

                <strong>
                  {searchResult.quantity}
                </strong>
              </div>

            </div>

          </div>

        )}

      </section>


      {/* ================= ORDER LOOKUP ================= */}
      <section
        className="section order-section"
        id="orders"
      >

        <div className="section-title">

          <span>
            🧾
          </span>

          <div>

            <h2>
              Order Lookup
            </h2>

            <p>
              Get the exact picking locations for every item
            </p>

          </div>

        </div>


        <div className="order-placeholder">

          <div className="placeholder-icon">
            🛒
          </div>

          <h3>
  Order Lookup
</h3>

<p>
  Enter an Order ID to find warehouse picking locations.
</p>

<div className="search-box">
  <input
    type="text"
    placeholder="Enter Order ID (e.g. ORD-1001)"
  />
  <button>
    Lookup Order
  </button>
</div>

<div style={{ marginTop: "20px" }}>
  <p><strong>Order ID:</strong> ORD-1001</p>
  <p><strong>Items:</strong> Wireless Mouse, Keyboard</p>
  <p><strong>Warehouse:</strong> WH-01</p>
  <p><strong>Picking Route:</strong> A02 → B01</p>
  <p><strong>Status:</strong> Ready for Dispatch</p>
</div>

        </div>

      </section>
<section className="section">

  <div className="section-title">
    <span>✨</span>
    <div>
      <h2>Features</h2>
    </div>
  </div>

  <div className="location-grid">

    <div>
      <strong>⚡ Real-Time Search</strong>
<p>Instant product lookup</p>
    </div>

    <div>
      <strong>🏢 Multi-Warehouse</strong>
<p>Manage multiple warehouses</p>
    </div>

    <div>
      <strong>📍 Bin Tracking</strong>
<p>Locate products precisely</p>
    </div>

    <div>
      <strong>🚚 Order Lookup</strong>
<p>Fast order fulfillment</p>
    </div>

  </div>

</section>

      {/* ================= FOOTER ================= */}
      <footer>

        <div>
          🇮🇳 <strong>StockSetu</strong>
        </div>

        <p>
          Smart Inventory • Made for India
        </p>

      </footer>

    </div>
  );
}

export default App;
