// Working Code

import React, { useState, useEffect } from "react";

import axios from "axios";

import './App.css';

import AgentChat from "./agent";



export default function App() {

  // ------------------- STATE -------------------

  const [authPage, setAuthPage] = useState("login"); // login | signup

  const [isLoggedIn, setIsLoggedIn] = useState(false);

  const [page, setPage] = useState("dashboard");



  const [dropdown, setDropdown] = useState(false);

  const [users, setUsers] = useState([]);

  const [showModal, setShowModal] = useState(false);

  const [editMode, setEditMode] = useState(false);

  const [editId, setEditId] = useState(null);



  const [authForm, setAuthForm] = useState({

    username: "", email: "", phone: "", password: "",

  });



  const [userForm, setUserForm] = useState({

    username: "", email: "", phone: "", password: "",

  });

  const [chatStarted, setChatStarted] = useState(false);

  // YOUR AGENT URL

  // const agentUrl = "http://127.0.0.1:8800/dev-ui/?app=main_personal_agent&session=d77aa51d-d97d-487c-91db-b2d3b0173730&userId=user";



  // ------------------- AUTH FUNCTIONS -------------------

const login = async () => {
  try {
    const res = await axios.post(
      "http://127.0.0.1:8000/api/login/",
      {
        username: authForm.username,
        password: authForm.password,
      },
      {
        withCredentials: true, // ✅ tell browser to store Django session cookie
      }
    );

    console.log("Login response:", res);
    if (res.data.msg === "Login success") {
      setIsLoggedIn(true);
    } else {
      alert("Invalid login");
    }
  } catch (err) {
    console.log(err);
    alert("Login error");
  }
};





  const signup = async () => {

    try {

      await axios.post("http://127.0.0.1:8000/api/signup/", authForm);

      alert("Signup success. Please login.");

      setAuthPage("login");

    } catch (err) {

      console.log(err);

      alert("Signup error");

    }

  };



  const logout = () => {

    setIsLoggedIn(false);

    setAuthPage("login");

    setDropdown(false);

  };



  // ------------------- USER FUNCTIONS -------------------

  const fetchUsers = async () => {

    try {

      const res = await axios.get("http://127.0.0.1:8000/api/users/");

      setUsers(res.data);

    } catch (err) {

      console.log("Fetch users error:", err);

    }

  };



  const deleteUser = async (id) => {

    if (window.confirm("Are you sure you want to delete this user?")) {

      try {

        await axios.delete(`http://127.0.0.1:8000/api/delete-user/${id}/`);

        fetchUsers();

      } catch (err) {

        console.log("Delete user error:", err);

      }

    }

  };



  const submitUser = async () => {

    try {

      if (editMode) {

        await axios.put(`http://127.0.0.1:8000/api/update-user/${editId}/`, userForm);

      } else {

        await axios.post("http://127.0.0.1:8000/api/create-user/", userForm);

      }

      setShowModal(false);

      fetchUsers();

    } catch (err) {

      console.log("Submit user error:", err);

    }

  };



  // ------------------- USE EFFECT -------------------

  useEffect(() => {

    if (page === "users") fetchUsers();

  }, [page]);



  // ------------------- AUTH UI (LOGIN/SIGNUP) -------------------

  if (!isLoggedIn) {

    return (

      <div className="modal-backdrop">

        <div className="modal">

          <h2 style={{ marginBottom: '20px', textAlign: 'center' }}>

            {authPage === "login" ? "Welcome Back" : "Create Account"}

          </h2>



          <input

            placeholder="Username" type="text" required

            value={authForm.username}

            onChange={(e) => setAuthForm({ ...authForm, username: e.target.value })}

          />



          {authPage === "signup" && (

            <>

              <input

                type="email" required placeholder="Email"

                onChange={(e) => setAuthForm({ ...authForm, email: e.target.value })}

              />

              <input

                type="phone" placeholder="Phone" required

                onChange={(e) => setAuthForm({ ...authForm, phone: e.target.value })}

              />

            </>

          )}



          <input

            type="password" placeholder="Password" required

            onChange={(e) => setAuthForm({ ...authForm, password: e.target.value })}

          />



          <div style={{ textAlign: 'center' }}>

            <button style={{ width: '100%' }} onClick={authPage === "login" ? login : signup}>

              {authPage === "login" ? "Login" : "Signup"}

            </button>

            <p style={{ marginTop: '15px', fontSize: '14px' }}>

              {authPage === "login" ? "Don't have an account? " : "Already have an account? "}

              <span

                style={{ cursor: 'pointer', color: '#2563eb', fontWeight: 'bold' }}

                onClick={() => setAuthPage(authPage === "login" ? "signup" : "login")}

              >

                {authPage === "login" ? "Signup" : "Login"}

              </span>

            </p>

          </div>

        </div>

      </div>

    );

  }



  // ------------------- MAIN DASHBOARD UI -------------------

  return (

    <div className="app-wrapper">

      {/* Navbar */}

      <nav className="navbar">

        <h3>ADMIN PANEL</h3>

        <div className="dropdown">

          <button onClick={() => setDropdown(!dropdown)}>

            {authForm.username || "User"} ▼

          </button>

          {dropdown && (

            <div className="dropdown-content" style={{ display: 'block' }}>

              <button onClick={() => { setPage("profile"); setDropdown(false); }}>Profile</button>

              <button onClick={logout}>Logout</button>

            </div>

          )}

        </div>

      </nav>



      <div className="container">

        {/* Sidebar */}

        <aside className="sidebar">

          <button className={page === "dashboard" ? "active" : ""} onClick={() => setPage("dashboard")}>Dashboard</button>

          <button className={page === "chat" ? "active" : ""} onClick={() => setPage("chat")}>Chat</button>

          <button className={page === "users" ? "active" : ""} onClick={() => setPage("users")}>User Management</button>

          <button className={page === "profile" ? "active" : ""} onClick={() => setPage("profile")}>Settings</button>

        </aside>



        {/* Main Content Area */}

        <main className="main-content">



          {page === "dashboard" && (

            <div className="card">

              <h2>Welcome to the Dashboard</h2>

              <p style={{ color: '#64748b', marginTop: '10px' }}>Select an option from the sidebar to manage your application.</p>

            </div>

          )}



          {page === "profile" && (

            <div className="card">

              <h3>Account Profile</h3>

              <hr style={{ margin: '20px 0', border: '0', borderTop: '1px solid #eee' }} />

              <p><strong>Username:</strong> {authForm.username}</p>

              <p><strong>Email:</strong> {authForm.email || 'N/A'}</p>

              <p><strong>Phone:</strong> {authForm.phone || 'N/A'}</p>

            </div>

          )}



          {page === "chat" && (

            <div className="agent-wrapper card">

              {!chatStarted ? (

                // Show this if chat hasn't started

                <div style={{ textAlign: 'center', padding: '40px' }}>

                  <h3>Welcome to Chat</h3>

                  <p style={{ marginBottom: '20px', color: '#64748b' }}>

                    Connect with our Live AI Assistant to get started.

                  </p>

                  <button onClick={() => setChatStarted(true)}>

                    Start Chat

                  </button>

                </div>

              ) : (

                // Show the actual component once button is clicked

                <AgentChat />

              )}

            </div>

          )}

          {page === "users" && (

            <>

              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>

                <h2>System Users</h2>

                <button

                  onClick={() => {

                    setEditMode(false);

                    setUserForm({ username: "", email: "", phone: "", password: "" });

                    setShowModal(true);

                  }}

                >

                  + Add New User

                </button>

              </div>



              <div className="table-container">

                <table>

                  <thead>

                    <tr>

                      <th>Username</th>

                      <th>Email</th>

                      <th>Phone</th>

                      <th>Actions</th>

                    </tr>

                  </thead>

                  <tbody>

                    {users.map((u) => (

                      <tr key={u.id}>

                        <td style={{ fontWeight: '500' }}>{u.username}</td>

                        <td>{u.email}</td>

                        <td>{u.phone}</td>

                        <td>

                          <button

                            style={{ background: '#f1f5f9', color: '#1e293b', marginRight: '8px', padding: '6px 12px' }}

                            onClick={() => {

                              setEditMode(true);

                              setEditId(u.id);

                              setUserForm({

                                username: u.username, email: u.email, phone: u.phone, password: "",

                              });

                              setShowModal(true);

                            }}

                          >

                            <span><img src="./edit-button-svgrepo-com.svg" alt="" style={{ height: 15 }}/></span>

                          </button>

                          <button

                            style={{ background: '#f1f5f9', color: '#1e293b', padding: '6px 12px' }}

                            onClick={() => deleteUser(u.id)}

                          >

                            <span><img src="./delete-cross-svgrepo-com.svg" alt="" style={{height:15}}/></span>

                          </button>

                        </td>

                      </tr>

                    ))}

                  </tbody>

                </table>

              </div>

            </>

          )}

        </main>

      </div>



      {/* Modal for Add/Edit User */}

      {showModal && (

        <div className="modal-backdrop">

          <div className="modal">

            <h3>{editMode ? "Update User Details" : "Register New User"}</h3>



            <input

              placeholder="Full Name" required

              value={userForm.username}

              onChange={(e) => setUserForm({ ...userForm, username: e.target.value })}

            />

            <input

              placeholder="Email Address" required

              value={userForm.email}

              onChange={(e) => setUserForm({ ...userForm, email: e.target.value })}

            />

            <input

              placeholder="Phone Number" required

              value={userForm.phone}

              onChange={(e) => setUserForm({ ...userForm, phone: e.target.value })}

            />

            <input

              type="password" required={!editMode}

              placeholder="Account Password"

              onChange={(e) => setUserForm({ ...userForm, password: e.target.value })}

            />



            <div style={{ display: 'flex', gap: '10px', marginTop: '10px' }}>

              <button style={{ flex: 2 }} onClick={submitUser}>

                {editMode ? "Save Changes" : "Create User"}

              </button>

              <button style={{ flex: 1, background: '#64748b' }} onClick={() => setShowModal(false)}>

                Cancel

              </button>

            </div>

          </div>

        </div>

      )}

    </div>

  );

}