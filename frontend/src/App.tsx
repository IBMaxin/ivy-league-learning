import { useState } from "react";
import Curriculum from "./components/Curriculum";
import CodingLab from "./components/CodingLab";
import Quiz from "./components/Quiz";
import Login from "./components/Login";
import { Community, Library, Studio } from "./components/Library";

type View = "curriculum" | "lab" | "quiz" | "library" | "studio" | "community";

export default function App(): JSX.Element {
  const [view, setView] = useState<View>("curriculum");
  return (
    <main style={{ fontFamily: "system-ui", maxWidth: 860, margin: "0 auto", padding: 16 }}>
      <h1>Ivy League Learning</h1>
      <Login />
      <nav style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
        {(["curriculum", "lab", "quiz", "library", "studio", "community"] as View[]).map((v) => (
          <button key={v} onClick={() => setView(v)} aria-pressed={view === v}>
            {v}
          </button>
        ))}
      </nav>
      {view === "curriculum" && <Curriculum />}
      {view === "lab" && <CodingLab />}
      {view === "quiz" && <Quiz />}
      {view === "library" && <Library />}
      {view === "studio" && <Studio />}
      {view === "community" && <Community />}
    </main>
  );
}
