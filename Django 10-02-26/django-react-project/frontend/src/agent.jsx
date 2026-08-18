// // const agentUrl = "http://127.0.0.1:8800/dev-ui/?app=main_personal_agent&session=d77aa51d-d97d-487c-91db-b2d3b0173730&userId=user";

// // export default function AgentChat() {
// //   return (
// //     <>
// //       <div className="agent-header">
// //         <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
// //           <span className="live-dot"></span>
// //           <h3 style={{ margin: 0 }}>Live AI Assistant</h3>
// //         </div>
// //         <span style={{ fontSize: '12px', color: '#64748b' }}>Secure Connection</span>
// //       </div>
// //       <div className="iframe-container">
// //         <iframe
// //           src={agentUrl}
// //           title="Personal AI Agent"
// //           className="agent-iframe"
// //           allow="microphone; camera"
// //         />
// //       </div>
// //     </>
// //   );
// // }



// import React, { useState, useRef, useEffect } from "react";

// export default function AgentChat() {
//   const [input, setInput] = useState("");
//   const [messages, setMessages] = useState([]);
//   const messagesEndRef = useRef(null);

//   // Auto-scroll
//   useEffect(() => {
//     messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
//   }, [messages]);

//   // Update bot message in real-time
//   const sendMessage = async () => {
//     const trimmedInput = input.trim();
//     if (!trimmedInput) return;

//     // Add user message
//     setMessages((prev) => [...prev, { role: "user", text: trimmedInput }]);
//     setInput("");

//     try {
//       const response = await fetch("http://127.0.0.1:8000/api/agent-chat/", {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         body: JSON.stringify({ message: trimmedInput }),
//       });

//       const data = await response.json();

//       if (data.error) {
//         setMessages((prev) => [...prev, { role: "bot", text: "Error: " + data.error }]);
//       } else {
//         setMessages((prev) => [...prev, { role: "bot", text: data.reply }]);
//       }
//     } catch (err) {
//       setMessages((prev) => [...prev, { role: "bot", text: "Error: " + err.message }]);
//     }
//   };


//   return (
//     <div
//       style={{
//         display: "flex",
//         flexDirection: "column",
//         height: "500px",
//         border: "1px solid #ddd",
//         borderRadius: "8px",
//         padding: "10px",
//         backgroundColor: "#f9fafb",
//       }}
//     >
//       {/* Chat messages */}
//       <div style={{ flex: 1, overflowY: "auto", padding: "10px" }}>
//         {messages.map((m, i) => (
//           <div
//             key={i}
//             style={{
//               textAlign: m.role === "user" ? "right" : "left",
//               margin: "5px 0",
//             }}
//           >
//             <span
//               style={{
//                 padding: "8px 12px",
//                 borderRadius: "10px",
//                 background: m.role === "user" ? "#2563eb" : "#e5e7eb",
//                 color: m.role === "user" ? "#fff" : "#000",
//                 display: "inline-block",
//                 maxWidth: "70%",
//                 whiteSpace: "pre-wrap",
//               }}
//             >
//               {m.text}
//             </span>
//           </div>
//         ))}
//         <div ref={messagesEndRef} />
//       </div>

//       {/* Input */}
//       <div style={{ display: "flex", gap: "10px", marginTop: "10px" }}>
//         <input
//           style={{ flex: 1, padding: "10px", borderRadius: "6px", border: "1px solid #ccc" }}
//           value={input}
//           onChange={(e) => setInput(e.target.value)}
//           placeholder="Ask your AI assistant..."
//           onKeyDown={(e) => e.key === "Enter" && sendMessage()}
//         />
//         <button
//           onClick={sendMessage}
//           style={{
//             padding: "10px 20px",
//             backgroundColor: "#2563eb",
//             color: "#fff",
//             border: "none",
//             borderRadius: "6px",
//             cursor: "pointer",
//           }}
//         >
//           Send
//         </button>
//       </div>
//     </div>
//   );
// }


import React, { useState, useRef, useEffect } from "react";

export default function AgentChat() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([
    { role: "bot", text: "Welcome! I'm your social assistant." }
  ]);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userText = input;
    setMessages(prev => [...prev, { role: "user", text: userText }]);
    setInput("");
    setLoading(true);

    try {
  const response = await fetch("http://127.0.0.1:8000/api/chat/", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  credentials: "include", // ✅ required for Django session auth
  body: JSON.stringify({ message: userText }),
});

      if (response.status === 401) {
        setMessages(prev => [...prev, { role: "bot", text: "❌ Session expired. Please login again." }]);
      } else {
        const data = await response.json();
        setMessages(prev => [...prev, { role: "bot", text: data.reply }]);
      }
    } catch (err) {
      setMessages(prev => [...prev, { role: "bot", text: "⚠️ Error: " + err.message }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h3 style={styles.title}>AI Assistant</h3>
        <span style={styles.status}>● Online</span>
      </div>

      <div style={styles.chatBox}>
        {messages.map((m, i) => (
          <div key={i} style={{ ...styles.messageRow, justifyContent: m.role === "user" ? "flex-end" : "flex-start" }}>
            <div style={{ 
              ...styles.bubble, 
              backgroundColor: m.role === "user" ? "#007bff" : "#ffffff",
              color: m.role === "user" ? "#fff" : "#333",
              borderRadius: m.role === "user" ? "15px 15px 2px 15px" : "15px 15px 15px 2px",
            }}>
              {m.text}
            </div>
          </div>
        ))}
        {loading && <div style={styles.loader}>Agent is typing...</div>}
        <div ref={messagesEndRef} />
      </div>

      <div style={styles.inputArea}>
        <input
          style={styles.input}
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder="Ask me anything..."
          onKeyDown={e => e.key === "Enter" && sendMessage()}
        />
        <button onClick={sendMessage} style={styles.button} disabled={loading}>
          {loading ? "..." : "Send"}
        </button>
      </div>
    </div>
  );
}

const styles = {
  container: { maxWidth: "500px", margin: "20px auto", height: "500px", display: "flex", flexDirection: "column", borderRadius: "12px", overflow: "hidden", boxShadow: "0 4px 12px rgba(0,0,0,0.1)", backgroundColor: "#f8f9fa", fontFamily: "sans-serif" },
  header: { padding: "10px 15px", backgroundColor: "#007bff", color: "white", display: "flex", justifyContent: "space-between", alignItems: "center" },
  title: { margin: 0, fontSize: "1rem" },
  status: { fontSize: "0.7rem", color: "#afffaf" },
  chatBox: { flex: 1, overflowY: "auto", padding: "15px", display: "flex", flexDirection: "column", gap: "10px" },
  messageRow: { display: "flex", width: "100%" },
  bubble: { padding: "8px 12px", maxWidth: "75%", fontSize: "0.9rem", boxShadow: "0 1px 2px rgba(0,0,0,0.1)" },
  loader: { fontSize: "0.75rem", color: "#888", fontStyle: "italic" },
  inputArea: { padding: "10px", backgroundColor: "white", display: "flex", gap: "8px", borderTop: "1px solid #ddd" },
  input: { flex: 1, padding: "10px", borderRadius: "20px", border: "1px solid #ddd", outline: "none" },
  button: { padding: "0 15px", backgroundColor: "#007bff", color: "white", border: "none", borderRadius: "20px", cursor: "pointer" }
};