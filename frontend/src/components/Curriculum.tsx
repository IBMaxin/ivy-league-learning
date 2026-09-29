import { useState } from "react";
import { useCurriculum } from "../hooks/useCurriculum";
import { api, authErrorMessage, getUser } from "../api/client";

export default function Curriculum() {
  const { tracks, error } = useCurriculum();
  const [msg, setMsg] = useState("");
  async function complete(course_id: string, lesson_id: string) {
    if (!getUser()) {
      setMsg("Login required — sign in above.");
      return;
    }
    try {
      await api.saveProgress({ course_id, lesson_id, completed: true });
      setMsg(`Saved ${lesson_id}`);
    } catch (e) {
      setMsg(authErrorMessage(e));
    }
  }
  return (
    <section>
      <h2>Curriculum</h2>
      {error && <p>{error} (VITE_API_BASE?)</p>}
      {tracks.map((t) => (
        <article key={t.id}>
          <h3>{t.title}</h3>
          <ul>
            {t.lessons.map((l) => (
              <li key={l.id}>
                {l.title} <small>({l.language})</small>{" "}
                <button onClick={() => void complete(t.id, l.id)}>Mark done</button>
              </li>
            ))}
          </ul>
        </article>
      ))}
      <p aria-live="polite">{msg}</p>
    </section>
  );
}
