// Vite proxy sayesinde /api → http://localhost:8000/api
const BASE_URL = import.meta.env.VITE_API_URL ?? "/api";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail ?? "Sunucu hatası");
  }
  return res.json();
}

export const api = {
  register: (name: string, frames: string[]) =>
    request<{ success: boolean; message: string }>("/register", {
      method: "POST",
      body: JSON.stringify({ name, frames }),
    }),

  login: (frames: string[]) =>
    request<{ success: boolean; user?: string; message: string }>("/login", {
      method: "POST",
      body: JSON.stringify({ frames }),
    }),

  checkLiveness: (frames: Array<{ frame: string; timestamp_ms: number }>) =>
    request<{ is_live: boolean; message: string }>("/liveness", {
      method: "POST",
      body: JSON.stringify({ frames }),
    }),

  listUsers: () =>
    request<{ users: string[] }>("/users"),

  deleteUser: (name: string) =>
    request<{ success: boolean; message: string }>(`/users/${name}`, {
      method: "DELETE",
    }),
};
