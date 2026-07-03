import { useState } from "react";
import API from "../services/api";
import { SERVICES } from "../constants/services";

const ServiceSelector = ({ setTokenData }) => {
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState("")

    const selectService = async (service) => {
        setLoading(true)
        setError("")
        try {
            const response = await API.post("/queue/new", { service_type: service })
            setTokenData(response.data)
        } catch (err) {
            const message = err.response?.data?.error || "Failed to generate token. Please try again."
            setError(message)
        }
        setLoading(false)
    }

    return (
        <div>
            <h3>Select Services</h3>
            <div className="service-btn-container">
                {SERVICES.map((service) => (
                    <button key={service} onClick={() => selectService(service)} disabled={loading}>
                        {service}
                    </button>
                ))}
            </div>
            {loading && <p className="text-info">Generating intelligent token...</p>}
            {error && <p className="text-error">{error}</p>}
        </div>
    )
}

export default ServiceSelector