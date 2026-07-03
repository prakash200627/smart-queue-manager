import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import API from "../services/api";

const LoginPage = () => {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const navigate = useNavigate();

    const handleLogin = async (e) => {
        e.preventDefault();
        try {
            const res = await API.post("/auth/login", { username, password });
            localStorage.setItem("token", res.data.access_token);
            localStorage.setItem("role", res.data.role);
            localStorage.setItem("username", res.data.username);

            if (res.data.role === "admin") navigate("/admin");
            else if (res.data.role === "operator") navigate("/operator");
            else navigate("/");
        } catch (err) {
            setError(err.response?.data?.error || "Login failed");
        }
    };

    return (
        <div className="login-container token-info-box auth-box">
            <h2>Login to Smart Queue</h2>
            <form onSubmit={handleLogin} className="auth-form">
                <input type="text" placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)} required />
                <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} required />
                {error && <p className="text-error">{error}</p>}
                <button type="submit">Login</button>
            </form>
            <p className="auth-footer">
                Don't have an account? <Link to="/register" className="auth-link">Register here</Link>
            </p>
        </div>
    );
};

export default LoginPage;
