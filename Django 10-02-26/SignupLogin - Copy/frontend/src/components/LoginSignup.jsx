import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Dashboard.css";

const LoginSignup = () => {
  const [isSignup, setIsSignup] = useState(true);
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    phone: "",
    password: ""
  });

  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const { name, email, phone, password } = formData;

    // ------------------------------------------------ SIGNUP
    if (isSignup) {
      try {
        const response = await fetch("http://127.0.0.1:8000/api/register/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify({
            username: name,
            email,
            phone,
            password
          }),
        });

        const data = await response.json();
        if (!response.ok) return alert(data.error || "Signup failed");

        alert("Signup Successful");
        setIsSignup(false);
      } catch (error) {
        alert("Signup failed!");
        console.error("Signup Error:", error);
      }
      return;
    }

    // ------------------------------------------------ LOGIN
    try {
      try {
        const response = await fetch("http://127.0.0.1:8000/api/login/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify({ email, password }),
        });
        const data = await response.json();
        // Check for Django auth success
        if (data.success !== true) {
          return alert(data.error || data.detail || "Login failed");
        }
        alert("Login Successful");
        // small delay helps cookie set before redirect
        setTimeout(() => navigate("/dashboard"), 300);
      } catch (error) {
        alert("Login failed!");
        console.error("Login Error:", error);
      }

    } catch (error) {
      alert("Login failed!");
      console.error("Login Error:", error);
    }
  };

  return (
    <div>
      <div className="signup">
        <div className="header">{isSignup ? "Signup" : "Login"}</div>

        <form className="inputs" onSubmit={handleSubmit}>
          {isSignup && (
            <input
              className="input"
              name="name"
              type="text"
              placeholder="Name"
              required
              onChange={handleChange}
            />
          )}

          <input
            className="input"
            name="email"
            type="email"
            placeholder="Email"
            required
            onChange={handleChange}
          />

          {isSignup && (
            <input
              className="input"
              name="phone"
              type="text"
              placeholder="Phone"
              required
              onChange={handleChange}
            />
          )}

          <input
            className="input"
            name="password"
            type="password"
            placeholder="Password"
            required
            onChange={handleChange}
          />

          <button type="submit" className="submit">
            {isSignup ? "Signup" : "Login"}
          </button>

          {isSignup ? (
            <p>
              Already have an account?{" "}
              <span
                style={{ color: "blue", cursor: "pointer" }}
                onClick={() => setIsSignup(false)}
              >
                Login
              </span>
            </p>
          ) : (
            <p>
              Don't have an account?{" "}
              <span
                style={{ color: "blue", cursor: "pointer" }}
                onClick={() => setIsSignup(true)}
              >
                Signup
              </span>
            </p>
          )}
        </form>
      </div>
    </div>
  );
};

export default LoginSignup;
