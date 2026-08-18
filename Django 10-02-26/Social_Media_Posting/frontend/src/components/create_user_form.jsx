import React, { useState } from "react";

const CreateUserForm = ({ onClose, onSuccess }) => {
    const [formData, setFormData] = useState({
        username: "",
        email: "",
        phone: "",
        password: "",
        role: "User"
    });

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value,
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError("");

        try {
            const response = await fetch("http://127.0.0.1:8000/api/register/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                credentials: "include",
                body: JSON.stringify(formData),
            });

            const data = await response.json();

            if (!response.ok) {
                setError(data.error || "Registration failed.");
                setLoading(false);
                return;
            }

            setLoading(false);
            onSuccess(); // Refresh user list
            onClose();   // Close modal

            alert("User created successfully!");

        } catch (err) {
            setError("Something went wrong.");
            setLoading(false);
        }
    };

    return (
        <div style={containerStyle}>
            <h2 style={titleStyle}>Create New User</h2>

            {error && <p style={errorStyle}>{error}</p>}

            <form onSubmit={handleSubmit}>

                {/* Username */}
                <input
                    type="text"
                    name="username"
                    placeholder="Username"
                    required
                    value={formData.username}
                    onChange={handleChange}
                    style={inputStyle}
                />

                {/* Email */}
                <input
                    type="email"
                    name="email"
                    placeholder="Email"
                    required
                    value={formData.email}
                    onChange={handleChange}
                    style={inputStyle}
                />

                {/* Phone */}
                <input
                    type="text"
                    name="phone"
                    placeholder="Phone"
                    value={formData.phone}
                    onChange={handleChange}
                    style={inputStyle}
                />

                {/* Password */}
                <input
                    type="password"
                    name="password"
                    placeholder="Password"
                    required
                    value={formData.password}
                    onChange={handleChange}
                    style={inputStyle}
                />

                {/* Role Selector */}
                <select
                    name="role"
                    value={formData.role}
                    onChange={handleChange}
                    style={selectStyle}
                >
                    <option value="User">User</option>
                    <option value="Admin">Admin</option>
                    <option value="SuperAdmin">SuperAdmin</option>
                </select>

                {/* Submit Button */}
                <button type="submit" style={submitBtnStyle} disabled={loading}>
                    {loading ? "Creating..." : "Create User"}
                </button>

                <button type="button" onClick={onClose} style={cancelBtnStyle}>
                    Cancel
                </button>

            </form>
        </div>
    );
};

export default CreateUserForm;

const containerStyle = {
    maxWidth: "380px",
    margin: "20px auto",
    padding: "18px",
    backgroundColor: "#ffffff",
    borderRadius: "8px",
    boxShadow: "0 3px 8px rgba(0,0,0,0.1)",
    fontFamily: "Arial, sans-serif"
};

const titleStyle = {
    textAlign: "center",
    marginBottom: "12px",
    fontSize: "20px",
    fontWeight: "600",
    color: "#333"
};

const inputStyle = {
    width: "100%",
    padding: "8px",
    marginBottom: "10px",
    borderRadius: "5px",
    border: "1px solid #ddd",
    fontSize: "13px",
    boxSizing: "border-box"
};

const selectStyle = {
    width: "100%",
    padding: "8px",
    marginBottom: "10px",
    borderRadius: "5px",
    border: "1px solid #ddd",
    fontSize: "13px",
    boxSizing: "border-box",
    backgroundColor: "#fff"
};

const submitBtnStyle = {
    width: "100%",
    padding: "9px",
    backgroundColor: "#4CAF50",
    color: "#fff",
    border: "none",
    borderRadius: "5px",
    fontSize: "14px",
    fontWeight: "600",
    cursor: "pointer",
    marginBottom: "8px"
};

const cancelBtnStyle = {
    width: "100%",
    padding: "9px",
    backgroundColor: "#6c757d",
    color: "#fff",
    border: "none",
    borderRadius: "5px",
    fontSize: "14px",
    cursor: "pointer"
};

const errorStyle = {
    color: "#d9534f",
    marginBottom: "8px",
    textAlign: "center",
    fontSize: "13px"
};