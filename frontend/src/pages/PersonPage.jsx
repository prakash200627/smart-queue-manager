import { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import ServiceSelector from "../components/ServiceSelector"
import TokenDisplay from "../components/TokenDisplay"
import ChatBot from "../components/ChatBot"

const PersonPage = () => {
    const [tokenData, setTokenData] = useState(null)
    const [username, setUsername] = useState("")

    const navigate = useNavigate()

    useEffect(() => {
        const role = localStorage.getItem("role")
        if (role === "admin") {
            navigate("/admin")
            return
        } else if (role === "operator") {
            navigate("/operator")
            return
        }

        const storedName = localStorage.getItem("username")
        if (storedName) setUsername(storedName)
    }, [navigate])

    return (
        <div>
            <h2>Welcome{username ? `, ${username}` : ""}</h2>
            <ServiceSelector setTokenData={setTokenData} />
            <ChatBot setTokenData={setTokenData} />
            <TokenDisplay tokenData={tokenData} />
        </div>
    )
}

export default PersonPage