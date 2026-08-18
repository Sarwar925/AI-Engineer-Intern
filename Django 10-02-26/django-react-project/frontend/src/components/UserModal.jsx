import React from "react";

export default function UserModal({ userForm, setUserForm, submitUser, setShowModal }) {
  return (
    <div className="modal">
      <div className="modal-box">
        <input placeholder="Name" value={userForm.username} onChange={e => setUserForm({ ...userForm, username: e.target.value })} />
        <input placeholder="Email" value={userForm.email} onChange={e => setUserForm({ ...userForm, email: e.target.value })} />
        <input placeholder="Phone" value={userForm.phone} onChange={e => setUserForm({ ...userForm, phone: e.target.value })} />
        <input type="password" placeholder="Password" onChange={e => setUserForm({ ...userForm, password: e.target.value })} />
        <button onClick={submitUser}>Submit</button>
        <button onClick={() => setShowModal(false)}>Cancel</button>
      </div>
    </div>
  );
}
