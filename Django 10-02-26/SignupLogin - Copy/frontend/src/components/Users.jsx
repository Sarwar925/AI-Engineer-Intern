import { useState, useEffect } from "react";
import axios from "axios";
import { FaEye, FaEdit, FaTrash } from "react-icons/fa";
import CreateUserForm from "./create_user_form";


const Users = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showSignup, setShowSignup] = useState(false);
  const [selectUser, setSelectUser] = useState(null);
  const [showUpdateUser, setShowUpdateUser] = useState(false);
  const [showModel, setShowModel] = useState(false);
  const [showDelete, setShowDelete] = useState(false);
  const [deleteId, setDeleteId] = useState(null);
  const [showRoleModal, setShowRoleModal] = useState(false);

  const togglePopup = () => setShowSignup(!showSignup);

  // Load all users (SuperAdmin only)
  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const response = await axios.get(
          "http://127.0.0.1:8000/api/users/",
          { withCredentials: true }
        );
        setUsers(response.data);
        setLoading(false);

      } catch (err) {
        console.log(err.response);
        setError("Failed to fetch users. You must be SuperAdmin.");
        setLoading(false);
      }
    };

    fetchUsers();
  }, []);

  if (loading) return <div className="loader">Loading Database...</div>;
  if (error) return <div className="error">{error}</div>;

  // View User
  const view_user = (id) => {
    fetch(`http://127.0.0.1:8000/api/update-user/${id}/`, {
      credentials: "include",
    })
      .then((res) => res.json())
      .then((data) => {
        setSelectUser(data);
        setShowModel(true);
      });
  };

  // Update User
  const update_user = (id) => {
    fetch(`http://127.0.0.1:8000/api/update-user/${id}/`, {
      credentials: "include",
    })
      .then((res) => res.json())
      .then((data) => {
        setSelectUser(data);
        setShowUpdateUser(true);
      });
  };

  const handleChange = (e) => {
    setSelectUser({
      ...selectUser,
      [e.target.name]: e.target.value,
    });
  };

  const save_update_user = () => {
    fetch(`http://127.0.0.1:8000/api/update-user/${selectUser.id}/`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify(selectUser),
    }).then(() => {
      setShowUpdateUser(false);
      window.location.reload();
    });
  };

  // Delete User
  const delete_user = () => {
    if (selectUser && selectUser.role === "SuperAdmin") {
      alert("SuperAdmin cannot be deleted!");
      return;
    }

    fetch(`http://127.0.0.1:8000/api/delete-user/${deleteId}/`, {
      method: "DELETE",
      credentials: "include",
    })
      .then((res) => res.json())
      .then(() => {
        setUsers(users.filter((user) => user.id !== deleteId));
        setShowDelete(false);
        setDeleteId(null);
      });
  };

  const cancel_delete = () => {
    setShowDelete(false);
    setDeleteId(null);
  };

  // Save Role Change
  const save_role_change = () => {
    fetch(`http://127.0.0.1:8000/api/set-role/${selectUser.id}/`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ role: selectUser.role }),
    })
      .then((res) => res.json())
      .then(() => {
        setUsers((prev) =>
          prev.map((u) =>
            u.id === selectUser.id ? { ...u, role: selectUser.role } : u
          )
        );

        setShowRoleModal(false);
        alert("Role updated successfully!");
      });
  };

  return (
    <div style={{ padding: "20px", position: "relative" }}>
      <h2 style={{ color: "#333" }}>System Users (MySQL)</h2>
      <button onClick={togglePopup} style={btnStyle}>+ Add New User</button>

      {/* Show Signup */}
      {showSignup && (
        <div style={modalOverlayStyle} onClick={togglePopup}>
          <div style={modalContentStyle} onClick={(e) => e.stopPropagation()}>
            <button onClick={togglePopup} style={closeBtnStyle}>&times;</button>

            <CreateUserForm
              onClose={togglePopup}
              onSuccess={() => {
                setShowSignup(false);
                window.location.reload();
              }}
            />

          </div>
        </div>
      )}


      {/* USERS TABLE */}
      <table style={tableStyle}>
        <thead>
          <tr style={headerStyle}>
            <th>ID</th>
            <th>Username</th>
            <th>Email</th>
            <th>Phone</th>
            <th>Actions</th>
            <th>Role</th>
          </tr>
        </thead>

        <tbody>
          {users.map((user) => (
            <tr key={user.id} style={rowStyle}>
              <td>{user.id}</td>
              <td>{user.username}</td>
              <td>{user.email}</td>
              <td>{user.phone || "N/A"}</td>

              <td>
                <button onClick={() => view_user(user.id)} style={{iconBtn,color:'blue',backgroundColor:'white',border:'None'}}><FaEye /></button>
                <button onClick={() => update_user(user.id)} style={{iconBtn,color:'orange',backgroundColor:'white',border:'None'}}><FaEdit /></button>

                <button
                  onClick={() => {
                    setDeleteId(user.id);
                    setSelectUser(user);
                    setShowDelete(true);
                  }}
                  style={{ ...iconBtn, color: "red" }}
                >
                  <FaTrash />
                </button>
              </td>

              <td style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                <span style={{ ...roleBadgeStyle[user.role], minWidth: "90px", textAlign: "center" }}>
                  {user.role}
                </span>

                <button
                  onClick={() => {
                    setSelectUser(user);
                    setShowRoleModal(true);
                  }}
                  style={changeRoleBtn}
                >
                  Change
                </button>
              </td>


            </tr>
          ))}
        </tbody>
      </table>

      {/* Role Assignment Modal */}
      {showRoleModal && selectUser && (
        <div style={modalOverlayStyle} onClick={() => setShowRoleModal(false)}>
          <div style={modalContentStyle} onClick={(e) => e.stopPropagation()}>
            <h2>Assign Role</h2>

            <select
              name="role"
              value={selectUser.role || "User"}
              onChange={(e) =>
                setSelectUser({ ...selectUser, role: e.target.value })
              }
              style={{ width: "100%", padding: "8px", marginTop: "10px" }}
            >
              <option value="User">User</option>
              <option value="Admin">Admin</option>
              <option value="SuperAdmin">SuperAdmin</option>
            </select>

            <button
              style={{ marginTop: "15px", backgroundColor: "green", color: "white", padding: "8px 12px" }}
              onClick={save_role_change}
            >
              Save Role
            </button>

            <button
              style={{ marginLeft: "10px", padding: "8px 12px" }}
              onClick={() => setShowRoleModal(false)}
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Update User */}
      {showUpdateUser && selectUser && (
        <div style={modalOverlayStyle} onClick={() => setShowUpdateUser(false)}>
          <div style={modalContentStyle} onClick={(e) => e.stopPropagation()}>
            <h2>Update User</h2>

            <input
              name="username"
              value={selectUser.username}
              onChange={handleChange}
              placeholder="Username"
            />

            <input
              name="email"
              value={selectUser.email}
              onChange={handleChange}
              placeholder="Email"
              style={{ marginTop: "10px" }}
            />

            <input
              name="phone"
              value={selectUser.phone}
              onChange={handleChange}
              placeholder="Phone"
              style={{ marginTop: "10px" }}
            />

            <br />
            <button style={{ marginTop: "10px" }} onClick={save_update_user}>
              Save
            </button>
            <button style={{ marginLeft: "10px" }} onClick={() => setShowUpdateUser(false)}>
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* View User */}
      {showModel && selectUser && (
        <div style={modalOverlayStyle} onClick={() => setShowModel(false)}>
          <div style={modalContentStyle} onClick={(e) => e.stopPropagation()}>
            <button onClick={() => setShowModel(false)} style={closeBtnStyle}>&times;</button>
            <h2>{selectUser.username}</h2>
            <p><strong>Email:</strong> {selectUser.email}</p>
            <p><strong>Phone:</strong> {selectUser.phone || "N/A"}</p>
          </div>
        </div>
      )}

      {/* Delete Confirm */}
      {showDelete && (
        <div style={modalOverlayStyle}>
          <div style={modalContentStyle}>
            <h3>Delete User?</h3>
            <p>Are you sure?</p>

            <button style={deleteBtn} onClick={delete_user}>Yes Delete</button>
            <button style={cancelBtn} onClick={cancel_delete}>Cancel</button>
          </div>
        </div>
      )}

    </div>
  );
};

// Role badge colors
const roleBadgeStyle = {
  SuperAdmin: {
    background: "#e63946",
    color: "white",
    padding: "6px 12px",
    borderRadius: "20px",
    fontWeight: "bold",
    fontSize: "13px",
    display: "inline-block"
  },
  Admin: {
    background: "#ff9800",
    color: "white",
    padding: "6px 12px",
    borderRadius: "20px",
    fontWeight: "bold",
    fontSize: "13px",
    display: "inline-block"
  },
  User: {
    background: "#2a9d8f",
    color: "white",
    padding: "6px 12px",
    borderRadius: "20px",
    fontWeight: "bold",
    fontSize: "13px",
    display: "inline-block"
  }
};


const iconBtn = { background: "white", border: "none", cursor: "pointer", marginRight: "5px" };
const deleteBtn = { background: "red", color: "white", padding: "8px 15px", border: "none", cursor: "pointer" };
const cancelBtn = { background: "gray", color: "white", padding: "8px 15px", border: "none", cursor: "pointer" };

const modalOverlayStyle = {
  position: "fixed",
  top: 0, left: 0, right: 0, bottom: 0,
  backgroundColor: "rgba(0,0,0,0.5)",
  display: "flex",
  justifyContent: "center",
  alignItems: "center",
  zIndex: 1000,
};

const modalContentStyle = {
  backgroundColor: "white",
  padding: "20px",
  borderRadius: "8px",
  width: "300px",
  boxShadow: "0 2px 10px rgba(0,0,0,0.3)",
};

const closeBtnStyle = {
  position: "absolute",
  top: "10px",
  right: "15px",
  fontSize: "24px",
  background: "none",
  border: "none",
  cursor: "pointer",
};

const btnStyle = {
  padding: "10px 20px",
  backgroundColor: "#4A90E2",
  color: "white",
  border: "none",
  borderRadius: "5px",
  cursor: "pointer",
  fontWeight: "bold",
};

const tableStyle = {
  width: "100%",
  borderCollapse: "collapse",
  marginTop: "20px",
  boxShadow: "0 2px 10px rgba(0,0,0,0.1)",
};

const headerStyle = {
  backgroundColor: "#4A90E2",
  color: "white",
  textAlign: "left",
  padding: "10px",
};

const rowStyle = {
  borderBottom: "1px solid #ddd",
};
const changeRoleBtn = {
  backgroundColor: "#4A90E2",
  color: "white",
  border: "none",
  padding: "6px 12px",
  borderRadius: "5px",
  cursor: "pointer",
  fontSize: "12px",
  fontWeight: "bold",
  transition: "0.2s",
};



export default Users;
