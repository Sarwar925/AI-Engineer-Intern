import React from "react";
import { uploadProfileImage } from "../api";

export default function Profile({ authInfo, setProfileImage }) {
  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const formData = new FormData();
    formData.append("image", file);
    const res = await uploadProfileImage(formData);
    setProfileImage(res.data.image_url);
  };

  return (
    <div>
      <h3>Profile</h3>
      <p>Username: {authInfo.username}</p>
      <p>Email: {authInfo.email}</p>
      <p>Phone: {authInfo.phone}</p>
      <h4>Upload Profile Image</h4>
      <input type="file" accept="image/*" onChange={handleUpload} />
    </div>
  );
}
