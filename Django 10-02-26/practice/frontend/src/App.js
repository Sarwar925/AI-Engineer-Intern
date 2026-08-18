import Signup from "./components/Signup";
import Login from "./components/Login";
import Dashboard from './components/Dashboard'
import { BrowserRouter, Routes, Route } from "react-router-dom";

function App() {

  return (

    <BrowserRouter>

      <Routes>
        <Route path="/" element={<Signup />} />
        <Route path='/dashboard' element={<Dashboard />} />
      </Routes>

    </BrowserRouter>

  )

}

export default App;