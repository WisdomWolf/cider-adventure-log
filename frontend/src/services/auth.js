import axios from "../axios";

export async function fetchCurrentUser() {
  try {
    const response = await axios.get("/api/auth/me");
    return response.data;
  } catch (error) {
    if (error.response && error.response.status === 401) {
      return null;
    }
    throw error;
  }
}

export async function fetchAuthConfig() {
  const response = await axios.get("/api/auth/config");
  return response.data;
}

export async function login(email, password) {
  const response = await axios.post("/api/auth/login", { email, password });
  return response.data;
}

export async function logout() {
  await axios.post("/api/auth/logout");
}

export async function fetchUsers() {
  const response = await axios.get("/api/auth/users");
  return response.data;
}
