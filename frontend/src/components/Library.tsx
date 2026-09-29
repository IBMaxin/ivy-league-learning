import { useEffect, useState } from "react";
import { api, type LibItem, type Post } from "../api/client";

const TRACKS = ["general", "cs-fundamentals", "fullstack", "maths", "humanities"];

export function Library() {
  const [q, setQ] = useState("");
  const [items, setItems] = useState<LibItem[]>([]);
  const [state, setState] = useState<"loading" | "ready" | "offline">("loading");
  useEffect(() => {
    const t = setTimeout(() => {
      api
        .library(q)
        .then((d) => {
          setItems(d.items);
          setState("ready");
        })
        .catch(() => setState("offline"));
    }, 250);
    return () => clearTimeout(t);
  }, [q]);
  return (
    <section>
      <h2>Content Library</h2>
      <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search open courses" />
      {state === "loading" && <p>Loading…</p>}
      {state === "offline" && <p>Backend offline — check VITE_API_BASE.</p>}
      {state === "ready" && items.length === 0 && <p>No matches.</p>}
      <ul>
        {items.map((i) => (
          <li key={i.id}>
            <a href={i.url} target="_blank" rel="noreferrer">{i.title}</a> — {i.university}
          </li>
        ))}
      </ul>
    </section>
  );
}

export function Community() {
  const [posts, setPosts] = useState<Post[]>([]);
  const [track, setTrack] = useState("");
  const [title, setTitle] = useState("");
  const [msg, setMsg] = useState("");

  useEffect(() => {
    api
      .posts(track)
      .then((d) => {
        setPosts(d.posts);
        setMsg("");
      })
      .catch(() => setMsg("Backend offline — showing nothing."));
  }, [track]);

  async function add() {
    if (!title.trim()) {
      setMsg("Write a question first.");
      return;
    }
    try {
      const p = await api.addPost({
        author: "learner",
        title: title.trim(),
        body: title.trim(),
        track: track || "general",
      });
      setPosts((s) => [...s, p]);
      setTitle("");
      setMsg("Posted.");
    } catch {
      setMsg("Post failed — backend offline?");
    }
  }

  return (
    <section>
      <h2>Community</h2>
      <label>
        Track{" "}
        <select value={track} onChange={(e) => setTrack(e.target.value)}>
          <option value="">All</option>
          {TRACKS.map((t) => (
            <option key={t} value={t}>{t}</option>
          ))}
        </select>
      </label>
      <div>
        <input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Ask a question" />
        <button onClick={() => void add()}>Post</button>
      </div>
      <p aria-live="polite">{msg}</p>
      <ul>
        {posts.map((p) => (
          <li key={p.id}><strong>{p.title}</strong> — {p.author} <small>[{p.track}]</small></li>
        ))}
      </ul>
    </section>
  );
}

export function Studio() {
  const [html, setHtml] = useState("<h1>Hello Ivy</h1>");
  const [apiOut, setApiOut] = useState("");
  const [code, setCode] = useState('print("hello ivy")');

  async function ping() {
    try {
      const [h, c] = await Promise.all([
        api.health(),
        api.curriculum(),
      ]);
      setApiOut(`health=${h.status} tracks=${c.tracks.length}`);
    } catch {
      setApiOut("Backend offline — check VITE_API_BASE.");
    }
  }

  async function sendCode() {
    try {
      const r = await api.runCode("python", code);
      setApiOut(r.output);
    } catch {
      setApiOut("Code run failed — backend offline?");
    }
  }

  return (
    <section>
      <h2>Full-Stack Studio</h2>
      <h3>Frontend preview</h3>
      <textarea value={html} onChange={(e) => setHtml(e.target.value)} rows={4} cols={60} />
      <iframe title="preview" srcDoc={html} sandbox="" width="100%" height={120} />
      <h3>Backend tester</h3>
      <button onClick={() => void ping()}>Ping API</button>
      <div>
        <textarea value={code} onChange={(e) => setCode(e.target.value)} rows={3} cols={60} />
        <br />
        <button onClick={() => void sendCode()}>Send to /api/code/run</button>
      </div>
      <pre aria-live="polite">{apiOut}</pre>
    </section>
  );
}
