import { BrowserRouter, Routes, Route, Link, useNavigate } from "react-router-dom"
import PersonPage from "./pages/PersonPage"
import OperatorPage from "./pages/OperatorPage"
import AdminPage from "./pages/AdminPage"
import LoginPage from "./pages/LoginPage"
import RegisterPage from "./pages/RegisterPage"
import DisplayBoard from "./components/DisplayBoard"

import "./App.css"

const NavBar = () => {
  const navigate = useNavigate();
  const token = localStorage.getItem("token");
  const role = localStorage.getItem("role");

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("role");
    localStorage.removeItem("username");
    navigate("/login");
  };

  return (
    <nav className="app-nav">
      <div className="nav-links">
        {(!role || role === "customer") && <Link to="/" className="nav-link" style={{ fontWeight: "bold" }}>Customer</Link>}
        <Link to="/display" className="nav-link">Board</Link>
        {role === "admin" && <Link to="/admin" className="nav-link">Admin</Link>}
        {role === "operator" && <Link to="/operator" className="nav-link">Operator</Link>}
      </div>
      <div>
        {token ? (
          <button onClick={handleLogout} className="btn-logout">Logout</button>
        ) : (
          <Link to="/login" className="nav-link">Login</Link>
        )}
      </div>
    </nav>
  );
};

const App = () => {
  return (
    <BrowserRouter>
      <div className="app-container">
        <header className="app-header">
          <h1>Smart Queue System</h1>
          <p className="subtitle">AI-Powered Token Management</p>
        </header>

        <NavBar />

        <main className="app-main">
          <Routes>
            <Route path="/" element={
              <section className="dashboard-card person-dashboard">
                <PersonPage />
              </section>
            } />

            <Route path="/operator" element={
              <section className="dashboard-card operator-dashboard">
                <OperatorPage />
              </section>
            } />

            <Route path="/admin" element={
              <section className="dashboard-card operator-dashboard">
                <AdminPage />
              </section>
            } />

            <Route path="/login" element={
              <LoginPage />
            } />

            <Route path="/register" element={
              <RegisterPage />
            } />

            <Route path="/display" element={
              <section className="dashboard-card display-board-container">
                <DisplayBoard />
              </section>
            } />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}

export default App