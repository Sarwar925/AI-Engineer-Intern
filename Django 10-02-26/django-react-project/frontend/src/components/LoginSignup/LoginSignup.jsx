// import React from "react";
// import { useState } from "react";
// import "./LoginSignup.css"
// const LoginSignup = () => {
//     const [action,setAction] = useState("Signup");
//     return (
//         <div className="container">
//             <div className="header">
//                 <div className="text">{action}</div>
//                 <div className="underline"></div>
//             </div>

//             <div className="inputs">
//                 {action==="Login"?<div></div>:<div className="input">
//                     <input type="text" placeholder="Name" required/>
//                 </div>}
                
//                 <div className="input">
//                     <input type="Email" placeholder="Email" required/>
//                 </div>
//                 <div className="input">
//                     <input type="password" placeholder="password" required/>
//                 </div>
//             </div>
//             {action==="Signup"?<div></div>:<div className="forgot-password">Forgot Password? <span>Click Here</span></div>}
            
//             <div className="submit-container">
//                 <div className={action==="Login"?"submit grey":"submit"} onClick={()=>{setAction("Signup")}}>Signup</div>
//                 <div className={action==="Signup"?"submit grey":"submit"}onClick={()=>{setAction("Login")}}>Login</div>
//             </div>
//         </div>
//     );
// };

// export default LoginSignup;




import React, { useState } from "react";
import "./LoginSignup.css";

const LoginSignup = () => {
  const [action, setAction] = useState("Signup");

  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
  });

  // Handle input change
  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  // Handle Signup
  const handleSignup = () => {
    if (!formData.name || !formData.email || !formData.password) {
      alert("Please fill all fields");
      return;
    }

    // Save in LocalStorage
    localStorage.setItem("user", JSON.stringify(formData));

    alert("Signup Successful");
    console.log("Saved Data:", formData);

    // Clear form
    setFormData({ name: "", email: "", password: "" });
  };

  // Handle Login
  const handleLogin = () => {
    const savedUser = JSON.parse(localStorage.getItem("user"));

    if (
      savedUser &&
      savedUser.email === formData.email &&
      savedUser.password === formData.password
    ) {
      alert("Login Successful");
    } else {
      alert("Invalid Email or Password  ");
    }
  };

  return (
    <div className="container">
      <div className="header">
        <div className="text">{action}</div>
        <div className="underline"></div>
      </div>

      <div className="inputs">
        {action === "Login" ? null : (
          <div className="input">
            <input
              type="text"
              name="name"
              placeholder="Name"
              value={formData.name}
              onChange={handleChange}
              required
            />
          </div>
        )}

        <div className="input">
          <input
            type="email"
            name="email"
            placeholder="Email"
            value={formData.email}
            onChange={handleChange}
            required
          />
        </div>

        <div className="input">
          <input
            type="password"
            name="password"
            placeholder="Password"
            value={formData.password}
            onChange={handleChange}
            required
          />
        </div>
      </div>

      {action === "Signup" ? null : (
        <div className="forgot-password">
          Forgot Password? <span>Click Here</span>
        </div>
      )}

      <div className="submit-container">
        <div
          className={action === "Login" ? "submit grey" : "submit"}
          onClick={() => {
            setAction("Signup");
            handleSignup();
          }}
        >
          Signup
        </div>

        <div
          className={action === "Signup" ? "submit grey" : "submit"}
          onClick={() => {
            setAction("Login");
            handleLogin();
          }}
        >
          Login
        </div>
      </div>
    </div>
  );
};

export default LoginSignup;


