import { useState } from "react";

const API_URL = import.meta.env.VITE_API_URL || "/api/chat/";

function makeWelcomeMessage() {
  return "Ask about products in WooCommerce and I’ll fetch the matching items from Django + Google ADK.";
}

export default function App() {
  const [messages, setMessages] = useState([
    { role: "assistant", text: makeWelcomeMessage() },
  ]);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    const trimmed = message.trim();
    if (!trimmed || loading) {
      return;
    }

    setMessages((current) => [...current, { role: "user", text: trimmed }]);
    setMessage("");
    setLoading(true);

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: trimmed }),
      });

      const contentType = response.headers.get("content-type") || "";
      const data = contentType.includes("application/json")
        ? await response.json()
        : { error: await response.text() };
      if (!response.ok) {
        throw new Error(
          data.error || `Request failed with status ${response.status}.`,
        );
      }

      setMessages((current) => [
        ...current,
        { role: "assistant", text: data.reply || "No reply returned." },
      ]);
    } catch (error) {
      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          text: error.message || "Something went wrong.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="shell">
      <section className="hero">
        <p className="eyebrow">WooCommerce store assistant</p>
        <h1>WooCommerce Chat Assistant</h1>
        <p className="lead">
          A React chat UI connected to a Django backend that uses Google ADK and
          WooCommerce data.
        </p>
      </section>

      <section className="chat-card">
        <div className="chat-stream" aria-live="polite">
          {messages.map((item, index) => (
            <article key={index} className={`bubble bubble--${item.role}`}>
              {item.text}
            </article>
          ))}
          {loading ? <article className="bubble bubble--assistant">Thinking...</article> : null}
        </div>

        <form className="composer" onSubmit={handleSubmit}>
          <input
            type="text"
            value={message}
            onChange={(event) => setMessage(event.target.value)}
            placeholder="Ask about available products..."
            autoComplete="off"
          />
          <button type="submit" disabled={loading}>
            {loading ? "Sending..." : "Send"}
          </button>
        </form>
      </section>
    </main>
  );
}
