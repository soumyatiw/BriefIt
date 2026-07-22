import axios from "axios";

const client = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? "/api",
});

// Attach the JWT from localStorage on every request
client.interceptors.request.use((config) => {
  const token = localStorage.getItem("briefit_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// If a request comes back 401, the token is invalid/expired — clear it and bounce to login
client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("briefit_token");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export default client;
