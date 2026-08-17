import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const client = axios.create({ baseURL: API_URL });

client.interceptors.request.use((config) => {
  const token = localStorage.getItem("asc_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

client.interceptors.response.use(
  (res) => res,
  (err) => Promise.reject(err)
);

export const API = {
  sendOtp: (email) => client.post("/auth/send-otp", { email }),
  verifyOtp: (email, otp) => client.post("/auth/verify-otp", { email, otp }),
  me: () => client.get("/me"),

  listTickets: (params) => client.get("/tickets", { params }),
  getTicket: (id) => client.get(`/tickets/${id}`),
  createTicket: (formData) =>
    client.post("/tickets", formData, { headers: { "Content-Type": "multipart/form-data" } }),
  updateTicket: (id, payload) => client.put(`/tickets/${id}`, payload),
  deleteTicket: (id) => client.delete(`/tickets/${id}`),
  analyzeTicket: (id) => client.post(`/tickets/${id}/analyze`),

  getChat: (id) => client.get(`/tickets/${id}/assistant`),
  askAssistant: (id, message) => client.post(`/tickets/${id}/assistant`, { message }),
  draftResolution: (id) => client.post(`/tickets/${id}/resolve`, null),
  saveResolution: (id, payload) => client.post(`/tickets/${id}/resolve`, payload),
  getResolution: (id) => client.get(`/tickets/${id}/resolution`),

  search: (q) => client.get("/search", { params: { q } }),

  listKB: (q) => client.get("/kb", { params: q ? { q } : {} }),
  getKB: (id) => client.get(`/kb/${id}`),
  createKB: (payload) => client.post("/kb", payload),
  updateKB: (id, payload) => client.put(`/kb/${id}`, payload),
  deleteKB: (id) => client.delete(`/kb/${id}`),

  analyticsOverview: () => client.get("/analytics/overview"),

  listUsers: () => client.get("/users"),
  createUser: (payload) => client.post("/users", payload),
  deleteUser: (id) => client.delete(`/users/${id}`),
};

export const UPLOADS_BASE = API_URL;

export default client;
