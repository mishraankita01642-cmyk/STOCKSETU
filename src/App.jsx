

import { useEffect, useState } from "react";
import "./App.css";

// Backend API
const API_URL =
  import.meta.env.VITE_API_URL || "http://172.25.162.142:5000/api";

function App() {
  const [products, setProducts] = useState([]);
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
    <div className="app">

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
            Find products, warehouse locations and order pick lists instantly.
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
                <small>
                  Warehouse
                </small>

                <strong>
                  {searchResult.warehouse}
                </strong>
              </div>


              <div>
                <small>
                  Row
                </small>

                <strong>
                  {searchResult.row}
                </strong>
              </div>


              <div>
                <small>
                  Bin
                </small>

                <strong>
                  {searchResult.bin}
                </strong>
              </div>


              <div>
                <small>
                  Available
                </small>

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
            Order API coming next
          </h3>

          <p>
            The backend currently provides the Product API.
            <br />
            We will connect Order Lookup when the backend team
            provides the Order API.
          </p>

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