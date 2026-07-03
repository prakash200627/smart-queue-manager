import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import API from "../services/api";

const RegisterPage = () => {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [role, setRole] = useState("customer");
    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");
    const navigate = useNavigate();

    const handleRegister = async (e) => {
        e.preventDefault();
        try {
            await API.post("/auth/register", { username, password, role });
            setSuccess("Registration successful! Redirecting to login...");
            setError("");
            setTimeout(() => navigate("/login"), 2000);
        } catch (err) {
            setError(err.response?.data?.error || "Registration failed");
            setSuccess("");
        }
    };

    return (
        <div className="login-container token-info-box auth-box">
            <h2>Register for Smart Queue</h2>
            <form onSubmit={handleRegister} className="auth-form">
                <input
                    type="text"
                    placeholder="Username"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    required
                />
                <input
                    type="password"
                    placeholder="Password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                />
                <select
                    value={role}
                    onChange={(e) => setRole(e.target.value)}
                    className="admin-select"
                >
                    <option value="customer">Customer</option>
                    <option value="operator">Operator</option>
                    <option value="admin">Admin</option>
                </select>
                {error && <p className="text-error">{error}</p>}
                {success && <p className="text-success">{success}</p>}
                <button type="submit">Register</button>
            </form>
            <p className="auth-footer">
                Already have an account? <Link to="/login" className="auth-link">Login here</Link>
            </p>
        </div>
    );
};

export default RegisterPage;
