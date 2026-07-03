import axios from "axios"
import { API_URL } from "../constants/api"

const API = axios.create({
    baseURL: API_URL
})

API.interceptors.request.use((req) => {
    const token = localStorage.getItem("token")
    if (token) {
        req.headers.Authorization = `Bearer ${token}`
    }
    return req
});

export default API