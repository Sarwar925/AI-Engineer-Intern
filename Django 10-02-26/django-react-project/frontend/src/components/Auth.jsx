import React, { useState } from "react";
import { loginUser, signupUser } from "../api";

export default function Auth({ setIsLoggedIn, setAuthInfo }) {
  const [authPage, setAuthPage] = useState("login");
  const [form, setForm] = useState({ username: "", email: "", phone: "", password: "" });

  const handleLogin = async () => {
    try {
      const res = await loginUser({ username: form.username, password: form.password });
      if (res.data.msg === "Login success") {
        setIsLoggedIn(true);
        setAuthInfo({ username: form.username, email: form.email, phone: form.phone });
      }
    } catch (err) { alert("Login failed"); }
  };

  const handleSignup = async () => {
    try {
      await signupUser(form);
      alert("Signup success. Please login.");
      setAuthPage("login");
    } catch (err) { alert("Signup failed"); }
  };

  return (
    <div className="center">
      <h2>{authPage}</h2>
      <input placeholder="Username" onChange={(e) => setForm({ ...form, username: e.target.value })} />
      {authPage === "signup" && <>
        <input placeholder="Email" onChange={(e) => setForm({ ...form, email: e.target.value })} />
        <input placeholder="Phone" onChange={(e) => setForm({ ...form, phone: e.target.value })} />
      </>}
      <input type="password" placeholder="Password" onChange={(e) => setForm({ ...form, password: e.target.value })} />
      {authPage === "login" ? (
        <><button onClick={handleLogin}>Login</button>
          <p>Don't have account? <button onClick={() => setAuthPage("signup")}>Signup</button></p>
        </>
      ) : (
        <><button onClick={handleSignup}>Signup</button>
          <p>Already have account? <button onClick={() => setAuthPage("login")}>Login</button></p>
        </>
      )}
    </div>
  );
}
