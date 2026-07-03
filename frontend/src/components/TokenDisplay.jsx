const TokenDisplay = ({ tokenData }) => {
    if (!tokenData) return null

    return (
        <div className="token-info-box">
            <h2>Your Token</h2>
            <p><strong>Token Number:</strong> <span className="text-token-medium">{tokenData.token}</span></p>
            <p><strong>Counter:</strong> {tokenData.counter}</p>
            <p><strong>Estimated Waiting Time:</strong> {tokenData.waiting_time}</p>
        </div>
    )
}

export default TokenDisplay