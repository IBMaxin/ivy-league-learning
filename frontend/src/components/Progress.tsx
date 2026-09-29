import { useState } from "react";
import { api, authErrorMessage, getUser, type Progress, type Rec } from "../api/client";

export default function ProgressView() {
  const [items, setItems] = useState<Progress[] | null>(null);
  const [rec, setRec] = useState<Rec | null>(null);
  const [msg, setMsg] = useState("");

  async function load() {
    if (!getUser()) {
      setMsg("Login required — sign in above.");
      return;
    }
    setMsg("Loading…");
    try {
      const [p, r] = await Promise.all([api.progress(), api.recommend()]);
      setItems(p);
      setRec(r.recommendation);
      setMsg("");
    } catch (e) {
      setMsg(authErrorMessage(e));
    }
  }

  return (
    <section>
      <h2>My Progress</h2>
      <button onClick={() => void load()}>Refresh</button>
      {msg && <p aria-live="polite">{msg}</p>}
      {rec && (
        <p>
          Next: <strong>{rec.lesson_id ?? "all complete"}</strong> — {rec.reason}
        </p>
      )}
      {items && items.length === 0 && <p>No progress yet — mark a lesson done.</p>}
      {items && items.length > 0 && (
        <ul>
          {items.map((p, i) => (
            <li key={i}>
              {p.lesson_id} — {p.completed ? "done" : "open"}
              {p.score !== null && p.score !== undefined ? ` (${p.score}%)` : ""}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
