import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import API from "../services/api";
import { SERVICES } from "../constants/services";

const AdminPage = () => {
    const [counters, setCounters] = useState([]);
    const [name, setName] = useState("");
    const [serviceType, setServiceType] = useState("Passport");
    const [error, setError] = useState("");
    const [username, setUsername] = useState("");
    const navigate = useNavigate();

    useEffect(() => {
        if (localStorage.getItem("role") !== "admin") {
            navigate("/login");
            return;
        }

        const storedName = localStorage.getItem("username");
        if (storedName) setUsername(storedName);

        loadCounters();
    }, [navigate]);

    const loadCounters = async () => {
        try {
            const res = await API.get("/counter/all");
            setCounters(res.data);
        } catch (err) {
            setError("Failed to load counters");
        }
    };

    const addCounter = async (e) => {
        e.preventDefault();
        try {
            await API.post("/counter/add", { name, service_type: serviceType });
            setName("");
            loadCounters();
        } catch (err) {
            setError("Failed to add counter");
        }
    };

    const deleteCounter = async (id) => {
        try {
            await API.delete(`/counter/delete/${id}`);
            loadCounters();
        } catch (err) {
            setError("Failed to delete counter");
        }
    };

    return (
        <div>
            <h2>Admin Dashboard{username ? ` - Hello, ${username}` : ""}</h2>
            {error && <p className="text-error">{error}</p>}

            <div className="token-info-box margin-top-1-5">
                <h3>Add New Counter</h3>
                <form onSubmit={addCounter} className="admin-form">
                    <input type="text" placeholder="Counter Name (e.g. C1)" value={name} onChange={(e) => setName(e.target.value)} required />
                    <select value={serviceType} onChange={(e) => setServiceType(e.target.value)} className="admin-select">
                        {SERVICES.map(s => (
                            <option key={s} value={s}>{s}</option>
                        ))}
                    </select>
                    <button type="submit">Add Counter</button>
                </form>
            </div>

            <table className="admin-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Service Type</th>
                        <th>Status</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
                    {counters.map(counter => (
                        <tr key={counter.id}>
                            <td>{counter.id}</td>
                            <td>{counter.name}</td>
                            <td>{counter.service_type}</td>
                            <td>{counter.status}</td>
                            <td>
                                <button onClick={() => deleteCounter(counter.id)} className="btn-danger">Delete</button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default AdminPage;
