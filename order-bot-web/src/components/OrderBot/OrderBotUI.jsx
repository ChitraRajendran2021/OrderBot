import React, { useState } from "react";

export default function OrderBotUI() {
  const [query, setQuery] = useState("");
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setResponse("");

    try {
      const res = await fetch("http://localhost:5000/api/query", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query }),
      });

      const data = await res.json();
      setResponse(data.response);
    } catch (err) {
      setResponse("Error contacting the backend.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#f3f4f6",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "1rem",
      }}
    >
      <div
        style={{
          background: "#fff",
          padding: "2rem",
          borderRadius: "0.75rem",
          boxShadow: "0 4px 12px rgba(0, 0, 0, 0.1)",
          width: "100%",
          maxWidth: "400px",
          textAlign: "center",
        }}
      >
        <h1
          style={{
            fontSize: "1.75rem",
            fontWeight: "bold",
            marginBottom: "1.5rem",
          }}
        >
          SDM Order Bot
        </h1>
        <h4>Know your Order details here</h4>

        <input
          type="text"
          placeholder="Ex : What is the status of order 1000000"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
          style={{
            width: "100%",
            padding: "0.75rem",
            marginBottom: "1rem",
            border: "1px solid #ccc",
            borderRadius: "0.375rem",
          }}
        />

        <button
          onClick={handleSubmit}
          disabled={loading}
          style={{
            padding: "0.5rem 1rem",
            background: "#6366f1",
            color: "#fff",
            border: "none",
            borderRadius: "0.375rem",
            cursor: loading ? "not-allowed" : "pointer",
            marginBottom: "1rem",
          }}
        >
          {loading ? "Thinking..." : "Ask"}
        </button>

        {response && (
          <div
            style={{
              marginTop: "1rem",
              padding: "1rem",
              background: "#f9fafb",
              borderRadius: "0.375rem",
              color: "#1f2937",
              fontWeight: "500",
            }}
          >
            {response}
          </div>
        )}
      </div>
    </div>
  );
}
