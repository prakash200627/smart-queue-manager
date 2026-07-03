import { useState } from "react";
import API from "../services/api";

const ChatBot = ({ setTokenData }) => {
    const [message, setMessage] = useState("")
    const [response, setResponse] = useState("")

    const sendMessage = async () => {
        if (!message.trim()) return

        setResponse("Analyzing with AI...")
        try {
            const aiRes = await API.post("/queue/ai-detect", { message: message })
            const service = aiRes.data.service

            if (!service) {
                setResponse("Sorry, I could not detect the service. Please try describing it differently.")
                return
            }

            setResponse(`Detected service: ${service}. Generating token...`)

            const res = await API.post("/queue/new", { service_type: service })

            if (res.data.error) {
                setResponse(`Error: ${res.data.error}`)
            } else {
                setTokenData(res.data)
                setResponse(`Token generated for ${service}!`)
            }
        } catch (err) {
            const errorMsg = err.response?.data?.error || "Something went wrong. Please try again."
            setResponse(`Error: ${errorMsg}`)
        }
    }

    return (
        <div>
            <h3>AI Assistant</h3>
            <div className="chatbot-container">
                <input
                    type="text"
                    placeholder="Describe your problem..."
                    value={message}
                    onChange={e => setMessage(e.target.value)}
                    onKeyDown={e => e.key === "Enter" && sendMessage()}
                />
                <button onClick={sendMessage}>Ask AI</button>
            </div>
            {response && <p className="text-info" style={{ marginTop: "0" }}>{response}</p>}
        </div>
    )
}

export default ChatBot