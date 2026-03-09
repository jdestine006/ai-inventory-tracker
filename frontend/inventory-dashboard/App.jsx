import { useEffect, useState } from "react";
import { ImEmbed } from "react-icons/im";

const API_BASE = "https://2jxjz2zjj8.execute-api.us-east-1.amazonaws.com/dev";

function App() {
  const [items, setItems] = useState([]);
  const [name, setName] = useState("");
  const [category, setCategory] = useState("");
  const [quantity, setQuantity] = useState("");
  const [reorderThreshold, setReorderThreshold] = useState("");

  const [summary, setSummary] = useState("");
  const [summaryLoading, setSummaryLoading] = useState(false);

  async function loadItems() {
    const res = await fetch(`${API_BASE}/items`);
    const data = await res.json();
    setItems(data.items || []);
  }

  useEffect(() => {
    loadItems();
  }, []);

  async function addItem(e) {
    e.preventDefault();

    await fetch(`${API_BASE}/items`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        name,
        category,
        quantity: Number(quantity),
        reorderThreshold: Number(reorderThreshold)
      })
    });

    setName("");
    setCategory("");
    setQuantity("");
    setReorderThreshold("");

    loadItems();
  }

  async function deleteItem(itemId) {
    await fetch(`${API_BASE}/items/${itemId}`, {
      method: "DELETE",
    });
    
    loadItems();
  }

  async function updateItem(itemId, updatedFields) {
    await fetch(`${API_BASE}/items/${itemId}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(updatedFields),
    });
    
    loadItems();
  }

  async function generateSummary() {
  setSummaryLoading(true);
  setSummary("");

  try {
    const res = await fetch(`${API_BASE}/inventory-summary`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    });

    const text = await res.text();
    console.log("inventory-summary status:", res.status);
    console.log("inventory-summary body:", text);

    if (!res.ok) {
      setSummary(`Summary failed: ${text}`);
      return;
    }

    const data = JSON.parse(text);
    setSummary(data.summary || "No summary returned.");
  } catch (error) {
    console.error(error);
    setSummary(`Failed to generate inventory summary: ${error.message}`);
  } finally {
    setSummaryLoading(false);
  }
}

  return (
    <div style={{ maxWidth: 800, margin: "40px auto", fontFamily: "Arial" }}>
      <h1>Inventory Dashboard</h1>

      <form onSubmit={addItem} style={{ marginBottom: 30 }}>
        <input
          placeholder="Item Name"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />

        <input
          placeholder="Category"
          value={category}
          onChange={(e) => setCategory(e.target.value)}
        />

        <input
          placeholder="Quantity"
          type="number"
          value={quantity}
          onChange={(e) => setQuantity(e.target.value)}
        />

        <input
          placeholder="Reorder Threshold"
          type="number"
          value={reorderThreshold}
          onChange={(e) => setReorderThreshold(e.target.value)}
        />

        <button>Add Item</button>
      </form>

      <div style ={{ marginBottom: "20px", justifyContent: "center", display: "flex", flexDirection: "column", alignItems: "center" }}>
      <button onClick={generateSummary}>
        {summaryLoading ? "Generating Summary..." : "Generate Inventory Summary"}
        </button>
        {summary && (
          <div style={{
            marginBottom: "20px",
            padding: "15px",
            border: "1px solid #ddd",
            borderRadius: "8px",
            backgroundColor: "#fafafa",
            textAlign: "left",
            whiteSpace: "pre-wrap",
          }}
          >
            <h3> AI Inventory Summary:</h3>
            <p>{summary}</p>
          </div>
        )}
      <table width="100%" border="1" cellPadding="10">
        <thead>
          <tr>
            <th>Item</th>
            <th>Category</th>
            <th>Quantity</th>
            <th>Status</th>
            <th>Last Updated</th>
            <th>Actions</th>
          </tr>
        </thead>

        <tbody>
          {items.map((item) => (
            <tr key={item.itemId} className={item.quantity <= item.reorderThreshold ? "low-stock" : ""}>
              <td>{item.name}</td>
              <td>{item.category}</td>
              <td>{item.quantity}</td>
              <td>
                {item.quantity <= item.reorderThreshold ? "⚠ Low Stock" : "OK"}
              </td>
              <td>{new Date(item.lastUpdated).toLocaleString()}</td>
              <td>
                <button onClick={() => updateItem(item.itemId, {
                  quantity: item.quantity + 1})}>+1</button>
                <button onClick={() => item.quantity > 0 && updateItem(item.itemId, {
                  quantity: item.quantity - 1})}>-1</button>
                <button onClick={() => deleteItem(item.itemId)}>Delete</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      </div>
    </div>
  );
}

export default App;