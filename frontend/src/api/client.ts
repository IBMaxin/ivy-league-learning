// API layer only. No UI here.
const BASE: string = import.meta.env.VITE_API_BASE ?? "http://localhost:8000";
const TOKEN = "dev-token";

export function reqId(): string {
  return crypto.randomUUID();
}

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      "X-Request-ID": reqId(),
      Authorization: `Bearer ${TOKEN}`,
      ...(init?.headers ?? {}),
    },
  });
  if (!res.ok) throw new Error(`Request failed: ${res.status}`);
  return (await res.json()) as T;
}

export const api = {
  curriculum: () => req<{ tracks: Track[] }>("/api/curriculum"),
  library: (q = "") => req<{ items: LibItem[] }>(`/api/library?q=${encodeURIComponent(q)}`),
  quiz: (id: string) => req<{ questions: QuizQ[] }>(`/api/quiz/${id}`),
  submitQuiz: (user_id: string, lesson_id: string, answers: number[]) =>
    req<{ score: number; recommendation: Rec }>(`/api/quiz/submit`, {
      method: "POST",
      body: JSON.stringify({ user_id, lesson_id, answers }),
    }),
  recommend: (user_id: string) =>
    req<{ recommendation: Rec; completed: string[] }>(`/api/adaptive/recommend/${user_id}`),
  progress: (user_id: string) => req<Progress[]>(`/api/progress/${user_id}`),
  saveProgress: (p: Progress) =>
    req(`/api/progress`, { method: "POST", body: JSON.stringify(p) }),
  health: () => req<{ status: string }>(`/health`),
  runCode: (language: string, code: string) =>
    req<{ output: string }>(`/api/code/run`, {
      method: "POST",
      body: JSON.stringify({ language, code }),
    }),
  posts: (track = "") => {
    const q = track ? `?track=${encodeURIComponent(track)}` : "";
    return req<{ posts: Post[] }>(`/api/community/posts${q}`);
  },
  addPost: (p: Omit<Post, "id">) =>
    req<Post>(`/api/community/posts`, { method: "POST", body: JSON.stringify(p) }),
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
