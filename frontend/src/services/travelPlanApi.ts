import axios from "axios";
import { AuthResponse, LoginPayload, RegisterPayload } from "../types/apiType";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8081/api/v1";

export async function register(
  payload: RegisterPayload
): Promise<AuthResponse> {
  const res = await axios.post<AuthResponse>(
    `${API_BASE_URL}/auth/register`,
    payload
  );
  return res.data;
}

export async function login(payload: LoginPayload): Promise<AuthResponse> {
  const res = await axios.post<AuthResponse>(
    `${API_BASE_URL}/auth/login`,
    payload
  );
  return res.data;
}
