import React, { useEffect, useState } from "react";
import axios from "axios";

function Profile() {
    const [user, setUser] = useState(null);
    const [editMode, setEditMode] = useState(false);
    const [editForm, setEditForm] = useState({
        username: "",
        email: "",
        phone: "",
    });

    // Automatically send HttpOnly cookies
    axios.defaults.withCredentials = true;

    // Fetch logged-in user
    const fetchUser = () => {
        axios
            .get("http://127.0.0.1:8000/api/profile/")
            .then((res) => {
                if (res.data && res.data.length > 0) {
                    setUser(res.data[0]);
                }
            })
            .catch((err) => console.log("Profile Fetch Error:", err));
    };

    useEffect(() => {
        fetchUser();
    }, []);

    // Handle input changes
    const handleChange = (e) => {
        setEditForm({ ...editForm, [e.target.name]: e.target.value });
    };

    // Save updated profile info
    const handleSave = () => {
        axios
            .patch("http://127.0.0.1:8000/api/profile/", editForm)
            .then((res) => {
                alert("Profile updated!");
                setUser(res.data);
                setEditMode(false);
            })
            .catch((err) => console.log("Update Error:", err));
    };

    // Delete account
    const handleDelete = () => {
        if (!window.confirm("Delete account?")) return;

        axios
            .delete("http://127.0.0.1:8000/api/profile/")
            .then(() => {
                alert("Account deleted!");
                window.location.href = "/";
            })
            .catch((err) => console.log("Delete Error:", err));
    };

    // Upload profile image
    const handleImageUpload = (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append("profile_image", file);

        axios
            .patch("http://127.0.0.1:8000/api/profile/", formData)
            .then(() => {
                alert("Image uploaded!");
                fetchUser();
            })
            .catch((err) => console.log("Image Upload Error:", err));
    };

    if (!user) return <div>Loading...</div>;

    return (
        <div style={{ padding: "40px", position: "relative", minHeight: "400px" }}>

            {/* Upload Image Button (top-right) */}
            <div style={{ position: "absolute", top: "10px", right: "10px" }}>
                <label
                    style={{
                        background: "blue",
                        color: "white",
                        padding: "8px 15px",
                        borderRadius: "5px",
                        cursor: "pointer",
                    }}
                >
                    Upload Image
                    <input
                        type="file"
                        onChange={handleImageUpload}
                        style={{ display: "none" }}
                    />
                </label>
            </div>

            <h2>My Profile</h2>

            {/* Profile Picture */}
            {user.profile_image && (
                <img
                    src={`http://127.0.0.1:8000${user.profile_image}`}
                    alt="profile"
                    width="130"
                    height="130"
                    style={{
                        borderRadius: "50%",
                        objectFit: "cover",
                        border: "3px solid #d6b288ff"
                    }}
                />
            )}

            {/* Profile Card */}
            <div
                style={{
                    marginTop: "30px",
                    maxWidth: "500px",
                    padding: "25px",
                    borderRadius: "10px",
                    boxShadow: "2px 2px 2px 2px rgba(0,0,0,0.1)",
                    backgroundColor: "#fff"
                }}
            >

                {/* Username */}
                <div style={{ marginBottom: "15px" }}>
                    <strong>Username:</strong><br />
                    {editMode ? (
                        <input
                            name="username"
                            value={editForm.username}
                            onChange={handleChange}
                            style={{ width: "100%", padding: "8px" }}
                        />
                    ) : (
                        <span>{user.username}</span>
                    )}
                </div>

                {/* Email */}
                <div style={{ marginBottom: "15px" }}>
                    <strong>Email:</strong><br />
                    {editMode ? (
                        <input
                            name="email"
                            value={editForm.email}
                            onChange={handleChange}
                            style={{ width: "100%", padding: "8px" }}
                        />
                    ) : (
                        <span>{user.email}</span>
                    )}
                </div>

                {/* Phone */}
                <div style={{ marginBottom: "20px" }}>
                    <strong>Phone:</strong><br />
                    {editMode ? (
                        <input
                            name="phone"
                            value={editForm.phone}
                            onChange={handleChange}
                            style={{ width: "100%", padding: "8px" }}
                        />
                    ) : (
                        <span>{user.phone}</span>
                    )}
                </div>

                {/* Buttons */}
                {editMode ? (
                    <>
                        <button
                            onClick={handleSave}
                            style={{
                                background: "green",
                                color: "white",
                                padding: "8px 20px",
                                border: "none",
                                borderRadius: "5px",
                                marginRight: "10px",
                                cursor: "pointer"
                            }}
                        >
                            Save
                        </button>

                        <button
                            onClick={() => setEditMode(false)}
                            style={{
                                padding: "8px 20px",
                                borderRadius: "5px",
                                cursor: "pointer"
                            }}
                        >
                            Cancel
                        </button>
                    </>
                ) : (
                    <>
                        <button
                            onClick={() => {
                                setEditMode(true);
                                setEditForm({
                                    username: user.username,
                                    email: user.email,
                                    phone: user.phone,
                                });
                            }}
                            style={{
                                background: "blue",
                                color: "white",
                                padding: "8px 20px",
                                border: "none",
                                borderRadius: "5px",
                                marginRight: "10px",
                                cursor: "pointer"
                            }}
                        >
                            Update
                        </button>

                        <button
                            onClick={handleDelete}
                            style={{
                                background: "red",
                                color: "white",
                                padding: "8px 20px",
                                border: "none",
                                borderRadius: "5px",
                                cursor: "pointer"
                            }}
                        >
                            Delete
                        </button>
                    </>
                )}

            </div>

        </div>
    );
}

export default Profile;
