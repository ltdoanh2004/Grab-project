export interface RegisterPayload {
  email: string;
  first_name: string;
  last_name: string;
  password: string;
  username: string;
}

export interface LoginPayload {
  username: string;
  password: string;
}

export interface AuthResponse {
  message: string;
  data: {
    access_token: string;
    refresh_token: string;
  };
}
