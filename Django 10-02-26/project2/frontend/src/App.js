import React from "react";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import Login from "./login";
import Signup from "./Signup";
import Home from "./Home";
import PrivateRoute from "./PrivateRoute";

function App() {
  return (
    <Router>
      <h1>Auth System</h1>

      <Link to="/login">Login</Link> | 
      <Link to="/signup">Signup</Link>

      <Routes>

        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />

        {/* Protected Dashboard */}
        <Route
          path="/home"
          element={
            <PrivateRoute>
              <Home />
            </PrivateRoute>
          }
        />

      </Routes>
    </Router>
  );
}

export default App;
