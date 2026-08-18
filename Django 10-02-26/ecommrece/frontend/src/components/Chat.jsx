import React, { useEffect, useRef, useState } from 'react';
import './Chat.css';

const API_BASE = 'http://127.0.0.1:8000';
const CHAT_EMAIL_KEY = 'chatUserEmail';
const DEFAULT_EMAIL = 'guest@ecommrece.local';

const buildFallbackMessage = (text, sender) => ({
  id: `${sender}-${Date.now()}-${Math.random().toString(16).slice(2)}`,
  sender,
  text,
});

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const messagesEndRef = useRef(null);
  const emailRef = useRef(
    localStorage.getItem(CHAT_EMAIL_KEY) || DEFAULT_EMAIL
  );

  useEffect(() => {
    localStorage.setItem(CHAT_EMAIL_KEY, emailRef.current);
  }, []);

  useEffect(() => {
    const loadHistory = async () => {
      setLoading(true);
      setError('');

      try {
        const res = await fetch(
          `${API_BASE}/chat/?email=${encodeURIComponent(emailRef.current)}`
        );

        if (!res.ok) {
          throw new Error('Failed to load chat history');
        }

        const data = await res.json();
        const history = data.messages?.length
          ? data.messages
          : [
              {
                id: 'welcome',
                sender: 'agent',
                text: 'Hi, I am your support agent. Ask me about products, orders, payment, or account details.',
              },
            ];

        setMessages(history);
      } catch (err) {
        setMessages([
          {
            id: 'welcome',
            sender: 'agent',
            text: 'Hi, I am your support agent. Ask me about products, orders, payment, or account details.',
          },
        ]);
        setError(err.message || 'Unable to connect to the chat service');
      } finally {
        setLoading(false);
      }
    };

    loadHistory();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    const text = input.trim();

    if (!text) return;

    setInput('');
    setError('');
    setMessages((prev) => [...prev, buildFallbackMessage(text, 'user')]);

    try {
      const res = await fetch(`${API_BASE}/chat/message/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: emailRef.current,
          message: text,
        }),
      });

      if (!res.ok) {
        throw new Error('Failed to send message');
      }

      const data = await res.json();

      setMessages((prev) => [
        ...prev,
        {
          id: `agent-${data.id}`,
          sender: 'agent',
          text: data.response,
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: `agent-error-${Date.now()}`,
          sender: 'agent',
          text: 'I could not reach the database-backed agent right now. Please try again.',
        },
      ]);
      setError(err.message || 'Failed to send message');
    }
  };

  return (
    <div className="chat-page">
      <header className="chat-hero">
        <div>
          <p className="chat-eyebrow">Database-backed agent</p>
          <h1>Ask anything and the agent checks the database every time.</h1>
        </div>
        <div className="chat-meta">
          <span>Auto-corrects spelling</span>
          <span>Uses live DB context</span>
        </div>
      </header>

      <main className="chat-shell">
        <div className="chat-feed">
          {loading && <div className="chat-status">Loading conversation...</div>}
          {error && <div className="chat-status error">{error}</div>}
          {messages.map((message) => (
            <div
              key={message.id}
              className={`chat-message ${message.sender === 'user' ? 'user' : 'agent'}`}
            >
              {message.text}
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        <form className="chat-form" onSubmit={handleSend}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about products, orders, payment, or account details..."
          />
          <button type="submit">Send</button>
        </form>
      </main>
    </div>
  );
};

export default Chat;
