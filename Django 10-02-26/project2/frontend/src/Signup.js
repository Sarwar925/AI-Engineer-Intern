import React, { useState } from "react";
import axios from "axios";

function Signup() {
  const [data, setData] = useState({ username: "", email: "", password: "" });

  const handleChange = (e) => {
    setData({ ...data, [e.target.name]: e.target.value });
  };

  const signupUser = async () => {
    try {
      await axios.post("http://127.0.0.1:8000/api/signup/", data);
      alert("Signup Successful");
    } catch {
      alert("Error in Signup");
    }
  };

  return (
    <div>
      <h2>Signup</h2>
      <input name="username" placeholder="Username" onChange={handleChange} />
      <br />
      <input name="email" placeholder="Email" onChange={handleChange} />
      <br />
      <input name="password" type="password" placeholder="Password" onChange={handleChange} />
      <br />
      <button onClick={signupUser}>Signup</button>
    </div>
  );
}

export default Signup;
