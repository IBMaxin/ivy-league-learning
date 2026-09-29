import { useState } from "react";
import { api } from "../api/client";

export default function Quiz() {
  const [lesson, setLesson] = useState("py-101");
  const [qs, setQs] = useState<{ q: string; choices: string[] }[]>([]);
  const [answers, setAnswers] = useState<number[]>([]);
  const [result, setResult] = useState("");

  async function load() {
    try {
      const d = await api.quiz(lesson);
      setQs(d.questions);
      setAnswers(d.questions.map(() => 0));
    } catch {
      setResult("Quiz load failed — backend offline?");
    }
  }
  async function submit() {
    try {
      const r = await api.submitQuiz("dev-user", lesson, answers);
      setResult(`Score ${r.score} — ${r.recommendation.reason}`);
    } catch {
      setResult("Submit failed.");
    }
  }
  return (
    <section>
      <h2>Quiz + Adaptive Path</h2>
      <select value={lesson} onChange={(e) => setLesson(e.target.value)}>
        <option value="py-101">Python Basics</option>
        <option value="js-101">JS Basics</option>
        <option value="rust-101">Rust Basics</option>
        <option value="api-101">FastAPI Intro</option>
        <option value="react-101">React + TS</option>
      </select>{" "}
      <button onClick={() => void load()}>Load quiz</button>
      {qs.map((q, i) => (
        <div key={i}>
          <p>{q.q}</p>
          {q.choices.map((c, j) => (
            <label key={j}>
              <input
                type="radio"
                name={`q${i}`}
                checked={answers[i] === j}
                onChange={() => setAnswers((a) => a.map((v, k) => (k === i ? j : v)))}
              />
              {c}
            </label>
          ))}
        </div>
      ))}
      {qs.length > 0 && <button onClick={() => void submit()}>Submit</button>}
      <p aria-live="polite">{result}</p>
    </section>
  );
}
