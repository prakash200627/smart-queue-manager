import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import API from "../services/api";
import socket from "../services/socket";

const OperatorPage = () => {
    const [counterId, setCounterId] = useState("")
    const [token, setToken] = useState(null)
    const [isServing, setIsServing] = useState(false)
    const [username, setUsername] = useState("")
    const [counters, setCounters] = useState([])
    const [waitingTokens, setWaitingTokens] = useState([])
    const isOptimistic = useRef(false);
    const navigate = useNavigate()

    const loadCounters = async () => {
        try {
            const res = await API.get("/counter/all?_t=" + Date.now());
            setCounters(res.data);
            setCounterId((prev) => {
                if (res.data.length === 0) return "";
                return res.data.some((c) => c.id == prev) ? prev : res.data[0].id;
            });
        } catch (error) {
            console.error("Failed to load counters");
        }
    };

    useEffect(() => {
        const role = localStorage.getItem("role");
        if (role !== "operator") {
            navigate("/login");
        }

        const storedName = localStorage.getItem("username");
        if (storedName) setUsername(storedName);

        loadCounters();

        const updateListener = () => {
            if (isOptimistic.current) return;

            loadCounters();
            if (counterId) {
                loadWaitingTokens(counterId);
            }
        };

        socket.on("queue_update", updateListener);

        return () => {
            socket.off("queue_update", updateListener);
        };
    }, [navigate, counterId]);

    const loadWaitingTokens = async (id) => {
        if (!id) return;
        try {
            const res = await API.get(`/queue/counter/${id}/tokens?_t=${Date.now()}`);
            setWaitingTokens(res.data);
        } catch (error) {
            console.error("Failed to load waiting tokens");
        }
    };

    useEffect(() => {
        setToken(null);
        setWaitingTokens([]);
        setIsServing(false);

        loadWaitingTokens(counterId);

        if (counterId) {
            const fetchCurrentToken = async () => {
                try {
                    const res = await API.get(`/queue/counter/${counterId}/next?_t=${Date.now()}`);
                    if (res.data.message) {
                        setToken(null);
                    } else {
                        setToken(res.data);
                        setIsServing(res.data.is_serving || false);
                    }
                } catch (error) {
                    console.error("Failed to fetch token on counter select");
                }
            };
            fetchCurrentToken();
        }
    }, [counterId]);

    const getNextToken = () => {
        isOptimistic.current = true;

        if (waitingTokens.length > 0) {
            const nextOpt = waitingTokens[0];
            setToken({ token_id: nextOpt.id, token_number: nextOpt.token_number });
            setIsServing(false);
            setWaitingTokens(prev => prev.slice(1));
        }

        API.get(`/queue/counter/${counterId}/next?_t=${Date.now()}`)
            .then((res) => {
                if (res.data.message) {
                    alert(res.data.message);
                    setToken(null);
                    setIsServing(false);
                } else {
                    setToken(res.data);
                    setIsServing(res.data.is_serving || false);
                }
            })
            .catch((error) => {
                console.error("Failed to get next token", error);
            })
            .finally(() => {
                setTimeout(() => { isOptimistic.current = false; }, 1000);
            });
    };
    const startService = () => {
        isOptimistic.current = true;
        setIsServing(true);
        API.post(`/queue/start/${token.token_id}`).catch((error) => {
            console.error(error);
            setIsServing(false);
        }).finally(() => {
            setTimeout(() => { isOptimistic.current = false; }, 1000);
        });
    };

    const finishService = () => {
        const targetId = token.token_id;
        isOptimistic.current = true;

        if (waitingTokens.length > 0) {
            const nextOpt = waitingTokens[0];
            setToken({ token_id: nextOpt.id, token_number: nextOpt.token_number });
            setIsServing(false);
            setWaitingTokens(prev => prev.slice(1));
        } else {
            setToken(null);
            setIsServing(false);
        }

        API.post(`/queue/finish/${targetId}`)
            .then(() => {
                return API.get(`/queue/counter/${counterId}/next?_t=${Date.now()}`);
            })
            .then((res) => {
                if (!res.data.message) {
                    setToken(res.data);
                    setIsServing(res.data.is_serving || false);
                } else {
                    setToken(null);
                    setIsServing(false);
                }
            })
            .catch((error) => {
                console.error("Failed to auto-fetch next token", error);
            })
            .finally(() => {
                setTimeout(() => { isOptimistic.current = false; }, 1000);
            });
    };

    return (
        <div>
            <h2>Operator Dashboard{username ? ` - Hello, ${username}` : ""}</h2>
            <div className="operator-controls">
                <select value={counterId} onChange={e => setCounterId(e.target.value)} className="admin-select" style={{ flex: 1 }}>
                    <option value="" disabled>Select a counter</option>
                    {counters.map(c => (
                        <option key={c.id} value={c.id}>{c.name} ({c.service_type})</option>
                    ))}
                </select>
                <button onClick={getNextToken} disabled={!counterId}>Get Next Token</button>
            </div>

            <div className="operator-waitlist">
                <h3 className="waitlist-heading">Live Waitlist for this Counter</h3>
                {waitingTokens.length > 0 ? (
                    <div className="waitlist-tokens">
                        {waitingTokens.map(t => (
                            <span key={t.id} className="waitlist-badge">{t.token_number}</span>
                        ))}
                    </div>
                ) : (
                    <p className="waitlist-empty">No tokens currently waiting.</p>
                )}
            </div>
            {token && (
                <div className="token-info-box operator">
                    <h3>{isServing ? "Serving" : "Next Token"}</h3>
                    <p className="text-token-large">{token.token_number}</p>
                    <div className="action-buttons">
                        {!isServing && <button onClick={startService}>Start Service</button>}
                        <button onClick={finishService}>Finish Service</button>
                    </div>
                </div>
            )}
        </div>
    )
}

export default OperatorPage