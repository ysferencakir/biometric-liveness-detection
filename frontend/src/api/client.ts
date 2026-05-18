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

export interface ModuleResult {
  module_name: string;
  passed: boolean;
  score: number;
  details: Record<string, unknown>;
}

export interface AuthenticateResponse {
  granted: boolean;
  reason: string;
  user?: string;
  recognition_score?: number;
  liveness: ModuleResult[];
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

  /**
   * Tam kimlik doğrulama:
   * - username: kullanıcı adı / öğrenci numarası (null = tüm DB'ye karşı ara)
   * - frames: yüz görüntüsü frame'leri (base64)
   * - livenessVerified: true → challenge adımı zaten geçildi, liveness tekrar çalışmaz
   */
  authenticate: (
    username: string | null,
    frames: string[],
    livenessVerified = false
  ) =>
    request<AuthenticateResponse>("/authenticate", {
      method: "POST",
      body: JSON.stringify({
        username,
        frames,
        liveness_verified: livenessVerified,
      }),
    }),

  checkLiveness: (frames: Array<{ frame: string; timestamp_ms: number }>) =>
    request<{ is_live: boolean; message: string; modules: ModuleResult[] }>("/liveness", {
      method: "POST",
      body: JSON.stringify({ frames }),
    }),

  checkChallenge: (
    challenge: string,
    frames: Array<{ frame: string; timestamp_ms: number }>
  ) =>
    request<{
      challenge: string;
      passed: boolean;
      score: number;
      message: string;
      details: Record<string, unknown>;
    }>("/liveness/challenge", {
      method: "POST",
      body: JSON.stringify({ challenge, frames }),
    }),

  /**
   * Tek frame'i analiz eder — test laboratuvarı için.
   * EAR, MAR, head pose, landmark koordinatları döner.
   */
  diagnose: (frame: string) =>
    request<{
      face_detected: boolean;
      landmarks: [number, number][];
      ear: number;
      mar: number;
      head_yaw: number;
      head_pitch: number;
      eye_dist: number;
      iris: {
        left: [number, number];
        right: [number, number];
        left_center: [number, number];
        right_center: [number, number];
      };
      key_points: {
        left_ear: [number, number][];
        right_ear: [number, number][];
        mouth: [number, number][];
      };
      thresholds: { ear: number; mar: number; head: number };
      error?: string;
    }>("/diagnose", {
      method: "POST",
      body: JSON.stringify({ frame }),
    }),

  listUsers: () =>
    request<{ users: string[] }>("/users"),

  deleteUser: (name: string) =>
    request<{ success: boolean; message: string }>(`/users/${name}`, {
      method: "DELETE",
    }),
};
