// Login.jsx
import React, { useState } from "react";
import './Login.css';  // Create this file or reuse Signup.css

function Login() {
  const [formData, setFormData] = useState({
    email: "",          // or username/phone — change based on your backend
    password: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
    setError(""); // Clear error when user types
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:8000/api/login/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (response.ok) {
        // Success - usually backend returns token or user info
        alert("Login successful!");

        // Most common patterns - choose one:
        // 1. Save JWT/token to localStorage (for token-based auth)
        if (data.access) {
          localStorage.setItem("access_token", data.access);
          // localStorage.setItem("refresh_token", data.refresh); // if using refresh tokens
        }

        // 2. Redirect to dashboard/home
        // window.location.href = "/dashboard";    // simple redirect
        // or if using react-router: navigate("/dashboard")

      } else {
        // Show backend error (e.g. "Invalid credentials", "User not found")
        setError(
          data.detail ||
          data.non_field_errors?.[0] ||
          data.email?.[0] ||
          data.password?.[0] ||
          "Login failed. Please check your credentials."
        );
      }
    } catch (err) {
      setError("Network error. Is the server running?");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <h2>Login</h2>

      <form onSubmit={handleLogin} className="login-form">
        {error && <p className="error-message">{error}</p>}

        <input
          type="email"
          name="email"
          placeholder="Email"
          value={formData.email}
          onChange={handleChange}
          required
          disabled={loading}
        />

        <input
          type="password"
          name="password"
          placeholder="Password"
          value={formData.password}
          onChange={handleChange}
          required
          disabled={loading}
        />

        <button type="submit" disabled={loading}>
          {loading ? "Logging in..." : "Login"}
        </button>

        <p className="signup-link">
          Don't have an account? <a href="/signup">Sign Up</a>
        </p>
      </form>
    </div>
  );
}

export default Login;