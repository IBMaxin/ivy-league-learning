// API layer only. No UI here.
const BASE: string = import.meta.env.VITE_API_BASE ?? "http://localhost:8000";
const TOKEN_KEY = "ivy-token";
const DEFAULT_USER = "dev-user";

export function getToken(): string | null {
  try {
    return localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
}

export function setToken(token: string): void {
  try {
    localStorage.setItem(TOKEN_KEY, token);
  } catch {
    /* storage unavailable — requests go unauthenticated */
  }
}

export function reqId(): string {
  return crypto.randomUUID();
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
  if (!getToken()) await login(DEFAULT_USER);
  try {
    return await req<T>(path, init);
  } catch (e) {
    // Token may be expired — mint once more and retry.
    if (e instanceof Error && e.message.includes("401")) {
      await login(DEFAULT_USER);
      return await req<T>(path, init);
    }
    throw e;
  }
}

export async function login(user_id: string = DEFAULT_USER): Promise<string> {
  const res = await fetch(`${BASE}/api/auth/token`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-Request-ID": reqId() },
    body: JSON.stringify({ user_id }),
  });
  if (!res.ok) throw new Error(`Login failed: ${res.status}`);
  const data = (await res.json()) as { access_token: string };
  setToken(data.access_token);
  return data.access_token;
}

export const api = {
  login,
  curriculum: () => req<{ tracks: Track[] }>("/api/curriculum"),
  library: (q = "") => req<{ items: LibItem[] }>(`/api/library?q=${encodeURIComponent(q)}`),
  quiz: (id: string) => req<{ questions: QuizQ[] }>(`/api/quiz/${id}`),
  submitQuiz: (user_id: string, lesson_id: string, answers: number[]) =>
    authed<{ score: number; recommendation: Rec }>(`/api/quiz/submit`, {
      method: "POST",
      body: JSON.stringify({ user_id, lesson_id, answers }),
    }),
  recommend: (user_id: string) =>
    authed<{ recommendation: Rec; completed: string[] }>(`/api/adaptive/recommend/${user_id}`),
  progress: (user_id: string) => authed<Progress[]>(`/api/progress/${user_id}`),
  saveProgress: (p: Progress) =>
    authed(`/api/progress`, { method: "POST", body: JSON.stringify(p) }),
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
  addPost: (p: Omit<Post, "id">) =>
    authed<Post>(`/api/community/posts`, { method: "POST", body: JSON.stringify(p) }),
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
export interface Post {
  id: string;
  author: string;
  title: string;
  body: string;
  track: string;
}
