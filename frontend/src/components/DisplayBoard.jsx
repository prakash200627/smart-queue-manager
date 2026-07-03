import { useEffect, useState } from "react";
import API from "../services/api";
import socket from "../services/socket";

const DisplayBoard = () => {
    const [counters, setCounters] = useState([])
    const loadCounters = async () => {
        try {
            const res = await API.get(`/queue/board/live?_t=${Date.now()}`)
            setCounters(res.data)
        } catch (error) {
            console.log("Error loading counters:", error)
        }
    }

    useEffect(() => {
        loadCounters()

        const updateListener = () => {
            loadCounters()
        }

        socket.on("queue_update", updateListener)

        return () => {
            socket.off("queue_update", updateListener)
        }
    }, [])

    return (
        <div>
            <h2>Live Queue Display</h2>
            <table className="admin-table">
                <thead>
                    <tr>
                        <th>Counter</th>
                        <th>Service</th>
                        <th>Status</th>
                        <th>Now Serving</th>
                        <th>Live Waitlist Queue</th>
                    </tr>
                </thead>
                <tbody>
                    {counters.length === 0 && (
                        <tr>
                            <td colSpan="5" className="waitlist-empty">No counters available</td>
                        </tr>
                    )}
                    {counters.map((counter) => (
                        <tr key={counter.id}>
                            <td>{counter.name}</td>
                            <td>{counter.service_type}</td>
                            <td>{counter.status || "-"}</td>
                            <td>{counter.current_token ? counter.current_token : "-"}</td>
                            <td>
                                {counter.waiters && counter.waiters.length > 0 ? (
                                    <div className="waitlist-tokens">
                                        {counter.waiters.map(t => (
                                            <span key={t.id} className="waitlist-badge waitlist-badge--sm">{t.token_number}</span>
                                        ))}
                                    </div>
                                ) : (
                                    <span className="waitlist-empty">Empty</span>
                                )}
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    )
}

export default DisplayBoard