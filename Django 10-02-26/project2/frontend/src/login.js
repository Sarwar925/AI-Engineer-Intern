import React, { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";


function Login() {
  const [data, setData] = useState({ username: "", password: "" });

  const handleChange = (e) => {
    setData({ ...data, [e.target.name]: e.target.value });
  };
  const navigate = useNavigate();

  const loginUser = async () => {
  try {
    const res = await axios.post("http://127.0.0.1:8000/api/login/", data);

    // Save token
    localStorage.setItem("token", res.data.access);

    // alert("Login Successful");

    // Redirect to Home/Dashboard
    navigate("/home");

  } catch {
    alert("Invalid Credentials");
  }
};


  return (
    <div>
      <h2>Login</h2>
      <input name="username" placeholder="Username" onChange={handleChange} />
      <br />
      <input name="password" type="password" placeholder="Password" onChange={handleChange} />
      <br />
      <button onClick={loginUser}>Login</button>
    </div>
  );
}

export default Login;
