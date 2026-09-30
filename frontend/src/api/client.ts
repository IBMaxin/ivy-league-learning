// API layer only. No UI here.
const BASE: string = import.meta.env.VITE_API_BASE ?? "http://localhost:8000";
const TOKEN_KEY = "ivy-token";
const USER_KEY = "ivy-user";

export const USER_RE = /^[A-Za-z0-9_-]{1,64}$/;

export function getToken(): string | null {
  try {
    return localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
}

export function getUser(): string | null {
  try {
    return localStorage.getItem(USER_KEY);
  } catch {
    return null;
  }
}

export function isLoggedIn(): boolean {
  return getToken() !== null && getUser() !== null;
}

function setUser(user_id: string): void {
  try {
    localStorage.setItem(USER_KEY, user_id);
  } catch {
    /* storage unavailable */
  }
}

export function setToken(token: string): void {
  try {
    localStorage.setItem(TOKEN_KEY, token);
  } catch {
    /* storage unavailable — requests go unauthenticated */
  }
}

export function clearAuth(): void {
  try {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  } catch {
    /* ignore */
  }
}

function clearTokenKeepUser(): void {
  try {
    localStorage.removeItem(TOKEN_KEY);
  } catch {
    /* ignore */
  }
}

export function reqId(): string {
  return crypto.randomUUID();
}

export function authErrorMessage(e: unknown): string {
  if (e instanceof Error) {
    if (e.message.includes("401") || e.message.includes("Login required"))
      return "Login required — sign in above.";
    if (e.message.includes("403")) return "Forbidden — that data belongs to another user.";
    return e.message;
  }
  return "Request failed.";
}

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const token = getToken();
  const res = await fetch(`${BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      "X-Request-ID": reqId(),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(init?.headers ?? {}),
    },
  });
  if (!res.ok) throw new Error(`Request failed: ${res.status}`);
  return (await res.json()) as T;
}

async function authed<T>(path: string, init?: RequestInit): Promise<T> {
  if (!getToken() || !getUser()) throw new Error("Login required (401)");
  try {
    return await req<T>(path, init);
  } catch (e) {
    if (e instanceof Error && e.message.includes("401")) clearTokenKeepUser();
    throw e;
  }
}

function requireUser(): string {
  const u = getUser();
  if (!u || !getToken()) throw new Error("Login required (401)");
  return u;
}

export async function login(user_id: string): Promise<string> {
  const id = user_id.trim();
  if (!USER_RE.test(id)) throw new Error("Invalid user id — use 1-64 chars: A-Z a-z 0-9 _ -");
  const res = await fetch(`${BASE}/api/auth/token`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-Request-ID": reqId() },
    body: JSON.stringify({ user_id: id }),
  });
  if (!res.ok) throw new Error(`Login failed: ${res.status}`);
  const data = (await res.json()) as { access_token: string };
  setToken(data.access_token);
  setUser(id);
  return data.access_token;
}

export function logout(): void {
  clearAuth();
}

export const api = {
  login,
  logout,
  curriculum: () => req<{ tracks: Track[] }>("/api/curriculum"),
  library: (q = "") => req<{ items: LibItem[] }>(`/api/library?q=${encodeURIComponent(q)}`),
  quiz: (id: string) => req<{ questions: QuizQ[] }>(`/api/quiz/${id}`),
  submitQuiz: (lesson_id: string, answers: number[]) => {
    const user_id = requireUser();
    return authed<{ score: number; recommendation: Rec }>(`/api/quiz/submit`, {
      method: "POST",
      body: JSON.stringify({ user_id, lesson_id, answers }),
    });
  },
  getLab: (id: string) =>
    authed<{ lesson_id: string; prompt: string; test_cases: LabTest[] }>(
      `/api/lab/${encodeURIComponent(id)}`,
    ),
  submitLab: (payload: { lesson_id: string; code: string }) => {
    return authed<{ success: boolean; results: LabResult[] }>(`/api/lab/submit`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },
  recommend: () => {
    const user_id = requireUser();
    return authed<{ recommendation: Rec; completed: string[] }>(
      `/api/adaptive/recommend/${encodeURIComponent(user_id)}`,
    );
  },
  progress: () => {
    const user_id = requireUser();
    return authed<Progress[]>(`/api/progress/${encodeURIComponent(user_id)}`);
  },
  saveProgress: (p: ProgressInput) => {
    const user_id = requireUser();
    return authed(`/api/progress`, { method: "POST", body: JSON.stringify({ ...p, user_id }) });
  },
  health: () => req<{ status: string }>(`/health`),
  runCode: (language: string, code: string) =>
    authed<{ output: string }>(`/api/code/run`, {
      method: "POST",
      body: JSON.stringify({ language, code }),
    }),
  posts: (track = "") => {
    const q = track ? `?track=${encodeURIComponent(track)}` : "";
    return req<{ posts: Post[] }>(`/api/community/posts${q}`);
  },
  addPost: (p: PostInput) => {
    const author = requireUser();
    return authed<Post>(`/api/community/posts`, {
      method: "POST",
      body: JSON.stringify({ ...p, author }),
    });
  },
};

export interface Track {
  id: string;
  title: string;
  lessons: { id: string; title: string; language: string }[];
}
export interface LibItem {
  id: string;
  title: string;
  university: string;
  url: string;
}
export interface QuizQ {
  q: string;
  choices: string[];
}
export interface Rec {
  mode: string;
  lesson_id: string | null;
  reason: string;
}
export interface Progress {
  user_id: string;
  course_id: string;
  lesson_id: string;
  completed: boolean;
  score?: number | null;
}
export type ProgressInput = Omit<Progress, "user_id">;
export interface Post {
  id: string;
  author: string;
  title: string;
  body: string;
  track: string;
}
export type PostInput = Omit<Post, "id" | "author">;
export interface LabTest {
  input: string;
  expected: any;
}
export interface LabResult {
  input: string;
  expected: any;
  actual?: any;
  passed: boolean;
  error?: string;
}
