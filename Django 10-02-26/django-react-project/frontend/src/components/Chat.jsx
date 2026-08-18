import React from "react";

export default function Chat() {
  return (
    <div style={{ height: "100%", display: "flex", flexDirection: "column" }}>
      <h2>Chat with Agent</h2>
      <iframe
        src="https://your-adk-agent-domain.com/webchat"
        title="ADK Chat"
        style={{ flex: 1, border: "1px solid #ccc" }}
      />
    </div>
  );
}
