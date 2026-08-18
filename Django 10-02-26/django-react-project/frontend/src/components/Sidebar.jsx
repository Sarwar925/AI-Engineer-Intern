import React from "react";

export default function Sidebar({ setPage }) {
  return (
    <div className="sidebar">
      <button onClick={() => setPage("dashboard")}>Dashboard</button>
      <button onClick={() => setPage("users")}>Users</button>
      <button onClick={() => setPage("chat")}>Chat</button>
      <button onClick={() => setPage("profile")}>Profile</button>
    </div>
  );
}
