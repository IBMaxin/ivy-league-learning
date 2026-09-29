import { useState } from "react";
import { USER_RE } from "../api/client";
import { useAuth } from "../hooks/useAuth";

export default function Login() {
  const { user, loggedIn, login, logout } = useAuth();
  const [input, setInput] = useState("");
  const [msg, setMsg] = useState("");

  async function doLogin() {
    const id = input.trim();
    if (!USER_RE.test(id)) {
      setMsg("Use 1-64 chars: A-Z a-z 0-9 _ -");
      return;
    }
    try {
      await login(id);
      setInput("");
      setMsg(`Signed in as ${id}.`);
    } catch {
      setMsg("Login failed — backend offline?");
    }
  }

  if (loggedIn && user) {
    return (
      <section aria-label="login" style={{ border: "1px solid #ccc", padding: 8, marginBottom: 12 }}>
        <span>
          Signed in as <strong>{user}</strong>
        </span>{" "}
        <button onClick={logout}>Log out</button>
        {msg && <span aria-live="polite"> — {msg}</span>}
      </section>
    );
  }

  return (
    <section aria-label="login" style={{ border: "1px solid #ccc", padding: 8, marginBottom: 12 }}>
      <label>
        User ID{" "}
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="e.g. learner-1"
          maxLength={64}
          onKeyDown={(e) => {
            if (e.key === "Enter") void doLogin();
          }}
        />
      </label>{" "}
      <button onClick={() => void doLogin()}>Log in</button>
      <p aria-live="polite" style={{ margin: "4px 0 0" }}>
        {msg || "Login mints a short-lived JWT — progress and quizzes are per-user."}
      </p>
    </section>
  );
}
