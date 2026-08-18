import React, { useState, useEffect } from "react";
import { fetchUsers, createUser, updateUser, deleteUser } from "../api";
import UserModal from "./UserModal";

export default function Users() {
  const [users, setUsers] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [editId, setEditId] = useState(null);
  const [userForm, setUserForm] = useState({ username: "", email: "", phone: "", password: "" });

  const loadUsers = async () => {
    const res = await fetchUsers();
    setUsers(res.data);
  };

  useEffect(() => { loadUsers(); }, []);

  const submitUser = async () => {
    if (editMode) await updateUser(editId, userForm);
    else await createUser(userForm);
    setShowModal(false);
    loadUsers();
  };

  return (
    <div>
      <h2>Users</h2>
      <button onClick={() => { setEditMode(false); setUserForm({ username: "", email: "", phone: "", password: "" }); setShowModal(true); }}>
        Add User
      </button>
      <table border="1" cellPadding="5" style={{ marginTop: 10 }}>
        <thead>
          <tr><th>Name</th><th>Email</th><th>Phone</th><th>Action</th></tr>
        </thead>
        <tbody>
          {users.map(u => (
            <tr key={u.id}>
              <td>{u.user.username}</td>
              <td>{u.user.email}</td>
              <td>{u.phone}</td>
              <td>
                <button onClick={() => { setEditMode(true); setEditId(u.user.id); setUserForm({ username: u.user.username, email: u.user.email, phone: u.phone, password: "" }); setShowModal(true); }}>Edit</button>
                <button onClick={() => deleteUser(u.user.id).then(loadUsers)}>Delete</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {showModal && <UserModal userForm={userForm} setUserForm={setUserForm} submitUser={submitUser} setShowModal={setShowModal} />}
    </div>
  );
}
