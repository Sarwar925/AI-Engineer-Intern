import React, { useState } from "react";

export default function Navbar({ profileImage, setPage, setIsLoggedIn }) {
  const [dropdown, setDropdown] = useState(false);

  return (
    <div className="navbar">
      {profileImage && <img src={profileImage} alt="Profile" className="profile-img" />}
      <button onClick={() => setDropdown(!dropdown)}>Profile ▼</button>
      {dropdown && <div className="dropdown">
        <button onClick={() => setPage("profile")}>Profile</button>
        <button onClick={() => setIsLoggedIn(false)}>Logout</button>
      </div>}
    </div>
  );
}
