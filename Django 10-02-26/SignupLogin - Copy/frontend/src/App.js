import React from "react";
import {BrowserRouter, Routes, Route} from 'react-router-dom'
// import LoginSignup from "./LoginSignup";
import LoginSignup from "./components/LoginSignup";
import './components/LoginSignup.css'
import Dashboard from "./components/Dashboard";

function App() {
  return (
    <>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LoginSignup />} />
        <Route path="/dashboard" element={<Dashboard />} /> 
      </Routes>
    </BrowserRouter>
    </>
  );
}

export default App;
