import React, { useState, useEffect } from "react";
import "./Dashboard.css";
import ChatPage from "./ChatPage";
import { useNavigate } from "react-router-dom";
import Users from "./Users";
import Profile from "./Profile";
import Product from "./Product";
import Knowledge_Base from "./Knowledge_Base";
import EmailAutomation from "./EmailAutomation";

const Dashboard = () => {
  const [view, setView] = useState("home");
  const [showDropdown, setShowDropdown] = useState(false);
  const [loading, setLoading] = useState(true);
  const [role, setRole] = useState(null);

  const navigate = useNavigate();
  const canViewUsers = role === "SuperAdmin" || role === "Admin";
  const canUseAdminTools = role === "SuperAdmin" || role === "Admin";

  // ---------------------------------------------------------
  // AUTH CHECK USING BACKEND (Correct way with HttpOnly cookies)
  // ---------------------------------------------------------
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const res = await fetch("http://127.0.0.1:8000/api/auth-check/", {
          method: "GET",
          credentials: "include"
        });

        const data = await res.json();

        if (!data.authenticated) {
          navigate("/");
          return;
        }

        setRole(data.role);
        setLoading(false);

      } catch (error) {
        navigate("/");
      }
    };

    checkAuth();
  }, [navigate]);
  
  // ---------------------------------------------------------
  // LOGOUT FUNCTION (Backend deletion of HttpOnly cookies)
  // ---------------------------------------------------------
  const logout = async () => {
    try {
      await fetch("http://127.0.0.1:8000/api/logout/", {
        method: "POST",
        credentials: "include",
      });

      navigate("/");
    } catch (error) {
      console.error("Logout Error:", error);
      navigate("/");
    }
  };

  // ---------------------------------------------------------
  // Show loading screen while authentication is checked
  // ---------------------------------------------------------
  if (loading) {
    return (
      <div style={{ textAlign: "center", paddingTop: "40px" }}>
        <h2>Loading Dashboard...</h2>
      </div>
    );
  }

  // ---------------------------------------------------------
  // UI Rendering
  // ---------------------------------------------------------
  return (
    <div className="dashboard-container">
      {/* Navbar */}
      <div className="navbar">
        <div className="navbar-title">My Dashboard</div>

        <div className="menu" onClick={() => setShowDropdown(!showDropdown)}>
          Account ▼
          {showDropdown && (
            <div className="dropdown">
              <div
                className="dropdown-item"
                onClick={() => setView("profile")}
              >
                Profile
              </div>

              <div className="dropdown-item" onClick={logout}>
                Logout
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Main Content */}
      <div className="main-section">
        {/* Sidebar */}
        <div className="sidebar">
          <h3 style={{ textAlign: "center" }}>Dashboard Menu</h3>

          <button
            onClick={() => setView("home")}
            style={view === "home" ? activeBtnStyle : btnStyle}
          >
            Dashboard
          </button>

          {canUseAdminTools && (
            <button
              onClick={() => setView("chat")}
              style={view === "chat" ? activeBtnStyle : btnStyle}
            >
              Chats
            </button>
          )}

          {canUseAdminTools && (
            <button
              onClick={() => setView("knowledge-base")}
              style={view === "knowledge-base" ? activeBtnStyle : btnStyle}
            >
              Knowledge Base
            </button>
          )}

          <button
            onClick={() => setView("email-automation")}
            style={view === "email-automation" ? activeBtnStyle : btnStyle}
          >
            Email Automation
          </button>

          {canViewUsers && (
            <button
              onClick={() => setView("users")}
              style={view === "users" ? activeBtnStyle : btnStyle}
            >
              Users
            </button>
          )}

          <button
            onClick={() => setView("products")}
            style={view === "products" ? activeBtnStyle : btnStyle}
          >
            Products
          </button>

          <button
            onClick={() => setView("profile")}
            style={view === "profile" ? activeBtnStyle : btnStyle}
          >
            Profile
          </button>

          <button style={btnStyle} onClick={logout}>
            Logout
          </button>
        </div>

        {/* Right Content Area */}
        <div className="content">
          {view === "home" && (
            <div>
              <h1>Welcome to Dashboard</h1>
              <hr />
              <p>This is your dashboard summary.</p>
            </div>
          )}

          {view === "chat" && canUseAdminTools && <ChatPage />}
          {view === "users" && canViewUsers && <Users currentRole={role} />}
          {view === "profile" && <Profile />}
          {view === "products" && <Product />}
          {view === "knowledge-base" && canUseAdminTools && <Knowledge_Base />}
          {view === "email-automation" && <EmailAutomation />}
        </div>
      </div>
    </div>
  );
};

// Button Styles
const btnStyle = {
  height: "40px",
  backgroundColor: "blue",
  color: "white",
  cursor: "pointer",
  borderRadius: "6px",
  border: "none",
  transition: "0.3s",
};

const activeBtnStyle = {
  ...btnStyle,
  backgroundColor: "#00d1b2",
  fontWeight: "bold",
};

export default Dashboard;
