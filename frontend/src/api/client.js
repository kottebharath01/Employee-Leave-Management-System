import axios from "axios";

let rawBase = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api").trim().replace(/\/+$/, "");
if (!rawBase.endsWith("/api")) {
  rawBase += "/api";
}

const api = axios.create({ baseURL: rawBase });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem("access_token");
      if (window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

export default api;

export function getErrorMessage(error) {
  if (error.response && error.response.data && error.response.data.detail) {
    const detail = error.response.data.detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail)) {
      return detail.map((d) => d.msg || JSON.stringify(d)).join("; ");
    }
    return JSON.stringify(detail);
  }
  return "Something went wrong. Please try again.";
}
